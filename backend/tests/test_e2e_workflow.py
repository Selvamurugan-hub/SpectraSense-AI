import os
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.models import SignalFile, AnalysisRecord, SignalBaseline, SignalAnomaly, AnalysisReport

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["system"] == "NTRO Signal Analysis Assistant"
    assert data["ps_id"] == "26147"

def test_demo_seed_and_samples():
    res = client.post("/api/demo/seed")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["sample_count"] >= 4

    samples_res = client.get("/api/demo/samples")
    assert samples_res.status_code == 200
    samples = samples_res.json()
    assert len(samples) >= 4

def test_full_analysis_workflow():
    # 1. Seed demo signals
    client.post("/api/demo/seed")
    
    # 2. Get dashboard to find file id
    dash_res = client.get("/api/dashboard/summary")
    assert dash_res.status_code == 200
    files = dash_res.json()["files"]
    assert len(files) > 0
    
    # Pick nominal QPSK file
    nom_file = next(f for f in files if "NOMINAL" in f["filename"])
    
    # 3. Run Analysis
    analysis_res = client.post(f"/api/analysis/run/{nom_file['id']}")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    analysis_id = analysis_data["analysis_id"]
    assert analysis_data["health_score"] >= 80.0
    assert analysis_data["health_status"] == "GOOD"
    
    # 4. Fetch Analysis Details
    detail_res = client.get(f"/api/analysis/{analysis_id}")
    assert detail_res.status_code == 200
    details = detail_res.json()
    assert "parameters" in details
    assert "fingerprint" in details
    assert "what_changed" in details
    assert len(details["fingerprint"]["vector"]) == 7
    
    # 5. Fetch Visualizations
    viz_res = client.get(f"/api/analysis/{analysis_id}/visualizations")
    assert viz_res.status_code == 200
    viz = viz_res.json()
    assert "waveform" in viz
    assert "fft" in viz
    assert "spectrogram" in viz
    assert len(viz["waveform"]["time"]) > 0
    
    # 6. Test Degraded Signal Analysis (Should detect anomalies & "What Changed?" deltas)
    deg_file = next(f for f in files if "DEGRADED" in f["filename"])
    deg_res = client.post(f"/api/analysis/run/{deg_file['id']}")
    assert deg_res.status_code == 200
    deg_data = deg_res.json()
    
    deg_details = client.get(f"/api/analysis/{deg_data['analysis_id']}").json()
    assert len(deg_details["anomalies"]) > 0
    assert deg_details["what_changed"]["has_baseline"] == True
    
    # 7. Generate PDF Report
    report_res = client.post(f"/api/reports/generate/{deg_data['analysis_id']}")
    assert report_res.status_code == 200
    rep_data = report_res.json()
    assert "report_id" in rep_data
    assert "download_url" in rep_data
    
    # 8. Download PDF
    dl_res = client.get(rep_data["download_url"])
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000
