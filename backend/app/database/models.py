import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class SignalFile(Base):
    __tablename__ = "signal_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # wav, iq, raw, bin
    file_size_bytes = Column(Integer, nullable=False)
    sample_rate = Column(Float, nullable=False)
    num_samples = Column(Integer, nullable=False)
    duration_sec = Column(Float, nullable=False)
    channels = Column(Integer, default=1)
    is_complex = Column(Boolean, default=False)
    iq_format = Column(String(50), default="float32")  # float32, int16, int8
    file_path = Column(String(500), nullable=False)
    is_demo = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analyses = relationship("AnalysisRecord", back_populates="file", cascade="all, delete-orphan")


class SignalBaseline(Base):
    __tablename__ = "signal_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    signal_type = Column(String(50), default="telemetry")
    sample_rate = Column(Float, nullable=False)
    
    # Statistical bands (mean, std, min, max)
    center_freq_mean = Column(Float, default=0.0)
    center_freq_std = Column(Float, default=0.0)
    bandwidth_mean = Column(Float, default=0.0)
    bandwidth_std = Column(Float, default=0.0)
    power_mean = Column(Float, default=0.0)
    power_std = Column(Float, default=0.0)
    snr_mean = Column(Float, default=0.0)
    snr_std = Column(Float, default=0.0)
    stability_mean = Column(Float, default=1.0)
    stability_std = Column(Float, default=0.0)
    rms_mean = Column(Float, default=0.0)
    rms_std = Column(Float, default=0.0)
    
    sample_count = Column(Integer, default=1)
    fingerprint_template = Column(Text, nullable=True)  # JSON representation
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    analyses = relationship("AnalysisRecord", back_populates="baseline")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("signal_files.id"), nullable=False)
    baseline_id = Column(Integer, ForeignKey("signal_baselines.id"), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    confidence_score = Column(Float, default=0.0)   # 0 to 100%
    health_score = Column(Float, default=100.0)      # 0 to 100
    health_status = Column(String(20), default="GOOD")  # GOOD, WARNING, CRITICAL
    analyst_priority = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    priority_reason = Column(Text, nullable=True)
    explainable_summary = Column(Text, nullable=True)
    
    # JSON payload fields
    parameters_json = Column(Text, nullable=True)
    fingerprint_json = Column(Text, nullable=True)
    what_changed_json = Column(Text, nullable=True)
    scoring_breakdown_json = Column(Text, nullable=True)
    
    file = relationship("SignalFile", back_populates="analyses")
    baseline = relationship("SignalBaseline", back_populates="analyses")
    segments = relationship("SignalSegment", back_populates="analysis", cascade="all, delete-orphan")
    anomalies = relationship("SignalAnomaly", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("AnalysisReport", back_populates="analysis", cascade="all, delete-orphan")


class SignalSegment(Base):
    __tablename__ = "signal_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id"), nullable=False)
    segment_index = Column(Integer, nullable=False)
    start_time_sec = Column(Float, nullable=False)
    end_time_sec = Column(Float, nullable=False)
    duration_sec = Column(Float, nullable=False)
    estimated_power_db = Column(Float, default=0.0)
    center_frequency_hz = Column(Float, default=0.0)
    bandwidth_hz = Column(Float, default=0.0)
    snr_db = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(String(255), nullable=True)
    parameters_json = Column(Text, nullable=True)
    
    analysis = relationship("AnalysisRecord", back_populates="segments")


class SignalAnomaly(Base):
    __tablename__ = "signal_anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id"), nullable=False)
    segment_index = Column(Integer, nullable=True)
    anomaly_score = Column(Float, default=0.0)
    severity = Column(String(20), default="WARNING")  # NORMAL, LOW, WARNING, HIGH, CRITICAL
    affected_parameter = Column(String(100), nullable=False)
    expected_range = Column(String(100), nullable=True)
    observed_value = Column(String(100), nullable=False)
    deviation_pct = Column(Float, default=0.0)
    reason = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analysis = relationship("AnalysisRecord", back_populates="anomalies")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id"), nullable=False)
    report_title = Column(String(255), nullable=False)
    report_pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analysis = relationship("AnalysisRecord", back_populates="reports")
