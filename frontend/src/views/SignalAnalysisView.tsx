import React, { useState, useEffect } from 'react';
import { 
  FileAudio, 
  FileText, 
  RefreshCw, 
  Download, 
  Layers, 
  Cpu, 
  AlertTriangle, 
  CheckCircle2, 
  Sparkles, 
  Database,
  ArrowRight
} from 'lucide-react';
import { AnalysisDetail, VisualizationsData } from '../types';
import { ApiService } from '../services/api';
import { SignalCharts } from '../components/SignalCharts';
import { ParametersTable } from '../components/ParametersTable';
import { FingerprintVisualizer } from '../components/FingerprintVisualizer';
import { WhatChangedTable } from '../components/WhatChangedTable';
import { SegmentInspector } from '../components/SegmentInspector';
import { HealthScoreCard } from '../components/HealthScoreCard';

interface SignalAnalysisViewProps {
  analysisId: number;
  onNavigateToReports?: () => void;
}

export const SignalAnalysisView: React.FC<SignalAnalysisViewProps> = ({
  analysisId,
  onNavigateToReports
}) => {
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [vizData, setVizData] = useState<VisualizationsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedSegmentIdx, setSelectedSegmentIdx] = useState<number | null>(null);
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);
  const [reportSuccessMsg, setReportSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysisData();
  }, [analysisId]);

  useEffect(() => {
    loadVisualizations(selectedSegmentIdx);
  }, [analysisId, selectedSegmentIdx]);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getAnalysisDetails(analysisId);
      setDetail(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadVisualizations = async (segIdx: number | null) => {
    try {
      const vData = await ApiService.getVisualizations(analysisId, segIdx || undefined);
      setVizData(vData);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGeneratePdf = async () => {
    try {
      setGeneratingReport(true);
      setReportSuccessMsg(null);
      const res = await ApiService.generateReport(analysisId);
      setReportSuccessMsg(res.pdf_filename);
      // Automatically trigger download
      window.open(`http://localhost:8000${res.download_url}`, '_blank');
    } catch (e: any) {
      alert(`Report generation error: ${e.message}`);
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading || !detail) {
    return (
      <div className="telemetry-card h-[500px] flex flex-col items-center justify-center space-y-3 text-slate-400 font-mono text-xs">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p>LOADING COMPLETE SIGNAL ANALYSIS & DSP TELEMETRY #{analysisId}...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Telemetry Header */}
      <div className="bg-[#0F172A] p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400">
            <FileAudio className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white tracking-tight font-mono">
                {detail.file.filename}
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-400 uppercase font-mono font-bold border border-slate-700">
                {detail.file.file_type}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Fs: {(detail.file.sample_rate / 1e3).toFixed(1)} kSps • Samples: {detail.file.num_samples?.toLocaleString()} • Duration: {detail.file.duration_sec}s • Analyzed: {detail.analyzed_at?.replace('T', ' ').slice(0, 19)} UTC
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleGeneratePdf}
            disabled={generatingReport}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center space-x-2 transition-all active:scale-95 disabled:opacity-50"
          >
            {generatingReport ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Download className="w-3.5 h-3.5" />
            )}
            <span>{generatingReport ? 'Compiling PDF...' : 'Download Technical PDF Report'}</span>
          </button>
        </div>
      </div>

      {reportSuccessMsg && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-800 rounded-lg text-emerald-300 text-xs flex items-center justify-between font-mono">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Technical PDF Report Generated: <b>{reportSuccessMsg}</b>
          </span>
          {onNavigateToReports && (
            <button onClick={onNavigateToReports} className="text-emerald-400 hover:underline">
              View in Reports Center →
            </button>
          )}
        </div>
      )}

      {/* 1. Health Score, Confidence, Analyst Priority Breakdown */}
      <HealthScoreCard
        healthScore={detail.health_score}
        healthStatus={detail.health_status}
        confidenceScore={detail.confidence_score}
        analystPriority={detail.analyst_priority}
        priorityReason={detail.priority_reason}
        scoringBreakdown={detail.scoring_breakdown}
      />

      {/* 2. Automatic Signal Segmentation Ribbon */}
      <SegmentInspector
        segments={detail.segments}
        selectedSegmentIdx={selectedSegmentIdx}
        onSelectSegment={setSelectedSegmentIdx}
      />

      {/* 3. Interactive Plotly Signal Visualizations (Waveform, FFT, Spectrogram, Constellation) */}
      <SignalCharts
        data={vizData}
        loading={!vizData}
        onRefresh={() => loadVisualizations(selectedSegmentIdx)}
      />

      {/* 4. Two-Column Split: Parameters vs Fingerprint & Delta */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Measured & Derived Parameters */}
        <div className="space-y-6">
          <ParametersTable parameters={detail.parameters} />
          <FingerprintVisualizer fingerprint={detail.fingerprint} />
        </div>

        {/* Right Column: "What Changed?" Baseline Delta & Explainable Summary */}
        <div className="space-y-6">
          <WhatChangedTable
            whatChanged={detail.what_changed}
            analysisId={detail.analysis_id}
            onBaselineCreated={loadAnalysisData}
          />

          {/* Explainable Engineering Narrative */}
          <div className="telemetry-card space-y-3">
            <div className="flex items-center space-x-2 border-b border-slate-800 pb-2.5">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Explainable Engineering Summary</h3>
            </div>
            <div className="text-xs text-slate-300 leading-relaxed space-y-2 bg-slate-900/60 p-3.5 rounded-lg border border-slate-800/80 font-sans">
              {detail.explainable_summary.split('\n\n').map((para, i) => (
                <p key={i}>{para}</p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
