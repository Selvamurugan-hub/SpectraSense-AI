import numpy as np
from scipy import signal
from typing import Tuple, Dict, Any, Optional

class SignalPreprocessor:
    """Standardized DSP preprocessing pipeline."""
    
    @staticmethod
    def preprocess(
        raw_signal: np.ndarray,
        sample_rate: float,
        remove_dc: bool = True,
        normalize: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # 1. Handle invalid/NaN/Inf values
        if not np.isfinite(raw_signal).all():
            raw_signal = np.nan_to_num(raw_signal, nan=0.0, posinf=1.0, neginf=-1.0)
            
        is_complex = np.iscomplexobj(raw_signal)
        processed = raw_signal.copy()
        
        # 2. DC Offset Removal
        dc_i = 0.0
        dc_q = 0.0
        if remove_dc:
            if is_complex:
                dc_i = float(np.mean(processed.real))
                dc_q = float(np.mean(processed.imag))
                processed = (processed.real - dc_i) + 1j * (processed.imag - dc_q)
            else:
                dc_i = float(np.mean(processed))
                processed = processed - dc_i
                
        # 3. Peak & RMS check
        peak_raw = float(np.max(np.abs(processed))) if len(processed) > 0 else 1.0
        if peak_raw == 0:
            peak_raw = 1.0
            
        # 4. Amplitude Normalization (scale to unit peak without distortion)
        if normalize and peak_raw > 0:
            processed = processed / peak_raw
            
        # 5. Noise floor estimate (MAD based)
        mag = np.abs(processed)
        noise_floor_estimate = float(np.median(mag) * 0.6745)
        
        metadata = {
            "is_complex": is_complex,
            "dc_offset_removed": {"I": round(dc_i, 6), "Q": round(dc_q, 6) if is_complex else 0.0},
            "peak_raw_amplitude": round(peak_raw, 6),
            "noise_floor_estimate": round(noise_floor_estimate, 6),
            "normalized": normalize,
            "sample_count": len(processed)
        }
        
        return processed, metadata

    @staticmethod
    def downsample_for_display(
        data: np.ndarray,
        max_points: int = 2000
    ) -> np.ndarray:
        """Min-Max decimation preserving peaks and envelopes for smooth chart rendering."""
        n = len(data)
        if n <= max_points:
            return data
            
        step = n // (max_points // 2)
        if step < 1:
            step = 1
            
        sampled = []
        for i in range(0, n, step):
            chunk = data[i:i + step]
            if len(chunk) == 0:
                continue
            if np.iscomplexobj(data):
                # Pick max magnitude sample and min magnitude sample
                mags = np.abs(chunk)
                min_idx = np.argmin(mags)
                max_idx = np.argmax(mags)
                sampled.append(chunk[min_idx])
                if min_idx != max_idx:
                    sampled.append(chunk[max_idx])
            else:
                min_idx = np.argmin(chunk)
                max_idx = np.argmax(chunk)
                sampled.append(chunk[min_idx])
                if min_idx != max_idx:
                    sampled.append(chunk[max_idx])
                    
        return np.array(sampled[:max_points])
