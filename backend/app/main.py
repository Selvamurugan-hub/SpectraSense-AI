import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, REPORT_DIR
from app.database.session import engine, Base, SessionLocal
from app.database.models import SignalFile, SignalBaseline
from app.api.endpoints import upload, analysis, baselines, anomalies, reports, demo, dashboard
from app.signal_processing.synthetic_generator import SyntheticSignalGenerator
from app.signal_processing.io_loader import SignalLoader
from app.signal_processing.preprocessing import SignalPreprocessor
from app.signal_processing.extractor import ParameterExtractor
from app.signal_processing.fingerprint import SignalFingerprintEngine
from app.services.baseline_service import BaselineService

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automated model for analysis of .IQ and .wav files along with signal parameter extraction (NTRO / SIH 2026 PS ID: 26147)",
    version="1.0.0"
)

# Enable CORS for Frontend Development and Production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(baselines.router, prefix=settings.API_V1_STR)
app.include_router(anomalies.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(demo.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_populate_demo():
    """Auto-seed sample data on startup for immediate out-of-the-box readiness."""
    db = SessionLocal()
    try:
        if db.query(SignalFile).count() == 0:
            samples = SyntheticSignalGenerator.generate_all_samples()
            for s in samples:
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
                
                # Seed nominal baseline for space telemetry
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
    except Exception as e:
        print(f"Startup demo seed warning: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "NTRO Signal Analysis Assistant",
        "ps_id": "26147",
        "theme": "Space Technology",
        "docs_url": "/docs"
    }
