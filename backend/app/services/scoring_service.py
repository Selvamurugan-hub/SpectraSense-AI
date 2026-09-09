import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from app.database.models import SignalBaseline

class ScoringService:
    """Computes Confidence Score, Signal Health Score (with explainable breakdown), Analyst Priority, and Technical Summaries."""

    @staticmethod
    def calculate_confidence_score(
        extracted_params: Dict[str, Any],
        segments: List[Dict[str, Any]],
        num_samples: int
    ) -> float:
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        score = 0.0
        
        # 1. Sample adequacy (up to 25 pts)
        if num_samples >= 100000:
            score += 25.0
        elif num_samples >= 10000:
            score += 20.0
        elif num_samples >= 2000:
            score += 15.0
        else:
            score += 10.0
            
        # 2. SNR Adequacy (up to 40 pts)
        snr = measured["snr_db"]
        if snr >= 20.0:
            score += 40.0
        elif snr >= 12.0:
            score += 30.0 + (snr - 12.0) * (10.0 / 8.0)
        elif snr >= 4.0:
            score += 15.0 + (snr - 4.0) * (15.0 / 8.0)
        else:
            score += max(5.0, snr * 2.5)
            
        # 3. Spectral Peak Prominence (up to 20 pts)
        flatness = derived["spectral_flatness"]
        prominence_factor = max(0.0, 1.0 - flatness)
        score += prominence_factor * 20.0
        
        # 4. Segmentation Quality (up to 15 pts)
        if len(segments) > 0:
            score += 15.0
        else:
            score += 8.0
            
        return round(float(min(99.0, max(20.0, score))), 1)

    @staticmethod
    def calculate_health_score(
        extracted_params: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        baseline: Optional[SignalBaseline]
    ) -> Tuple[float, str, List[Dict[str, Any]]]:
        """Calculates 0-100 Health Score with deductive factors."""
        base_score = 100.0
        breakdown = []
        
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        # Factor 1: SNR Health
        snr = measured["snr_db"]
        if snr < 6.0:
            penalty = 25.0
            base_score -= penalty
            breakdown.append({"factor": "Critical Low SNR (< 6 dB)", "impact": -25, "reason": f"Measured SNR is {snr:.1f} dB"})
        elif snr < 12.0:
            penalty = 12.0
            base_score -= penalty
            breakdown.append({"factor": "Sub-optimal SNR (< 12 dB)", "impact": -12, "reason": f"Measured SNR is {snr:.1f} dB"})
        else:
            breakdown.append({"factor": "Nominal SNR Quality", "impact": 0, "reason": f"Robust SNR at {snr:.1f} dB"})
            
        # Factor 2: Signal Stability
        stability = derived["signal_stability_index"]
        if stability < 0.6:
            penalty = 18.0
            base_score -= penalty
            breakdown.append({"factor": "High Envelope Instability", "impact": -18, "reason": f"Stability index at {stability:.2f}"})
        elif stability < 0.8:
            penalty = 8.0
            base_score -= penalty
            breakdown.append({"factor": "Moderate Envelope Variation", "impact": -8, "reason": f"Stability index at {stability:.2f}"})
        else:
            breakdown.append({"factor": "High Carrier Stability", "impact": 0, "reason": "Consistent amplitude & power profile"})

        # Factor 3: Anomalies Penalty
        for anom in anomalies:
            sev = anom.get("severity", "WARNING")
            if sev == "CRITICAL":
                pen = 20.0
            elif sev == "HIGH":
                pen = 14.0
            elif sev == "WARNING":
                pen = 8.0
            else:
                pen = 4.0
            base_score -= pen
            breakdown.append({
                "factor": f"{sev} Anomaly: {anom['affected_parameter']}",
                "impact": -int(pen),
                "reason": anom["reason"]
            })
            
        final_score = round(float(np.clip(base_score, 0.0, 100.0)), 1)
        
        if final_score >= 80.0:
            status = "GOOD"
        elif final_score >= 55.0:
            status = "WARNING"
        else:
            status = "CRITICAL"
            
        return final_score, status, breakdown

    @staticmethod
    def assign_analyst_priority(
        health_score: float,
        health_status: str,
        anomalies: List[Dict[str, Any]],
        confidence_score: float
    ) -> Tuple[str, str]:
        has_critical_anom = any(a.get("severity") == "CRITICAL" for a in anomalies)
        has_high_anom = any(a.get("severity") == "HIGH" for a in anomalies)
        
        if has_critical_anom or health_score < 50.0:
            priority = "HIGH"
            reasons = []
            if has_critical_anom:
                reasons.append("Critical parameter anomaly detected")
            if health_score < 50.0:
                reasons.append(f"Severe health degradation (Score: {health_score}/100)")
            return priority, "; ".join(reasons)
            
        if has_high_anom or health_status == "WARNING" or health_score < 75.0:
            priority = "MEDIUM"
            return priority, f"Warning state or moderate deviation detected (Health: {health_score}/100, Anomalies: {len(anomalies)})"
            
        return "LOW", "Signal operating within nominal tolerances. Routine monitoring."

    @staticmethod
    def generate_explainable_summary(
        filename: str,
        extracted_params: Dict[str, Any],
        segments: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        baseline: Optional[SignalBaseline],
        health_score: float,
        health_status: str,
        priority: str
    ) -> str:
        measured = extracted_params["measured"]
        derived = extracted_params["derived"]
        
        fc_str = measured["spectral_centroid_str"]
        bw_str = derived["occupied_bandwidth_99_str"]
        snr = measured["snr_db"]
        mod_hint = derived["modulation_type_hint"]
        
        lines = []
        lines.append(f"Automated analysis completed for '{filename}'.")
        lines.append(
            f"The recording contains {len(segments)} detected active segment(s) across a total duration of {measured['duration_sec']:.3f}s. "
            f"Spectral analysis identifies a center frequency at {fc_str} with an occupied bandwidth of {bw_str} and an SNR of {snr:.1f} dB "
            f"(Modulation profile: {mod_hint})."
        )
        
        if baseline:
            lines.append(
                f"Benchmarked against historical baseline '{baseline.name}'. "
                f"Statistical drift analysis indicates baseline center frequency was {baseline.center_freq_mean:.1f} Hz (observed: {measured['spectral_centroid_hz']:.1f} Hz) "
                f"and nominal SNR was {baseline.snr_mean:.1f} dB."
            )
        else:
            lines.append("No existing historical baseline matched this frequency band; current characteristics establish the initial baseline.")
            
        if anomalies:
            anom_descs = [f"- {a['affected_parameter']} ({a['severity']}): {a['reason']}" for a in anomalies]
            lines.append(f"Detected {len(anomalies)} anomaly condition(s):\n" + "\n".join(anom_descs))
        else:
            lines.append("No statistical anomalies detected; signal parameters conform to standard operational boundaries.")
            
        lines.append(
            f"Overall Signal Health Score is {health_score}/100 ({health_status}), assigning this file to {priority} PRIORITY for engineer triage."
        )
        
        return "\n\n".join(lines)
