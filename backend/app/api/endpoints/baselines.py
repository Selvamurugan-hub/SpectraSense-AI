import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database.session import get_db
from app.database.models import SignalBaseline, AnalysisRecord
from app.services.baseline_service import BaselineService

router = APIRouter(prefix="/baselines", tags=["Baselines"])

class BaselineCreateReq(BaseModel):
    name: str
    description: Optional[str] = "Historical Reference Baseline"
    analysis_id: int
    signal_type: Optional[str] = "space_telemetry"

@router.get("")
def list_baselines(db: Session = Depends(get_db)):
    baselines = db.query(SignalBaseline).order_by(SignalBaseline.updated_at.desc()).all()
    results = []
    for b in baselines:
        results.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "signal_type": b.signal_type,
            "sample_rate": b.sample_rate,
            "center_freq_mean": b.center_freq_mean,
            "center_freq_std": b.center_freq_std,
            "bandwidth_mean": b.bandwidth_mean,
            "bandwidth_std": b.bandwidth_std,
            "snr_mean": b.snr_mean,
            "snr_std": b.snr_std,
            "power_mean": b.power_mean,
            "stability_mean": b.stability_mean,
            "sample_count": b.sample_count,
            "fingerprint_template": json.loads(b.fingerprint_template) if b.fingerprint_template else None,
            "updated_at": b.updated_at.isoformat() if b.updated_at else None
        })
    return results

@router.post("/create-from-analysis")
def create_baseline_from_analysis(req: BaselineCreateReq, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
        
    params = json.loads(analysis.parameters_json) if analysis.parameters_json else None
    fp = json.loads(analysis.fingerprint_json) if analysis.fingerprint_json else None
    
    if not params or not fp:
        raise HTTPException(status_code=400, detail="Incomplete analysis data to build baseline")
        
    baseline = BaselineService.create_or_update_baseline(
        db=db,
        name=req.name,
        description=req.description or "Historical Baseline Reference",
        sample_rate=analysis.file.sample_rate,
        extracted_params=params,
        fingerprint=fp,
        signal_type=req.signal_type or "space_telemetry"
    )
    
    return {
        "status": "success",
        "message": f"Baseline '{baseline.name}' registered successfully",
        "baseline_id": baseline.id
    }

@router.delete("/{baseline_id}")
def delete_baseline(baseline_id: int, db: Session = Depends(get_db)):
    baseline = db.query(SignalBaseline).filter(SignalBaseline.id == baseline_id).first()
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
    db.delete(baseline)
    db.commit()
    return {"status": "success", "message": "Baseline deleted"}
