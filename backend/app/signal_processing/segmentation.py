import numpy as np
from typing import List, Dict, Any

class SignalSegmenter:
    """Automatic activity and burst segmentation using energy envelope & hysteresis thresholding."""
    
    @staticmethod
    def segment_signal(
        signal_data: np.ndarray,
        sample_rate: float,
        frame_len_sec: float = 0.005,  # 5ms window
        hop_sec: float = 0.002,       # 2ms hop
        min_duration_sec: float = 0.01,
        min_gap_sec: float = 0.01
    ) -> List[Dict[str, Any]]:
        n_samples = len(signal_data)
        if n_samples == 0:
            return []
            
        frame_len = max(32, int(frame_len_sec * sample_rate))
        hop_len = max(16, int(hop_sec * sample_rate))
        
        # Calculate instantaneous power / envelope
        mag_sq = np.abs(signal_data) ** 2
        
        # Sliding short-time energy
        num_frames = (n_samples - frame_len) // hop_len + 1
        if num_frames <= 1:
            # Entire signal is single segment
            dur = n_samples / sample_rate
            pwr = float(10 * np.log10(np.mean(mag_sq) + 1e-12))
            return [{
                "segment_index": 1,
                "start_time_sec": 0.0,
                "end_time_sec": round(dur, 4),
                "duration_sec": round(dur, 4),
                "estimated_power_db": round(pwr, 2),
                "start_idx": 0,
                "end_idx": n_samples,
                "snr_estimate_db": 15.0
            }]
            
        # Compute energy across frames
        energies = np.zeros(num_frames)
        for i in range(num_frames):
            st = i * hop_len
            energies[i] = np.mean(mag_sq[st:st + frame_len])
            
        energy_db = 10 * np.log10(energies + 1e-12)
        
        # Adaptive threshold: median + 0.3 * (90th percentile - median)
        med_e = np.median(energy_db)
        p90_e = np.percentile(energy_db, 90)
        p10_e = np.percentile(energy_db, 10)
        
        # Dynamic threshold
        dynamic_range = p90_e - p10_e
        if dynamic_range > 6.0:
            threshold_db = med_e + 0.25 * dynamic_range
        else:
            # Relatively flat/continuous signal
            threshold_db = med_e - 3.0
            
        active = energy_db > threshold_db
        
        # Merge short gaps and enforce min duration
        min_active_frames = max(1, int(min_duration_sec / hop_sec))
        min_gap_frames = max(1, int(min_gap_sec / hop_sec))
        
        # Clean transitions
        segments_raw = []
        in_segment = False
        start_f = 0
        
        for i, is_act in enumerate(active):
            if is_act and not in_segment:
                in_segment = True
                start_f = i
            elif not is_act and in_segment:
                in_segment = False
                if (i - start_f) >= min_active_frames:
                    segments_raw.append((start_f, i))
                    
        if in_segment and (num_frames - start_f) >= min_active_frames:
            segments_raw.append((start_f, num_frames))
            
        # Merge close segments (gap < min_gap_frames)
        merged = []
        for seg in segments_raw:
            if not merged:
                merged.append(list(seg))
            else:
                prev = merged[-1]
                if (seg[0] - prev[1]) <= min_gap_frames:
                    prev[1] = seg[1]
                else:
                    merged.append(list(seg))
                    
        # If no active bursts detected (e.g. continuous CW or noise), fallback to full signal or equal slices
        if not merged:
            dur = n_samples / sample_rate
            pwr = float(10 * np.log10(np.mean(mag_sq) + 1e-12))
            return [{
                "segment_index": 1,
                "start_time_sec": 0.0,
                "end_time_sec": round(dur, 4),
                "duration_sec": round(dur, 4),
                "estimated_power_db": round(pwr, 2),
                "start_idx": 0,
                "end_idx": n_samples,
                "snr_estimate_db": round(float(p90_e - p10_e), 2)
            }]
            
        # Build segment dictionaries
        results = []
        for idx, (st_f, end_f) in enumerate(merged):
            st_samp = min(n_samples - 1, st_f * hop_len)
            end_samp = min(n_samples, end_f * hop_len + frame_len)
            seg_data = signal_data[st_samp:end_samp]
            if len(seg_data) == 0:
                continue
                
            seg_dur = len(seg_data) / sample_rate
            seg_pwr = float(10 * np.log10(np.mean(np.abs(seg_data)**2) + 1e-12))
            st_time = st_samp / sample_rate
            end_time = end_samp / sample_rate
            
            # Local SNR estimate
            noise_est = p10_e
            local_snr = max(0.0, seg_pwr - noise_est)
            
            results.append({
                "segment_index": idx + 1,
                "start_time_sec": round(st_time, 4),
                "end_time_sec": round(end_time, 4),
                "duration_sec": round(seg_dur, 4),
                "estimated_power_db": round(seg_pwr, 2),
                "start_idx": int(st_samp),
                "end_idx": int(end_samp),
                "snr_estimate_db": round(local_snr, 2)
            })
            
        return results
