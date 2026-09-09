import numpy as np
from pathlib import Path
from scipy.io import wavfile
from typing import Dict, Any, List
from app.core.config import SAMPLE_DIR

class SyntheticSignalGenerator:
    """Generates realistic synthetic space & defense telemetry test signals."""

    @staticmethod
    def generate_all_samples() -> List[Dict[str, Any]]:
        SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
        results = []
        
        # 1. Nominal Space QPSK Telemetry (IQ Float32)
        qpsk_nom_path = SAMPLE_DIR / "DEMO_SAT_QPSK_NOMINAL.iq"
        if not qpsk_nom_path.exists():
            fs = 500000.0  # 500 kSps
            t_dur = 1.0    # 1 second
            n_samples = int(fs * t_dur)
            t = np.arange(n_samples) / fs
            
            # QPSK modulation
            baud_rate = 25000
            samples_per_sym = int(fs / baud_rate)
            num_syms = n_samples // samples_per_sym + 1
            
            bits_i = 2 * np.random.randint(0, 2, num_syms) - 1
            bits_q = 2 * np.random.randint(0, 2, num_syms) - 1
            
            syms_i = np.repeat(bits_i, samples_per_sym)[:n_samples]
            syms_q = np.repeat(bits_q, samples_per_sym)[:n_samples]
            
            # Pulse shaping filter approximation
            h = np.ones(samples_per_sym) / np.sqrt(samples_per_sym)
            bb_i = np.convolve(syms_i, h, mode='same')
            bb_q = np.convolve(syms_q, h, mode='same')
            
            # Carrier at 80 kHz
            fc = 80000.0
            carrier = np.exp(1j * 2 * np.pi * fc * t)
            qpsk_sig = (bb_i + 1j * bb_q) * carrier
            
            # Add moderate noise (SNR ~ 25 dB)
            noise = (np.random.randn(n_samples) + 1j * np.random.randn(n_samples)) * 0.08
            signal_out = (qpsk_sig + noise).astype(np.complex64)
            
            # Interleave I and Q as float32
            interleaved = np.empty(n_samples * 2, dtype=np.float32)
            interleaved[0::2] = signal_out.real
            interleaved[1::2] = signal_out.imag
            interleaved.tofile(str(qpsk_nom_path))
            
        results.append({
            "name": "DEMO_SAT_QPSK_NOMINAL.iq",
            "file_path": str(qpsk_nom_path),
            "file_type": "iq",
            "sample_rate": 500000.0,
            "iq_format": "float32",
            "description": "Nominal Space Telemetry QPSK downlink (Clean SNR ~25dB, 80kHz Carrier)",
            "is_anomaly": False
        })

        # 2. Degraded Space QPSK Telemetry (Anomalous)
        qpsk_deg_path = SAMPLE_DIR / "DEMO_SAT_QPSK_DEGRADED.iq"
        if not qpsk_deg_path.exists():
            fs = 500000.0
            t_dur = 1.0
            n_samples = int(fs * t_dur)
            t = np.arange(n_samples) / fs
            
            baud_rate = 25000
            samples_per_sym = int(fs / baud_rate)
            num_syms = n_samples // samples_per_sym + 1
            
            bits_i = 2 * np.random.randint(0, 2, num_syms) - 1
            bits_q = 2 * np.random.randint(0, 2, num_syms) - 1
            
            syms_i = np.repeat(bits_i, samples_per_sym)[:n_samples]
            syms_q = np.repeat(bits_q, samples_per_sym)[:n_samples]
            
            bb_i = np.convolve(syms_i, np.ones(samples_per_sym)/np.sqrt(samples_per_sym), mode='same')
            bb_q = np.convolve(syms_q, np.ones(samples_per_sym)/np.sqrt(samples_per_sym), mode='same')
            
            # Frequency drift (+22 kHz error) and severe phase jitter
            fc = 102000.0  # Drifted from 80kHz!
            phase_noise = np.cumsum(np.random.randn(n_samples) * 0.05)
            carrier = np.exp(1j * (2 * np.pi * fc * t + phase_noise))
            qpsk_sig = (bb_i + 1j * bb_q) * carrier
            
            # High noise (SNR ~ 9 dB)
            noise = (np.random.randn(n_samples) + 1j * np.random.randn(n_samples)) * 0.35
            signal_out = (qpsk_sig + noise).astype(np.complex64)
            
            interleaved = np.empty(n_samples * 2, dtype=np.float32)
            interleaved[0::2] = signal_out.real
            interleaved[1::2] = signal_out.imag
            interleaved.tofile(str(qpsk_deg_path))
            
        results.append({
            "name": "DEMO_SAT_QPSK_DEGRADED.iq",
            "file_path": str(qpsk_deg_path),
            "file_type": "iq",
            "sample_rate": 500000.0,
            "iq_format": "float32",
            "description": "Degraded Space QPSK Telemetry (Carrier Frequency Drift +22kHz, High Noise SNR ~9dB)",
            "is_anomaly": True
        })

        # 3. Pulsed LFM Radar Chirp (WAV format)
        radar_path = SAMPLE_DIR / "DEMO_RADAR_CHIRP_PULSED.wav"
        if not radar_path.exists():
            fs = 48000
            t_dur = 2.0
            n_samples = int(fs * t_dur)
            t = np.arange(n_samples) / fs
            sig = np.zeros(n_samples, dtype=np.float32)
            
            # 5 Chirp Pulses: 20ms pulse width every 350ms
            pulse_len = int(0.04 * fs)
            f0, f1 = 2000.0, 12000.0
            t_pulse = np.arange(pulse_len) / fs
            chirp_pulse = np.sin(2 * np.pi * (f0 * t_pulse + ((f1 - f0) / (2 * 0.04)) * (t_pulse ** 2)))
            
            # Apply Hann taper to pulse
            chirp_pulse *= np.hanning(pulse_len)
            
            pulse_offsets = [0.1, 0.5, 0.9, 1.3, 1.7]
            for po in pulse_offsets:
                st = int(po * fs)
                if st + pulse_len <= n_samples:
                    sig[st:st + pulse_len] += chirp_pulse
                    
            # Add thermal background noise
            sig += np.random.randn(n_samples) * 0.02
            # Normalize to 16-bit PCM
            sig = sig / np.max(np.abs(sig)) * 0.9
            wavfile.write(str(radar_path), fs, (sig * 32767).astype(np.int16))
            
        results.append({
            "name": "DEMO_RADAR_CHIRP_PULSED.wav",
            "file_path": str(radar_path),
            "file_type": "wav",
            "sample_rate": 48000.0,
            "iq_format": "wav_pcm",
            "description": "Multi-pulse LFM Radar Chirp (2-12kHz Sweep, 5 Periodic Burst Segments)",
            "is_anomaly": False
        })

        # 4. Multi-Burst FSK Telemetry Beacon (WAV format)
        fsk_path = SAMPLE_DIR / "DEMO_FSK_TELEMETRY_BEACON.wav"
        if not fsk_path.exists():
            fs = 44100
            t_dur = 2.0
            n_samples = int(fs * t_dur)
            t = np.arange(n_samples) / fs
            sig = np.zeros(n_samples, dtype=np.float32)
            
            # Burst 1 at 0.2s, Burst 2 at 1.1s
            tones = [3000.0, 5000.0, 7000.0, 9000.0]
            bursts = [(0.2, 0.6), (1.1, 1.7)]
            
            for st_sec, end_sec in bursts:
                st_idx = int(st_sec * fs)
                end_idx = int(end_sec * fs)
                seg_len = end_idx - st_idx
                hop_len = seg_len // 8
                
                for h in range(8):
                    h_st = st_idx + h * hop_len
                    h_end = min(end_idx, h_st + hop_len)
                    f_tone = tones[h % len(tones)]
                    t_hop = np.arange(h_end - h_st) / fs
                    sig[h_st:h_end] = np.sin(2 * np.pi * f_tone * t_hop)
                    
            sig += np.random.randn(n_samples) * 0.03
            sig = sig / np.max(np.abs(sig)) * 0.85
            wavfile.write(str(fsk_path), fs, (sig * 32767).astype(np.int16))
            
        results.append({
            "name": "DEMO_FSK_TELEMETRY_BEACON.wav",
            "file_path": str(fsk_path),
            "file_type": "wav",
            "sample_rate": 44100.0,
            "iq_format": "wav_pcm",
            "description": "Multi-channel FSK Telemetry Beacon (4-ary Frequency Hopping Bursts)",
            "is_anomaly": False
        })

        return results
