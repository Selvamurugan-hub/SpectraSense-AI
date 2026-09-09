import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR
from app.database.session import get_db
from app.database.models import SignalFile
from app.signal_processing.io_loader import SignalLoader

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("")
async def upload_signal_file(
    file: UploadFile = File(...),
    file_type: str = Form(None),
    sample_rate: float = Form(None),
    iq_format: str = Form("float32"),
    center_freq_hz: float = Form(0.0),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "iq"
    if not file_type:
        file_type = ext
        
    saved_filename = f"{Path(file.filename).stem}_{os.urandom(4).hex()}.{ext}"
    saved_path = UPLOAD_DIR / saved_filename
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Validate and inspect signal file
    try:
        raw_sig, meta = SignalLoader.load_file(
            file_path=str(saved_path),
            file_type=file_type,
            sample_rate=sample_rate,
            iq_format=iq_format,
            center_freq=center_freq_hz,
            max_samples=100000
        )
    except Exception as e:
        if saved_path.exists():
            os.remove(saved_path)
        raise HTTPException(status_code=400, detail=f"File validation failed: {str(e)}")
        
    # Store in database
    db_file = SignalFile(
        filename=file.filename,
        file_type=meta["file_type"],
        file_size_bytes=meta["file_size_bytes"],
        sample_rate=meta["sample_rate"],
        num_samples=meta["num_samples"],
        duration_sec=meta["duration_sec"],
        channels=meta["channels"],
        is_complex=meta["is_complex"],
        iq_format=meta["iq_format"],
        file_path=str(saved_path),
        is_demo=False
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {
        "status": "success",
        "message": "File uploaded and validated successfully",
        "file_id": db_file.id,
        "metadata": {
            "id": db_file.id,
            "filename": db_file.filename,
            "file_type": db_file.file_type,
            "file_size_bytes": db_file.file_size_bytes,
            "sample_rate": db_file.sample_rate,
            "num_samples": db_file.num_samples,
            "duration_sec": db_file.duration_sec,
            "channels": db_file.channels,
            "is_complex": db_file.is_complex,
            "iq_format": db_file.iq_format,
            "uploaded_at": db_file.uploaded_at.isoformat() if db_file.uploaded_at else None
        }
    }
