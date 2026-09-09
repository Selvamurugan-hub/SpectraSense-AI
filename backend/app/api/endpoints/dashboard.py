import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.database.models import SignalFile, AnalysisRecord, SignalSegment, SignalAnomaly

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_files = db.query(SignalFile).count()
    total_analyses = db.query(AnalysisRecord).count()
    total_segments = db.query(SignalSegment).count()
    total_anomalies = db.query(SignalAnomaly).count()
    
    # Health status counts
    good_signals = db.query(AnalysisRecord).filter(AnalysisRecord.health_status == "GOOD").count()
    warning_signals = db.query(AnalysisRecord).filter(AnalysisRecord.health_status == "WARNING").count()
    critical_signals = db.query(AnalysisRecord).filter(AnalysisRecord.health_status == "CRITICAL").count()
    
    # Priority counts
    high_priority = db.query(AnalysisRecord).filter(AnalysisRecord.analyst_priority == "HIGH").count()
    med_priority = db.query(AnalysisRecord).filter(AnalysisRecord.analyst_priority == "MEDIUM").count()
    low_priority = db.query(AnalysisRecord).filter(AnalysisRecord.analyst_priority == "LOW").count()
    
    # Average health score
    avg_health = db.query(func.avg(AnalysisRecord.health_score)).scalar() or 100.0
    avg_confidence = db.query(func.avg(AnalysisRecord.confidence_score)).scalar() or 0.0
    
    # Recent analyses
    recent = db.query(AnalysisRecord).order_by(AnalysisRecord.analyzed_at.desc()).limit(10).all()
    recent_list = []
    for r in recent:
        recent_list.append({
            "analysis_id": r.id,
            "file_id": r.file_id,
            "filename": r.file.filename if r.file else "Unknown",
            "file_type": r.file.file_type if r.file else "N/A",
            "health_score": r.health_score,
            "health_status": r.health_status,
            "analyst_priority": r.analyst_priority,
            "confidence_score": r.confidence_score,
            "anomalies_count": len(r.anomalies),
            "analyzed_at": r.analyzed_at.isoformat() if r.analyzed_at else None
        })
        
    # File catalog
    files = db.query(SignalFile).order_by(SignalFile.uploaded_at.desc()).limit(20).all()
    files_list = []
    for f in files:
        latest_analysis = db.query(AnalysisRecord).filter(AnalysisRecord.file_id == f.id).order_by(AnalysisRecord.analyzed_at.desc()).first()
        files_list.append({
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size_bytes": f.file_size_bytes,
            "sample_rate": f.sample_rate,
            "duration_sec": f.duration_sec,
            "is_complex": f.is_complex,
            "is_demo": f.is_demo,
            "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
            "latest_analysis_id": latest_analysis.id if latest_analysis else None,
            "latest_health_score": latest_analysis.health_score if latest_analysis else None,
            "latest_priority": latest_analysis.analyst_priority if latest_analysis else None
        })
        
    return {
        "kpis": {
            "total_files": total_files,
            "total_analyses": total_analyses,
            "total_segments": total_segments,
            "total_anomalies": total_anomalies,
            "good_signals": good_signals,
            "warning_signals": warning_signals,
            "critical_signals": critical_signals,
            "high_priority": high_priority,
            "med_priority": med_priority,
            "low_priority": low_priority,
            "avg_health_score": round(float(avg_health), 1),
            "avg_confidence_score": round(float(avg_confidence), 1)
        },
        "recent_analyses": recent_list,
        "files": files_list
    }
