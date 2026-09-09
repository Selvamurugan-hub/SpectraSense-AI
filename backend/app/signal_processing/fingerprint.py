import hashlib
import json
import numpy as np
from typing import Dict, Any, List

class SignalFingerprintEngine:
    """Deterministic Multi-Domain Signal Fingerprinting."""

    @staticmethod
    def generate_fingerprint(
        extracted_params: Dict[str, Any],
        sample_rate: float
    ) -> Dict[str, Any]:
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        # 1. Normalize feature dimensions into [0.0, 1.0]
        # Frequency score (normalized to Nyquist fs/2)
        nyquist = sample_rate / 2.0
        fc_norm = float(np.clip(abs(measured["spectral_centroid_hz"]) / (nyquist + 1e-6), 0.0, 1.0))
        
        # Bandwidth score (normalized to sample rate)
        bw_norm = float(np.clip(derived["occupied_bandwidth_99_hz"] / (sample_rate + 1e-6), 0.0, 1.0))
        
        # Power score (normalized from [-80dB, 0dB])
        pwr_db = measured["signal_power_db"]
        pwr_norm = float(np.clip((pwr_db + 80.0) / 80.0, 0.0, 1.0))
        
        # SNR score (normalized from [0dB, 40dB])
        snr_db = measured["snr_db"]
        snr_norm = float(np.clip(snr_db / 40.0, 0.0, 1.0))
        
        # Stability score
        stab_norm = float(np.clip(derived["signal_stability_index"], 0.0, 1.0))
        
        # Spectral Flatness
        flat_norm = float(np.clip(derived["spectral_flatness"], 0.0, 1.0))
        
        # Crest factor (normalized from [1.0, 10.0])
        cf_norm = float(np.clip((derived["crest_factor_ratio"] - 1.0) / 9.0, 0.0, 1.0))
        
        # 2. Key visual summary bars (0 to 100%)
        visual_bars = {
            "Frequency": int(round(fc_norm * 100)),
            "Bandwidth": int(round(bw_norm * 100)),
            "Power": int(round(pwr_norm * 100)),
            "SNR": int(round(snr_norm * 100)),
            "Stability": int(round(stab_norm * 100)),
            "Spectral Spread": int(round((1.0 - flat_norm) * 100))
        }
        
        # 3. Numeric feature vector
        vector = [
            round(fc_norm, 4),
            round(bw_norm, 4),
            round(pwr_norm, 4),
            round(snr_norm, 4),
            round(stab_norm, 4),
            round(flat_norm, 4),
            round(cf_norm, 4)
        ]
        
        # 4. Deterministic Hash ID
        canonical_str = f"fc:{measured['spectral_centroid_hz']:.1f}|bw:{derived['occupied_bandwidth_99_hz']:.1f}|snr:{measured['snr_db']:.1f}|stab:{derived['signal_stability_index']:.3f}"
        signature_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()[:16].upper()
        
        return {
            "fingerprint_id": f"FP-{signature_hash}",
            "hash_signature": signature_hash,
            "vector": vector,
            "vector_labels": ["Frequency", "Bandwidth", "Power", "SNR", "Stability", "Flatness", "CrestFactor"],
            "visual_bars": visual_bars,
            "metrics": {
                "center_frequency_hz": measured["spectral_centroid_hz"],
                "bandwidth_hz": derived["occupied_bandwidth_99_hz"],
                "signal_power_db": measured["signal_power_db"],
                "snr_db": measured["snr_db"],
                "stability_index": derived["signal_stability_index"],
                "crest_factor": derived["crest_factor_ratio"]
            }
        }

    @staticmethod
    def calculate_similarity(fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """Calculates cosine similarity (0 to 100%) between two fingerprints."""
        v1 = np.array(fp1.get("vector", []), dtype=np.float64)
        v2 = np.array(fp2.get("vector", []), dtype=np.float64)
        if len(v1) == 0 or len(v2) == 0 or len(v1) != len(v2):
            return 0.0
            
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        cos_sim = float(np.dot(v1, v2) / (norm1 * norm2))
        return round(float(np.clip(cos_sim * 100.0, 0.0, 100.0)), 2)
