import pytest
import numpy as np
from app.signal_processing.preprocessing import SignalPreprocessor
from app.signal_processing.segmentation import SignalSegmenter
from app.signal_processing.extractor import ParameterExtractor
from app.signal_processing.fingerprint import SignalFingerprintEngine
from app.services.delta_service import DeltaService
from app.ml.anomaly_detector import SignalAnomalyDetector
from app.services.scoring_service import ScoringService

def test_preprocessing():
    fs = 10000.0
    t = np.arange(1000) / fs
    raw_sig = np.sin(2 * np.pi * 1000 * t) + 2.5 # DC offset 2.5
    processed, meta = SignalPreprocessor.preprocess(raw_sig, fs, remove_dc=True, normalize=True)
    assert abs(np.mean(processed)) < 1e-3
    assert np.max(np.abs(processed)) <= 1.0001
    assert meta["normalized"] == True

def test_parameter_extractor():
    fs = 48000.0
    t = np.arange(48000) / fs
    f0 = 5000.0
    sig = np.sin(2 * np.pi * f0 * t)
    extracted = ParameterExtractor.extract_all(sig, fs)
    
    assert "measured" in extracted
    assert "derived" in extracted
    # Peak frequency should be close to 5000 Hz
    assert abs(extracted["measured"]["peak_frequency_hz"] - 5000.0) < 100.0
    assert extracted["measured"]["snr_db"] > 10.0

def test_fingerprint_deterministic():
    fs = 48000.0
    t = np.arange(10000) / fs
    sig = np.sin(2 * np.pi * 3000 * t)
    ext1 = ParameterExtractor.extract_all(sig, fs)
    fp1 = SignalFingerprintEngine.generate_fingerprint(ext1, fs)
    
    ext2 = ParameterExtractor.extract_all(sig, fs)
    fp2 = SignalFingerprintEngine.generate_fingerprint(ext2, fs)
    
    assert fp1["hash_signature"] == fp2["hash_signature"]
    assert fp1["visual_bars"] == fp2["visual_bars"]

def test_segmentation():
    fs = 10000.0
    t = np.arange(20000) / fs
    sig = np.zeros(20000)
    # Add active burst from sample 2000 to 5000
    sig[2000:5000] = np.sin(2 * np.pi * 500 * t[2000:5000])
    segments = SignalSegmenter.segment_signal(sig, fs)
    assert len(segments) >= 1
