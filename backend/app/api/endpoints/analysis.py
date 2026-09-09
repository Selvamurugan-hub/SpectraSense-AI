import json
import numpy as np
from scipy import signal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.database.session import get_db
from app.database.models import SignalFile, AnalysisRecord, SignalSegment, SignalAnomaly, SignalBaseline
from app.signal_processing.io_loader import SignalLoader
from app.signal_processing.preprocessing import SignalPreprocessor
from app.signal_processing.segmentation import SignalSegmenter
from app.signal_processing.extractor import ParameterExtractor
from app.signal_processing.fingerprint import SignalFingerprintEngine
from app.services.baseline_service import BaselineService
from app.services.delta_service import DeltaService
from app.ml.anomaly_detector import SignalAnomalyDetector
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/run/{file_id}")
def run_signal_analysis(
    file_id: int,
    baseline_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    sig_file = db.query(SignalFile).filter(SignalFile.id == file_id).first()
    if not sig_file:
        raise HTTPException(status_code=404, detail="Signal file not found")
        
    # 1. Load Signal File
    try:
        raw_signal, meta = SignalLoader.load_file(
            file_path=sig_file.file_path,
            file_type=sig_file.file_type,
            sample_rate=sig_file.sample_rate,
            iq_format=sig_file.iq_format,
            max_samples=2000000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed loading signal file: {str(e)}")
        
    # 2. Preprocess Signal
    processed_signal, prep_meta = SignalPreprocessor.preprocess(
        raw_signal=raw_signal,
        sample_rate=sig_file.sample_rate,
        remove_dc=True,
        normalize=True
    )
    
    # 3. Segmentation
    segments_raw = SignalSegmenter.segment_signal(
        signal_data=processed_signal,
        sample_rate=sig_file.sample_rate
    )
    
    # 4. Parameter Extraction
    extracted_params = ParameterExtractor.extract_all(
        sig=processed_signal,
        sample_rate=sig_file.sample_rate
    )
    
    # 5. Signal Fingerprint
    fingerprint = SignalFingerprintEngine.generate_fingerprint(
        extracted_params=extracted_params,
        sample_rate=sig_file.sample_rate
    )
    
    # 6. Match / Retrieve Baseline
    if baseline_id:
        baseline = db.query(SignalBaseline).filter(SignalBaseline.id == baseline_id).first()
    else:
        baseline = BaselineService.get_or_match_baseline(
            db=db,
            center_freq_hz=extracted_params["measured"]["spectral_centroid_hz"],
            sample_rate=sig_file.sample_rate
        )
        
    # 7. "What Changed?" Delta Analysis
    deltas = DeltaService.compute_delta(
        extracted_params=extracted_params,
        baseline=baseline
    )
    
    # 8. Anomaly Detection
    anomalies_raw = SignalAnomalyDetector.detect_anomalies(
        extracted_params=extracted_params,
        segments=segments_raw,
        baseline=baseline
    )
    
    # 9. Confidence, Health Score, Analyst Priority & Summary
    conf_score = ScoringService.calculate_confidence_score(
        extracted_params=extracted_params,
        segments=segments_raw,
        num_samples=len(processed_signal)
    )
    
    health_score, health_status, breakdown = ScoringService.calculate_health_score(
        extracted_params=extracted_params,
        anomalies=anomalies_raw,
        baseline=baseline
    )
    
    priority, priority_reason = ScoringService.assign_analyst_priority(
        health_score=health_score,
        health_status=health_status,
        anomalies=anomalies_raw,
        confidence_score=conf_score
    )
    
    summary = ScoringService.generate_explainable_summary(
        filename=sig_file.filename,
        extracted_params=extracted_params,
        segments=segments_raw,
        anomalies=anomalies_raw,
        baseline=baseline,
        health_score=health_score,
        health_status=health_status,
        priority=priority
    )
    
    # 10. Persist to Database
    analysis = AnalysisRecord(
        file_id=sig_file.id,
        baseline_id=baseline.id if baseline else None,
        confidence_score=conf_score,
        health_score=health_score,
        health_status=health_status,
        analyst_priority=priority,
        priority_reason=priority_reason,
        explainable_summary=summary,
        parameters_json=json.dumps(extracted_params),
        fingerprint_json=json.dumps(fingerprint),
        what_changed_json=json.dumps(deltas),
        scoring_breakdown_json=json.dumps(breakdown)
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Save Segments
    for seg in segments_raw:
        # Check if segment has anomaly
        seg_anom = next((a for a in anomalies_raw if a.get("segment_index") == seg["segment_index"]), None)
        s_rec = SignalSegment(
            analysis_id=analysis.id,
            segment_index=seg["segment_index"],
            start_time_sec=seg["start_time_sec"],
            end_time_sec=seg["end_time_sec"],
            duration_sec=seg["duration_sec"],
            estimated_power_db=seg["estimated_power_db"],
            center_frequency_hz=extracted_params["measured"]["spectral_centroid_hz"],
            bandwidth_hz=extracted_params["derived"]["occupied_bandwidth_99_hz"],
            snr_db=seg.get("snr_estimate_db", extracted_params["measured"]["snr_db"]),
            is_anomaly=bool(seg_anom),
            anomaly_reason=seg_anom["reason"] if seg_anom else None,
            parameters_json=json.dumps(seg)
        )
        db.add(s_rec)
        
    # Save Anomalies
    for anom in anomalies_raw:
        a_rec = SignalAnomaly(
            analysis_id=analysis.id,
            segment_index=anom.get("segment_index"),
            anomaly_score=anom.get("anomaly_score", 0.5),
            severity=anom.get("severity", "WARNING"),
            affected_parameter=anom.get("affected_parameter", "General"),
            expected_range=anom.get("expected_range", ""),
            observed_value=anom.get("observed_value", ""),
            deviation_pct=anom.get("deviation_pct", 0.0),
            reason=anom.get("reason", "")
        )
        db.add(a_rec)
        
    db.commit()
    db.refresh(analysis)
    
    return {
        "status": "success",
        "analysis_id": analysis.id,
        "health_score": health_score,
        "health_status": health_status,
        "confidence_score": conf_score,
        "analyst_priority": priority,
        "priority_reason": priority_reason,
        "anomalies_count": len(anomalies_raw),
        "segments_count": len(segments_raw)
    }

@router.get("/{analysis_id}")
def get_analysis_details(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
        
    file_obj = analysis.file
    params = json.loads(analysis.parameters_json) if analysis.parameters_json else {}
    fp = json.loads(analysis.fingerprint_json) if analysis.fingerprint_json else {}
    deltas = json.loads(analysis.what_changed_json) if analysis.what_changed_json else {}
    breakdown = json.loads(analysis.scoring_breakdown_json) if analysis.scoring_breakdown_json else []
    
    segments = [
        {
            "id": s.id,
            "segment_index": s.segment_index,
            "start_time_sec": s.start_time_sec,
            "end_time_sec": s.end_time_sec,
            "duration_sec": s.duration_sec,
            "estimated_power_db": s.estimated_power_db,
            "center_frequency_hz": s.center_frequency_hz,
            "bandwidth_hz": s.bandwidth_hz,
            "snr_db": s.snr_db,
            "is_anomaly": s.is_anomaly,
            "anomaly_reason": s.anomaly_reason
        }
        for s in analysis.segments
    ]
    
    anomalies = [
        {
            "id": a.id,
            "segment_index": a.segment_index,
            "anomaly_score": a.anomaly_score,
            "severity": a.severity,
            "affected_parameter": a.affected_parameter,
            "expected_range": a.expected_range,
            "observed_value": a.observed_value,
            "deviation_pct": a.deviation_pct,
            "reason": a.reason,
            "detected_at": a.detected_at.isoformat() if a.detected_at else None
        }
        for a in analysis.anomalies
    ]
    
    return {
        "analysis_id": analysis.id,
        "file": {
            "id": file_obj.id,
            "filename": file_obj.filename,
            "file_type": file_obj.file_type,
            "sample_rate": file_obj.sample_rate,
            "num_samples": file_obj.num_samples,
            "duration_sec": file_obj.duration_sec,
            "is_complex": file_obj.is_complex,
            "channels": file_obj.channels,
            "iq_format": file_obj.iq_format
        },
        "analyzed_at": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
        "health_score": analysis.health_score,
        "health_status": analysis.health_status,
        "confidence_score": analysis.confidence_score,
        "analyst_priority": analysis.analyst_priority,
        "priority_reason": analysis.priority_reason,
        "explainable_summary": analysis.explainable_summary,
        "parameters": params,
        "fingerprint": fp,
        "what_changed": deltas,
        "scoring_breakdown": breakdown,
        "segments": segments,
        "anomalies": anomalies
    }

@router.get("/{analysis_id}/visualizations")
def get_signal_visualizations(
    analysis_id: int,
    segment_idx: Optional[int] = None,
    max_waveform_points: int = 1500,
    db: Session = Depends(get_db)
):
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
        
    sig_file = analysis.file
    try:
        raw_signal, _ = SignalLoader.load_file(
            file_path=sig_file.file_path,
            file_type=sig_file.file_type,
            sample_rate=sig_file.sample_rate,
            iq_format=sig_file.iq_format,
            max_samples=1000000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed loading signal: {str(e)}")
        
    processed_signal, _ = SignalPreprocessor.preprocess(
        raw_signal=raw_signal,
        sample_rate=sig_file.sample_rate,
        remove_dc=True,
        normalize=True
    )
    
    # Filter by segment if specified
    start_time_offset = 0.0
    if segment_idx is not None and segment_idx > 0:
        seg = db.query(SignalSegment).filter(
            SignalSegment.analysis_id == analysis_id,
            SignalSegment.segment_index == segment_idx
        ).first()
        if seg:
            st_idx = int(seg.start_time_sec * sig_file.sample_rate)
            end_idx = int(seg.end_time_sec * sig_file.sample_rate)
            processed_signal = processed_signal[st_idx:min(len(processed_signal), end_idx)]
            start_time_offset = seg.start_time_sec
            
    n_samples = len(processed_signal)
    if n_samples == 0:
        raise HTTPException(status_code=400, detail="Empty segment selected")
        
    fs = sig_file.sample_rate
    is_complex = np.iscomplexobj(processed_signal)
    
    # 1. Downsampled Waveform
    step = max(1, n_samples // max_waveform_points)
    sampled_indices = np.arange(0, n_samples, step)
    time_points = (sampled_indices / fs) + start_time_offset
    
    waveform_data = {
        "time": [round(float(t), 5) for t in time_points],
        "is_complex": is_complex,
        "i_channel": [round(float(processed_signal[i].real if is_complex else processed_signal[i]), 4) for i in sampled_indices],
        "q_channel": [round(float(processed_signal[i].imag), 4) for i in sampled_indices] if is_complex else None,
        "envelope": [round(float(np.abs(processed_signal[i])), 4) for i in sampled_indices]
    }
    
    # 2. FFT Power Spectral Density (Welch)
    nperseg = min(1024, 2 ** int(np.floor(np.log2(n_samples))))
    if nperseg < 32:
        nperseg = max(16, n_samples)
        
    if is_complex:
        f_welch, psd = signal.welch(processed_signal, fs=fs, window='hann', nperseg=nperseg, return_onesided=False)
        f_welch = np.fft.fftshift(f_welch)
        psd = np.fft.fftshift(psd)
    else:
        f_welch, psd = signal.welch(processed_signal, fs=fs, window='hann', nperseg=nperseg, return_onesided=True)
        
    psd_db = 10 * np.log10(psd + 1e-18)
    
    fft_data = {
        "frequencies_hz": [round(float(f), 1) for f in f_welch],
        "frequencies_khz": [round(float(f / 1e3), 3) for f in f_welch],
        "psd_db": [round(float(p), 2) for p in psd_db]
    }
    
    # 3. Spectrogram Matrix (STFT)
    stft_nperseg = min(256, 2 ** int(np.floor(np.log2(n_samples))))
    if stft_nperseg < 32:
        stft_nperseg = max(16, n_samples)
        
    sig_stft = np.abs(processed_signal) if is_complex else processed_signal
    f_spec, t_spec, sxx = signal.spectrogram(sig_stft, fs=fs, nperseg=stft_nperseg, noverlap=stft_nperseg // 2)
    sxx_db = 10 * np.log10(sxx + 1e-15)
    
    # Downsample spectrogram grid if too large
    max_t_bins = 60
    max_f_bins = 40
    if len(t_spec) > max_t_bins:
        t_step = len(t_spec) // max_t_bins
        t_spec = t_spec[::t_step]
        sxx_db = sxx_db[:, ::t_step]
    if len(f_spec) > max_f_bins:
        f_step = len(f_spec) // max_f_bins
        f_spec = f_spec[::f_step]
        sxx_db = sxx_db[::f_step, :]
        
    spectrogram_data = {
        "time_sec": [round(float(t + start_time_offset), 4) for t in t_spec],
        "freq_khz": [round(float(f / 1e3), 3) for f in f_spec],
        "power_mesh_db": [[round(float(val), 1) for val in row] for row in sxx_db]
    }
    
    # 4. Constellation Diagram (for Complex IQ)
    constellation_data = None
    if is_complex:
        const_samples = min(1000, len(processed_signal))
        idx_c = np.linspace(0, len(processed_signal) - 1, const_samples, dtype=int)
        constellation_data = {
            "i": [round(float(processed_signal[i].real), 4) for i in idx_c],
            "q": [round(float(processed_signal[i].imag), 4) for i in idx_c]
        }
        
    return {
        "waveform": waveform_data,
        "fft": fft_data,
        "spectrogram": spectrogram_data,
        "constellation": constellation_data
    }
