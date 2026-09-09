export interface FileMetadata {
  id: number;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  sample_rate: number;
  num_samples: number;
  duration_sec: number;
  channels: number;
  is_complex: boolean;
  iq_format?: string;
  uploaded_at?: string;
  latest_analysis_id?: number;
  latest_health_score?: number;
  latest_priority?: string;
}

export interface MeasuredParameters {
  peak_frequency_hz: number;
  peak_frequency_str: string;
  spectral_centroid_hz: number;
  spectral_centroid_str: string;
  signal_power_db: number;
  estimated_noise_power_db: number;
  snr_db: number;
  peak_amplitude_v: number;
  rms_amplitude_v: number;
  duration_sec: number;
  sample_count: number;
  sample_rate_hz: number;
}

export interface DerivedParameters {
  bandwidth_3db_hz: number;
  bandwidth_3db_str: string;
  bandwidth_10db_hz: number;
  bandwidth_10db_str: string;
  occupied_bandwidth_99_hz: number;
  occupied_bandwidth_99_str: string;
  crest_factor_ratio: number;
  papr_db: number;
  signal_stability_index: number;
  frequency_drift_std_hz: number;
  phase_jitter_rad: number;
  spectral_flatness: number;
  spectral_spread_hz: number;
  spectral_rolloff_hz: number;
  spectral_kurtosis: number;
  spectral_skewness: number;
  modulation_type_hint: string;
  modulation_hint_confidence_pct: number;
}

export interface DominantPeak {
  rank: number;
  frequency_hz: number;
  frequency_str: string;
  power_db: number;
  relative_to_peak_db: number;
}

export interface ParameterSet {
  measured: MeasuredParameters;
  derived: DerivedParameters;
  dominant_peaks: DominantPeak[];
}

export interface SignalFingerprint {
  fingerprint_id: string;
  hash_signature: string;
  vector: number[];
  vector_labels: string[];
  visual_bars: {
    Frequency: number;
    Bandwidth: number;
    Power: number;
    SNR: number;
    Stability: number;
    "Spectral Spread": number;
  };
  metrics: {
    center_frequency_hz: number;
    bandwidth_hz: number;
    signal_power_db: number;
    snr_db: number;
    stability_index: number;
    crest_factor: number;
  };
}

export interface DeltaItem {
  parameter: string;
  unit: string;
  baseline_value: number;
  normal_range_str: string;
  current_value: number;
  delta_absolute: number;
  delta_pct: number;
  z_score: number;
  direction: 'INCREASE' | 'DECREASE' | 'STABLE';
  arrow: string;
  status: string;
  badge_color: 'green' | 'amber' | 'red';
  is_significant: boolean;
}

export interface WhatChangedResult {
  has_baseline: boolean;
  baseline_id?: number;
  baseline_name?: string;
  message?: string;
  sample_count?: number;
  deltas: DeltaItem[];
}

export interface SignalSegmentItem {
  id?: number;
  segment_index: number;
  start_time_sec: number;
  end_time_sec: number;
  duration_sec: number;
  estimated_power_db: number;
  center_frequency_hz?: number;
  bandwidth_hz?: number;
  snr_db?: number;
  is_anomaly: boolean;
  anomaly_reason?: string;
}

export interface SignalAnomalyItem {
  id?: number;
  analysis_id?: number;
  segment_index?: number;
  severity: 'NORMAL' | 'LOW' | 'WARNING' | 'HIGH' | 'CRITICAL';
  anomaly_score: number;
  affected_parameter: string;
  expected_range: string;
  observed_value: string;
  deviation_pct: number;
  reason: string;
  detected_at?: string;
  filename?: string;
  analyst_priority?: string;
}

export interface ScoringBreakdownItem {
  factor: string;
  impact: number;
  reason: string;
}

export interface AnalysisDetail {
  analysis_id: number;
  file: FileMetadata;
  analyzed_at: string;
  health_score: number;
  health_status: 'GOOD' | 'WARNING' | 'CRITICAL';
  confidence_score: number;
  analyst_priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priority_reason: string;
  explainable_summary: string;
  parameters: ParameterSet;
  fingerprint: SignalFingerprint;
  what_changed: WhatChangedResult;
  scoring_breakdown: ScoringBreakdownItem[];
  segments: SignalSegmentItem[];
  anomalies: SignalAnomalyItem[];
}

export interface VisualizationsData {
  waveform: {
    time: number[];
    is_complex: boolean;
    i_channel: number[];
    q_channel?: number[] | null;
    envelope: number[];
  };
  fft: {
    frequencies_hz: number[];
    frequencies_khz: number[];
    psd_db: number[];
  };
  spectrogram: {
    time_sec: number[];
    freq_khz: number[];
    power_mesh_db: number[][];
  };
  constellation?: {
    i: number[];
    q: number[];
  } | null;
}

export interface DashboardSummary {
  kpis: {
    total_files: number;
    total_analyses: number;
    total_segments: number;
    total_anomalies: number;
    good_signals: number;
    warning_signals: number;
    critical_signals: number;
    high_priority: number;
    med_priority: number;
    low_priority: number;
    avg_health_score: number;
    avg_confidence_score: number;
  };
  recent_analyses: {
    analysis_id: number;
    file_id: number;
    filename: string;
    file_type: string;
    health_score: number;
    health_status: 'GOOD' | 'WARNING' | 'CRITICAL';
    analyst_priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    confidence_score: number;
    anomalies_count: number;
    analyzed_at: string;
  }[];
  files: FileMetadata[];
}

export interface BaselineItem {
  id: number;
  name: string;
  description: string;
  signal_type: string;
  sample_rate: number;
  center_freq_mean: number;
  center_freq_std: number;
  bandwidth_mean: number;
  bandwidth_std: number;
  snr_mean: number;
  snr_std: number;
  power_mean: number;
  stability_mean: number;
  sample_count: number;
  fingerprint_template?: SignalFingerprint | null;
  updated_at?: string;
}
