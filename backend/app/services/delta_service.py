import numpy as np
from typing import Dict, Any, List, Optional
from app.database.models import SignalBaseline

class DeltaService:
    """'What Changed?' Comparative Delta Engine."""

    @staticmethod
    def compute_delta(
        extracted_params: Dict[str, Any],
        baseline: Optional[SignalBaseline]
    ) -> Dict[str, Any]:
        if baseline is None:
            return {
                "has_baseline": False,
                "baseline_name": None,
                "message": "No historical baseline available",
                "deltas": []
            }
            
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        current_fc = measured["spectral_centroid_hz"]
        current_bw = derived["occupied_bandwidth_99_hz"]
        current_snr = measured["snr_db"]
        current_pwr = measured["signal_power_db"]
        current_stab = derived["signal_stability_index"]
        current_rms = measured["rms_amplitude_v"]
        
        deltas = []
        
        # 1. Center Frequency
        deltas.append(DeltaService._compare_param(
            param_name="Center Frequency",
            unit="Hz",
            current_val=current_fc,
            baseline_mean=baseline.center_freq_mean,
            baseline_std=baseline.center_freq_std,
            threshold_pct=2.0
        ))
        
        # 2. Bandwidth (99% OBW)
        deltas.append(DeltaService._compare_param(
            param_name="Bandwidth (99% OBW)",
            unit="Hz",
            current_val=current_bw,
            baseline_mean=baseline.bandwidth_mean,
            baseline_std=baseline.bandwidth_std,
            threshold_pct=5.0
        ))
        
        # 3. SNR
        deltas.append(DeltaService._compare_param(
            param_name="Signal-to-Noise Ratio (SNR)",
            unit="dB",
            current_val=current_snr,
            baseline_mean=baseline.snr_mean,
            baseline_std=baseline.snr_std,
            threshold_pct=5.0,
            is_linear_pct=False  # dB comparison
        ))
        
        # 4. Signal Power
        deltas.append(DeltaService._compare_param(
            param_name="Signal Power",
            unit="dBFS",
            current_val=current_pwr,
            baseline_mean=baseline.power_mean,
            baseline_std=baseline.power_std,
            threshold_pct=5.0,
            is_linear_pct=False
        ))
        
        # 5. Signal Stability
        deltas.append(DeltaService._compare_param(
            param_name="Signal Stability",
            unit="index",
            current_val=current_stab,
            baseline_mean=baseline.stability_mean,
            baseline_std=baseline.stability_std,
            threshold_pct=8.0
        ))
        
        # 6. RMS Amplitude
        deltas.append(DeltaService._compare_param(
            param_name="RMS Amplitude",
            unit="V",
            current_val=current_rms,
            baseline_mean=baseline.rms_mean,
            baseline_std=baseline.rms_std,
            threshold_pct=5.0
        ))
        
        return {
            "has_baseline": True,
            "baseline_id": baseline.id,
            "baseline_name": baseline.name,
            "sample_count": baseline.sample_count,
            "deltas": deltas
        }

    @staticmethod
    def _compare_param(
        param_name: str,
        unit: str,
        current_val: float,
        baseline_mean: float,
        baseline_std: float,
        threshold_pct: float = 5.0,
        is_linear_pct: bool = True
    ) -> Dict[str, Any]:
        diff = current_val - baseline_mean
        
        if is_linear_pct:
            denom = abs(baseline_mean) if abs(baseline_mean) > 1e-6 else 1.0
            pct_change = (diff / denom) * 100.0
        else:
            # For dB, the arithmetic difference is directly the ratio in dB
            pct_change = diff
            
        z_score = diff / (baseline_std + 1e-6)
        
        if abs(pct_change) < threshold_pct:
            direction = "STABLE"
            arrow = "→"
            status = "Nominal"
            badge_color = "green"
        elif pct_change > 0:
            direction = "INCREASE"
            arrow = "↑"
            status = "Elevated" if abs(z_score) < 3.0 else "Anomalous High"
            badge_color = "amber" if abs(z_score) < 3.0 else "red"
        else:
            direction = "DECREASE"
            arrow = "↓"
            status = "Reduced" if abs(z_score) < 3.0 else "Anomalous Low"
            badge_color = "amber" if abs(z_score) < 3.0 else "red"
            
        # Expected normal range: mean ± 2*std
        min_normal = baseline_mean - 2.0 * baseline_std
        max_normal = baseline_mean + 2.0 * baseline_std
        
        return {
            "parameter": param_name,
            "unit": unit,
            "baseline_value": round(baseline_mean, 3),
            "normal_range_str": f"{round(min_normal, 2)} to {round(max_normal, 2)} {unit}",
            "current_value": round(current_val, 3),
            "delta_absolute": round(diff, 3),
            "delta_pct": round(pct_change, 1),
            "z_score": round(z_score, 2),
            "direction": direction,
            "arrow": arrow,
            "status": status,
            "badge_color": badge_color,
            "is_significant": abs(z_score) >= 2.0
        }
