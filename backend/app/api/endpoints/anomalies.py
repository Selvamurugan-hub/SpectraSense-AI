from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.session import get_db
from app.database.models import SignalAnomaly, AnalysisRecord, SignalFile

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("")
def list_all_anomalies(
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(SignalAnomaly).join(AnalysisRecord).join(SignalFile).order_by(SignalAnomaly.detected_at.desc())
    if severity:
        query = query.filter(SignalAnomaly.severity == severity.upper())
        
    anomalies = query.limit(limit).all()
    results = []
    for a in anomalies:
        results.append({
            "id": a.id,
            "analysis_id": a.analysis_id,
            "filename": a.analysis.file.filename if a.analysis and a.analysis.file else "Unknown",
            "file_id": a.analysis.file_id if a.analysis else None,
            "segment_index": a.segment_index,
            "severity": a.severity,
            "anomaly_score": a.anomaly_score,
            "affected_parameter": a.affected_parameter,
            "expected_range": a.expected_range,
            "observed_value": a.observed_value,
            "deviation_pct": a.deviation_pct,
            "reason": a.reason,
            "analyst_priority": a.analysis.analyst_priority if a.analysis else "LOW",
            "detected_at": a.detected_at.isoformat() if a.detected_at else None
        })
    return results
