import json
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import AnalysisRecord, AnalysisReport
from app.reports.pdf_generator import TechnicalReportGenerator
from app.signal_processing.io_loader import SignalLoader
from app.signal_processing.preprocessing import SignalPreprocessor

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/generate/{analysis_id}")
def generate_report(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
        
    sig_file = analysis.file
    params = json.loads(analysis.parameters_json) if analysis.parameters_json else {}
    fp = json.loads(analysis.fingerprint_json) if analysis.fingerprint_json else {}
    deltas = json.loads(analysis.what_changed_json) if analysis.what_changed_json else {}
    breakdown = json.loads(analysis.scoring_breakdown_json) if analysis.scoring_breakdown_json else []
    
    segments = [
        {
            "segment_index": s.segment_index,
            "start_time_sec": s.start_time_sec,
            "end_time_sec": s.end_time_sec,
            "duration_sec": s.duration_sec,
            "estimated_power_db": s.estimated_power_db,
            "snr_db": s.snr_db,
            "is_anomaly": s.is_anomaly
        }
        for s in analysis.segments
    ]
    
    anomalies = [
        {
            "severity": a.severity,
            "affected_parameter": a.affected_parameter,
            "observed_value": a.observed_value,
            "reason": a.reason
        }
        for a in analysis.anomalies
    ]
    
    raw_signal, _ = SignalLoader.load_file(
        file_path=sig_file.file_path,
        file_type=sig_file.file_type,
        sample_rate=sig_file.sample_rate,
        iq_format=sig_file.iq_format,
        max_samples=200000
    )
    processed_signal, _ = SignalPreprocessor.preprocess(raw_signal, sig_file.sample_rate)
    
    file_meta = {
        "id": sig_file.id,
        "filename": sig_file.filename,
        "file_type": sig_file.file_type,
        "sample_rate": sig_file.sample_rate,
        "num_samples": sig_file.num_samples,
        "duration_sec": sig_file.duration_sec
    }
    
    pdf_path = TechnicalReportGenerator.generate_pdf_report(
        file_meta=file_meta,
        extracted_params=params,
        fingerprint=fp,
        segments=segments,
        anomalies=anomalies,
        deltas=deltas,
        health_score=analysis.health_score,
        health_status=analysis.health_status,
        confidence_score=analysis.confidence_score,
        priority=analysis.analyst_priority,
        priority_reason=analysis.priority_reason or "",
        explainable_summary=analysis.explainable_summary or "",
        scoring_breakdown=breakdown,
        signal_data=processed_signal,
        sample_rate=sig_file.sample_rate
    )
    
    # Save Report Record
    report_rec = AnalysisReport(
        analysis_id=analysis.id,
        report_title=f"NTRO Signal Intel - {sig_file.filename}",
        report_pdf_path=pdf_path
    )
    db.add(report_rec)
    db.commit()
    db.refresh(report_rec)
    
    return {
        "status": "success",
        "report_id": report_rec.id,
        "pdf_filename": os.path.basename(pdf_path),
        "download_url": f"/api/reports/download/{report_rec.id}"
    }

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report or not os.path.exists(report.report_pdf_path):
        raise HTTPException(status_code=404, detail="Report PDF not found")
        
    return FileResponse(
        path=report.report_pdf_path,
        filename=os.path.basename(report.report_pdf_path),
        media_type="application/pdf"
    )

@router.get("/list")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(AnalysisReport).order_by(AnalysisReport.generated_at.desc()).all()
    return [
        {
            "id": r.id,
            "analysis_id": r.analysis_id,
            "filename": r.analysis.file.filename if r.analysis and r.analysis.file else "Unknown",
            "report_title": r.report_title,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            "download_url": f"/api/reports/download/{r.id}"
        }
        for r in reports
    ]
