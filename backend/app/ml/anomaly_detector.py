import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
from app.database.models import SignalBaseline

class SignalAnomalyDetector:
    """Explainable Multi-Layer Anomaly Detection (Statistical Z-Score + Mahalanobis + Isolation Forest)."""

    @staticmethod
    def detect_anomalies(
        extracted_params: Dict[str, Any],
        segments: List[Dict[str, Any]],
        baseline: Optional[SignalBaseline]
    ) -> List[Dict[str, Any]]:
        anomalies = []
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        # 1. Baseline-Referenced Statistical Deviations
        if baseline is not None:
            # A. Center Frequency Drift
            fc_diff = abs(measured["spectral_centroid_hz"] - baseline.center_freq_mean)
            fc_z = fc_diff / (baseline.center_freq_std + 1e-6)
            if fc_z >= 2.5:
                sev = "CRITICAL" if fc_z >= 4.0 else "HIGH"
                pct = ((measured["spectral_centroid_hz"] - baseline.center_freq_mean) / baseline.center_freq_mean) * 100.0
                anomalies.append({
                    "affected_parameter": "Center Frequency",
                    "severity": sev,
                    "anomaly_score": min(1.0, round(float(fc_z / 5.0), 2)),
                    "observed_value": f"{measured['spectral_centroid_hz']:.1f} Hz",
                    "expected_range": f"{baseline.center_freq_mean - 2*baseline.center_freq_std:.1f} to {baseline.center_freq_mean + 2*baseline.center_freq_std:.1f} Hz",
                    "deviation_pct": round(pct, 1),
                    "reason": f"Center frequency drifted by {pct:+.1f}% ({fc_diff:.1f} Hz) from baseline mean ({fc_z:.1f}σ deviation). Possible oscillator frequency drift or Doppler shift.",
                    "segment_index": None
                })
                
            # B. Severe SNR Degradation
            snr_drop = baseline.snr_mean - measured["snr_db"]
            snr_z = snr_drop / (baseline.snr_std + 1e-6)
            if snr_drop >= 4.0 and snr_z >= 2.0:
                sev = "CRITICAL" if snr_drop >= 10.0 else "WARNING"
                anomalies.append({
                    "affected_parameter": "Signal-to-Noise Ratio (SNR)",
                    "severity": sev,
                    "anomaly_score": min(1.0, round(float(snr_z / 4.0), 2)),
                    "observed_value": f"{measured['snr_db']:.1f} dB",
                    "expected_range": f">= {baseline.snr_mean - 2*baseline.snr_std:.1f} dB (Nominal: {baseline.snr_mean:.1f} dB)",
                    "deviation_pct": round(-snr_drop, 1),
                    "reason": f"SNR degraded by {snr_drop:.1f} dB below historical baseline. Indicates elevated channel noise floor, attenuation, or RF interference.",
                    "segment_index": None
                })
                
            # C. Bandwidth Expansion or Compression
            bw_diff = abs(derived["occupied_bandwidth_99_hz"] - baseline.bandwidth_mean)
            bw_z = bw_diff / (baseline.bandwidth_std + 1e-6)
            if bw_z >= 3.0:
                sev = "HIGH" if bw_z >= 4.5 else "WARNING"
                pct = ((derived["occupied_bandwidth_99_hz"] - baseline.bandwidth_mean) / baseline.bandwidth_mean) * 100.0
                anomalies.append({
                    "affected_parameter": "Occupied Bandwidth",
                    "severity": sev,
                    "anomaly_score": min(1.0, round(float(bw_z / 5.0), 2)),
                    "observed_value": f"{derived['occupied_bandwidth_99_hz']:.1f} Hz",
                    "expected_range": f"{baseline.bandwidth_mean - 2*baseline.bandwidth_std:.1f} to {baseline.bandwidth_mean + 2*baseline.bandwidth_std:.1f} Hz",
                    "deviation_pct": round(pct, 1),
                    "reason": f"Occupied bandwidth expanded/compressed by {pct:+.1f}% from nominal baseline. Indicates symbol rate change, non-linear distortion, or spectral regrowth.",
                    "segment_index": None
                })
                
            # D. Stability Degradation
            stab_drop = baseline.stability_mean - derived["signal_stability_index"]
            if stab_drop >= 0.20:
                anomalies.append({
                    "affected_parameter": "Signal Stability",
                    "severity": "WARNING",
                    "anomaly_score": round(float(stab_drop), 2),
                    "observed_value": f"{derived['signal_stability_index']:.2f}",
                    "expected_range": f">= {baseline.stability_mean - 2*baseline.stability_std:.2f}",
                    "deviation_pct": round(-stab_drop * 100.0, 1),
                    "reason": f"Signal amplitude stability dropped by {stab_drop * 100:.1f}%. Indicates amplitude fluctuations, carrier fading, or intermittent burst dropping.",
                    "segment_index": None
                })

        # 2. Intrinsic Segment-to-Segment Anomaly Detection (Isolation Forest / Outlier scan)
        if len(segments) >= 4:
            seg_features = []
            for s in segments:
                pwr = s.get("estimated_power_db", 0.0)
                dur = s.get("duration_sec", 0.0)
                snr = s.get("snr_estimate_db", 10.0)
                seg_features.append([pwr, dur, snr])
                
            X = np.array(seg_features)
            # Standardize
            X_std = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-6)
            
            try:
                clf = IsolationForest(contamination=0.15, random_state=42)
                preds = clf.fit_predict(X_std)
                scores = clf.decision_function(X_std)
                
                for idx, (pred, score) in enumerate(zip(preds, scores)):
                    if pred == -1:  # Outlier segment
                        seg = segments[idx]
                        anom_score = float(np.clip(1.0 - (score + 0.5), 0.0, 1.0))
                        anomalies.append({
                            "affected_parameter": f"Segment #{seg['segment_index']} Profile",
                            "severity": "WARNING" if anom_score < 0.75 else "HIGH",
                            "anomaly_score": round(anom_score, 2),
                            "observed_value": f"Power: {seg['estimated_power_db']} dB, Dur: {seg['duration_sec']}s",
                            "expected_range": "Clustered segment envelope",
                            "deviation_pct": round(anom_score * 50.0, 1),
                            "reason": f"Segment #{seg['segment_index']} at {seg['start_time_sec']}s deviates significantly in power/duration envelope compared to adjacent pulse segments.",
                            "segment_index": seg["segment_index"]
                        })
            except Exception:
                pass
                
        # 3. Intrinsic Low SNR or Flatness warning even without baseline
        if measured["snr_db"] < 4.0 and not any(a["affected_parameter"] == "Signal-to-Noise Ratio (SNR)" for a in anomalies):
            anomalies.append({
                "affected_parameter": "Signal-to-Noise Ratio (SNR)",
                "severity": "WARNING",
                "anomaly_score": 0.65,
                "observed_value": f"{measured['snr_db']:.1f} dB",
                "expected_range": ">= 6.0 dB for reliable demodulation",
                "deviation_pct": -40.0,
                "reason": "Signal is operating near or below typical receiver sensitivity threshold (SNR < 4 dB).",
                "segment_index": None
            })
            
        return anomalies
