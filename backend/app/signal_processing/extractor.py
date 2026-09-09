import numpy as np
from scipy import signal
from scipy.stats import kurtosis, skew
from typing import Dict, Any, Tuple, List

class ParameterExtractor:
    """Rigorous signal parameter extraction separating measured vs derived metrics."""

    @staticmethod
    def extract_all(
        sig: np.ndarray,
        sample_rate: float,
        center_freq_offset: float = 0.0
    ) -> Dict[str, Any]:
        n_samples = len(sig)
        if n_samples < 16:
            raise ValueError("Signal chunk too short for parameter extraction.")
            
        is_complex = np.iscomplexobj(sig)
        dt = 1.0 / sample_rate
        duration = n_samples * dt
        
        # -------------------------------------------------------------
        # 1. TIME DOMAIN METRICS (MEASURED)
        # -------------------------------------------------------------
        mag = np.abs(sig)
        peak_amp = float(np.max(mag))
        min_amp = float(np.min(mag))
        rms_amp = float(np.sqrt(np.mean(mag ** 2)))
        mean_amp = float(np.mean(mag))
        
        # Crest Factor (Peak to Average Ratio)
        crest_factor = float(peak_amp / (rms_amp + 1e-12))
        papr_db = float(20 * np.log10(crest_factor + 1e-12))
        
        # Power in dBFS / relative
        signal_power = float(np.mean(mag ** 2))
        signal_power_db = float(10 * np.log10(signal_power + 1e-12))
        
        # -------------------------------------------------------------
        # 2. FREQUENCY DOMAIN METRICS (FFT / PSD)
        # -------------------------------------------------------------
        # Use Welch PSD for smooth spectral estimation
        nperseg = min(2048, 2 ** int(np.floor(np.log2(n_samples))))
        if nperseg < 64:
            nperseg = max(16, n_samples)
            
        if is_complex:
            freqs, psd = signal.welch(
                sig,
                fs=sample_rate,
                window='hann',
                nperseg=nperseg,
                return_onesided=False,
                scaling='density'
            )
            # Shift 0 to center
            freqs = np.fft.fftshift(freqs)
            psd = np.fft.fftshift(psd)
        else:
            freqs, psd = signal.welch(
                sig,
                fs=sample_rate,
                window='hann',
                nperseg=nperseg,
                return_onesided=True,
                scaling='density'
            )
            
        freqs_abs = freqs + center_freq_offset
        psd_db = 10 * np.log10(psd + 1e-18)
        
        # Peak Frequency & Peak PSD
        peak_idx = int(np.argmax(psd))
        peak_freq = float(freqs_abs[peak_idx])
        peak_psd_db = float(psd_db[peak_idx])
        
        # Noise Floor Estimation via lowest 20th percentile of PSD
        noise_floor_db = float(np.percentile(psd_db, 20))
        noise_power = float(10 ** (noise_floor_db / 10))
        
        # Measured SNR (Peak to noise floor & Total power to noise power)
        snr_db = float(max(0.0, peak_psd_db - noise_floor_db))
        
        # Occupied Bandwidth (99% power)
        total_energy = np.sum(psd)
        if total_energy > 0:
            cum_energy = np.cumsum(psd) / total_energy
            idx_005 = np.searchsorted(cum_energy, 0.005)
            idx_995 = min(len(freqs) - 1, np.searchsorted(cum_energy, 0.995))
            obw_99_hz = float(abs(freqs[idx_995] - freqs[idx_005]))
        else:
            obw_99_hz = 0.0
            
        # -3dB & -10dB Bandwidth around peak
        threshold_3db = peak_psd_db - 3.0
        threshold_10db = peak_psd_db - 10.0
        
        bw_3db_hz = ParameterExtractor._calc_bandwidth_at_threshold(freqs, psd_db, peak_idx, threshold_3db)
        bw_10db_hz = ParameterExtractor._calc_bandwidth_at_threshold(freqs, psd_db, peak_idx, threshold_10db)
        
        # Center Frequency (Power-weighted Centroid)
        psd_linear = np.maximum(0, psd)
        if np.sum(psd_linear) > 0:
            spectral_centroid_hz = float(np.sum(freqs_abs * psd_linear) / np.sum(psd_linear))
            # Spectral Spread / Variance
            spectral_spread_hz = float(np.sqrt(np.sum(((freqs_abs - spectral_centroid_hz) ** 2) * psd_linear) / np.sum(psd_linear)))
        else:
            spectral_centroid_hz = peak_freq
            spectral_spread_hz = 0.0
            
        # Spectral Flatness (Wiener entropy: Geometric mean / Arithmetic mean)
        geom_mean = np.exp(np.mean(np.log(psd_linear + 1e-15)))
        arith_mean = np.mean(psd_linear + 1e-15)
        spectral_flatness = float(geom_mean / arith_mean)
        
        # Spectral Rolloff (85% energy)
        if total_energy > 0:
            idx_85 = min(len(freqs) - 1, np.searchsorted(cum_energy, 0.85))
            spectral_rolloff_hz = float(freqs_abs[idx_85])
        else:
            spectral_rolloff_hz = peak_freq
            
        # Dominant Frequency Peaks (top 5)
        dominant_peaks = ParameterExtractor._find_dominant_peaks(freqs_abs, psd_db, peak_psd_db, top_k=5)
        
        # -------------------------------------------------------------
        # 3. STATISTICAL & STABILITY METRICS (DERIVED)
        # -------------------------------------------------------------
        # Amplitude envelope variance (Stability indicator: 1.0 is rock solid, <0.7 indicates pulsing/fading)
        env_mean = np.mean(mag)
        env_var = np.var(mag) / (env_mean ** 2 + 1e-12) if env_mean > 0 else 1.0
        amplitude_stability = float(np.clip(1.0 / (1.0 + env_var), 0.0, 1.0))
        
        # Frequency drift / instantaneous frequency stability
        if is_complex and n_samples > 32:
            phase = np.unwrap(np.angle(sig))
            inst_freq = np.diff(phase) / (2.0 * np.pi * dt)
            freq_drift_std = float(np.std(inst_freq))
            phase_jitter_rad = float(np.std(np.angle(sig)))
        else:
            # For real signal, compute Hilbert analytic signal phase
            try:
                analytic = signal.hilbert(sig)
                phase = np.unwrap(np.angle(analytic))
                inst_freq = np.diff(phase) / (2.0 * np.pi * dt)
                freq_drift_std = float(np.std(inst_freq))
                phase_jitter_rad = float(np.std(np.angle(analytic)))
            except Exception:
                freq_drift_std = 0.0
                phase_jitter_rad = 0.0
                
        # Spectral Shape moments (Kurtosis & Skewness)
        spec_kurt = float(kurtosis(psd_db))
        spec_skew = float(skew(psd_db))
        
        # Modulation Feature Hints (heuristic estimation based on envelope and phase variance)
        mod_hint, mod_confidence = ParameterExtractor._classify_modulation_hint(
            is_complex=is_complex,
            env_var=env_var,
            phase_jitter_rad=phase_jitter_rad,
            spectral_flatness=spectral_flatness,
            bw_3db_hz=bw_3db_hz,
            dominant_peaks=dominant_peaks
        )
        
        # Categorized outputs
        measured = {
            "peak_frequency_hz": round(peak_freq, 2),
            "peak_frequency_str": ParameterExtractor._format_hz(peak_freq),
            "spectral_centroid_hz": round(spectral_centroid_hz, 2),
            "spectral_centroid_str": ParameterExtractor._format_hz(spectral_centroid_hz),
            "signal_power_db": round(signal_power_db, 2),
            "estimated_noise_power_db": round(noise_floor_db, 2),
            "snr_db": round(snr_db, 2),
            "peak_amplitude_v": round(peak_amp, 4),
            "rms_amplitude_v": round(rms_amp, 4),
            "duration_sec": round(duration, 4),
            "sample_count": n_samples,
            "sample_rate_hz": float(sample_rate)
        }
        
        derived = {
            "bandwidth_3db_hz": round(bw_3db_hz, 2),
            "bandwidth_3db_str": ParameterExtractor._format_hz(bw_3db_hz),
            "bandwidth_10db_hz": round(bw_10db_hz, 2),
            "bandwidth_10db_str": ParameterExtractor._format_hz(bw_10db_hz),
            "occupied_bandwidth_99_hz": round(obw_99_hz, 2),
            "occupied_bandwidth_99_str": ParameterExtractor._format_hz(obw_99_hz),
            "crest_factor_ratio": round(crest_factor, 3),
            "papr_db": round(papr_db, 2),
            "signal_stability_index": round(amplitude_stability, 3),
            "frequency_drift_std_hz": round(freq_drift_std, 2),
            "phase_jitter_rad": round(phase_jitter_rad, 4),
            "spectral_flatness": round(spectral_flatness, 4),
            "spectral_spread_hz": round(spectral_spread_hz, 2),
            "spectral_rolloff_hz": round(spectral_rolloff_hz, 2),
            "spectral_kurtosis": round(spec_kurt, 3),
            "spectral_skewness": round(spec_skew, 3),
            "modulation_type_hint": mod_hint,
            "modulation_hint_confidence_pct": round(mod_confidence, 1)
        }
        
        return {
            "measured": measured,
            "derived": derived,
            "dominant_peaks": dominant_peaks,
            "raw_summary": {
                "center_freq_hz": spectral_centroid_hz,
                "peak_freq_hz": peak_freq,
                "bandwidth_hz": obw_99_hz if obw_99_hz > 0 else bw_3db_hz,
                "power_db": signal_power_db,
                "snr_db": snr_db,
                "stability": amplitude_stability,
                "duration_sec": duration
            }
        }

    @staticmethod
    def _calc_bandwidth_at_threshold(
        freqs: np.ndarray,
        psd_db: np.ndarray,
        peak_idx: int,
        threshold_db: float
    ) -> float:
        n = len(psd_db)
        # Scan left
        left_idx = peak_idx
        while left_idx > 0 and psd_db[left_idx] >= threshold_db:
            left_idx -= 1
            
        # Scan right
        right_idx = peak_idx
        while right_idx < n - 1 and psd_db[right_idx] >= threshold_db:
            right_idx += 1
            
        bw = abs(freqs[right_idx] - freqs[left_idx])
        return float(bw)

    @staticmethod
    def _find_dominant_peaks(
        freqs: np.ndarray,
        psd_db: np.ndarray,
        peak_val: float,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        peaks, props = signal.find_peaks(psd_db, height=peak_val - 25.0, distance=max(1, len(freqs)//50))
        if len(peaks) == 0:
            peaks = [int(np.argmax(psd_db))]
            
        # Sort by power
        sorted_indices = sorted(peaks, key=lambda i: psd_db[i], reverse=True)[:top_k]
        
        results = []
        for rank, idx in enumerate(sorted_indices, start=1):
            results.append({
                "rank": rank,
                "frequency_hz": round(float(freqs[idx]), 2),
                "frequency_str": ParameterExtractor._format_hz(float(freqs[idx])),
                "power_db": round(float(psd_db[idx]), 2),
                "relative_to_peak_db": round(float(psd_db[idx] - peak_val), 2)
            })
        return results

    @staticmethod
    def _classify_modulation_hint(
        is_complex: bool,
        env_var: float,
        phase_jitter_rad: float,
        spectral_flatness: float,
        bw_3db_hz: float,
        dominant_peaks: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """Explainable heuristic modulation classifier for defense & space telemetry."""
        if spectral_flatness > 0.6:
            return "Wideband Noise / Spread Spectrum", 85.0
            
        if len(dominant_peaks) == 1 and env_var < 0.05 and phase_jitter_rad < 0.2:
            return "Continuous Wave (CW / Unmodulated Carrier)", 92.0
            
        if len(dominant_peaks) >= 2 and env_var < 0.15:
            return "Frequency Shift Keying (FSK / 2-FSK/4-FSK)", 88.0
            
        if is_complex and env_var < 0.25 and phase_jitter_rad > 0.6:
            return "Phase Shift Keying (BPSK / QPSK Telemetry)", 86.0
            
        if env_var > 0.35 and phase_jitter_rad < 0.5:
            return "Amplitude Modulation (AM / ASK)", 82.0
            
        if env_var < 0.2 and phase_jitter_rad > 0.8:
            return "Frequency Modulation (FM / Chirp)", 84.0
            
        return "Complex Telemetry / Multi-carrier", 75.0

    @staticmethod
    def _format_hz(val_hz: float) -> str:
        abs_val = abs(val_hz)
        if abs_val >= 1e9:
            return f"{val_hz / 1e9:.4f} GHz"
        elif abs_val >= 1e6:
            return f"{val_hz / 1e6:.4f} MHz"
        elif abs_val >= 1e3:
            return f"{val_hz / 1e3:.3f} kHz"
        else:
            return f"{val_hz:.2f} Hz"
