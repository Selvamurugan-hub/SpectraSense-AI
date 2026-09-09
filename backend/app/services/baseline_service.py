import json
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.database.models import SignalBaseline

class BaselineService:
    """Manages historical signal baselines and parameter distributions."""
    
    @staticmethod
    def get_or_match_baseline(
        db: Session,
        center_freq_hz: float,
        sample_rate: float,
        tolerance_hz: float = 50000.0
    ) -> Optional[SignalBaseline]:
        """Finds closest baseline within frequency tolerance, or returns None."""
        baselines = db.query(SignalBaseline).all()
        if not baselines:
            return None
            
        best_match = None
        min_diff = float("inf")
        
        for b in baselines:
            diff = abs(b.center_freq_mean - center_freq_hz)
            if diff < tolerance_hz and diff < min_diff:
                min_diff = diff
                best_match = b
                
        return best_match

    @staticmethod
    def create_or_update_baseline(
        db: Session,
        name: str,
        description: str,
        sample_rate: float,
        extracted_params: Dict[str, Any],
        fingerprint: Dict[str, Any],
        signal_type: str = "space_telemetry"
    ) -> SignalBaseline:
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        fc = measured["spectral_centroid_hz"]
        bw = derived["occupied_bandwidth_99_hz"]
        pwr = measured["signal_power_db"]
        snr = measured["snr_db"]
        stab = derived["signal_stability_index"]
        rms = measured["rms_amplitude_v"]
        
        baseline = db.query(SignalBaseline).filter(SignalBaseline.name == name).first()
        
        if baseline:
            # Update running average
            n = baseline.sample_count
            baseline.center_freq_mean = (baseline.center_freq_mean * n + fc) / (n + 1)
            baseline.bandwidth_mean = (baseline.bandwidth_mean * n + bw) / (n + 1)
            baseline.power_mean = (baseline.power_mean * n + pwr) / (n + 1)
            baseline.snr_mean = (baseline.snr_mean * n + snr) / (n + 1)
            baseline.stability_mean = (baseline.stability_mean * n + stab) / (n + 1)
            baseline.rms_mean = (baseline.rms_mean * n + rms) / (n + 1)
            
            # Simple std estimate expansion
            baseline.center_freq_std = max(100.0, abs(fc - baseline.center_freq_mean) * 0.8)
            baseline.bandwidth_std = max(50.0, abs(bw - baseline.bandwidth_mean) * 0.8)
            baseline.snr_std = max(0.5, abs(snr - baseline.snr_mean) * 0.8)
            baseline.power_std = max(0.5, abs(pwr - baseline.power_mean) * 0.8)
            baseline.stability_std = max(0.02, abs(stab - baseline.stability_mean) * 0.8)
            
            baseline.sample_count = n + 1
            baseline.fingerprint_template = json.dumps(fingerprint)
        else:
            baseline = SignalBaseline(
                name=name,
                description=description,
                signal_type=signal_type,
                sample_rate=sample_rate,
                center_freq_mean=fc,
                center_freq_std=max(100.0, abs(fc * 0.02)),
                bandwidth_mean=bw,
                bandwidth_std=max(50.0, abs(bw * 0.05)),
                power_mean=pwr,
                power_std=2.0,
                snr_mean=snr,
                snr_std=1.5,
                stability_mean=stab,
                stability_std=0.05,
                rms_mean=rms,
                rms_std=0.02,
                sample_count=1,
                fingerprint_template=json.dumps(fingerprint)
            )
            db.add(baseline)
            
        db.commit()
        db.refresh(baseline)
        return baseline
