import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import SignalFile, SignalBaseline
from app.signal_processing.synthetic_generator import SyntheticSignalGenerator
from app.signal_processing.io_loader import SignalLoader
from app.signal_processing.preprocessing import SignalPreprocessor
from app.signal_processing.extractor import ParameterExtractor
from app.signal_processing.fingerprint import SignalFingerprintEngine
from app.services.baseline_service import BaselineService

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

@router.post("/seed")
def seed_demo_signals(db: Session = Depends(get_db)):
    """Generates synthetic signals and seeds baseline for instant zero-config testing."""
    samples = SyntheticSignalGenerator.generate_all_samples()
    created_files = []
    
    for s in samples:
        existing = db.query(SignalFile).filter(SignalFile.filename == s["name"]).first()
        if not existing:
            raw_sig, meta = SignalLoader.load_file(
                file_path=s["file_path"],
                file_type=s["file_type"],
                sample_rate=s["sample_rate"],
                iq_format=s["iq_format"],
                max_samples=200000
            )
            
            db_file = SignalFile(
                filename=s["name"],
                file_type=s["file_type"],
                file_size_bytes=meta["file_size_bytes"],
                sample_rate=s["sample_rate"],
                num_samples=meta["num_samples"],
                duration_sec=meta["duration_sec"],
                channels=meta["channels"],
                is_complex=meta["is_complex"],
                iq_format=s["iq_format"],
                file_path=s["file_path"],
                is_demo=True
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            created_files.append(db_file.id)
            
            # If this is the nominal QPSK file, create baseline
            if s["name"] == "DEMO_SAT_QPSK_NOMINAL.iq":
                proc_sig, _ = SignalPreprocessor.preprocess(raw_sig, s["sample_rate"])
                params = ParameterExtractor.extract_all(proc_sig, s["sample_rate"])
                fp = SignalFingerprintEngine.generate_fingerprint(params, s["sample_rate"])
                BaselineService.create_or_update_baseline(
                    db=db,
                    name="SAT-QPSK-REF-BASELINE",
                    description="Nominal Reference Baseline for Space QPSK Downlink (80kHz)",
                    sample_rate=s["sample_rate"],
                    extracted_params=params,
                    fingerprint=fp,
                    signal_type="space_telemetry"
                )
                
    return {
        "status": "success",
        "message": "Demo signals and space telemetry baselines seeded successfully",
        "sample_count": len(samples)
    }

@router.get("/samples")
def list_demo_samples():
    samples = SyntheticSignalGenerator.generate_all_samples()
    return samples
