import React from 'react';
import { 
  FileAudio, 
  Layers, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  ArrowRight, 
  TrendingUp, 
  Play, 
  Sparkles 
} from 'lucide-react';
import { DashboardSummary } from '../types';
import { MetricCard } from '../components/MetricCard';

interface DashboardViewProps {
  summary: DashboardSummary | null;
  loading: boolean;
  onNavigateToAnalysis: (analysisId: number) => void;
  onNavigateToUpload: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  summary,
  loading,
  onNavigateToAnalysis,
  onNavigateToUpload
}) => {
  if (loading || !summary) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono text-xs">
        LOADING DASHBOARD METRICS...
      </div>
    );
  }

  const { kpis, recent_analyses, files } = summary;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-900 p-5 rounded-xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            Automated Telemetry Intelligence Overview
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time DSP parameter extraction, deterministic RF fingerprinting, and explainable anomaly detection for IQ/WAV space signals.
          </p>
        </div>
        <button
          onClick={onNavigateToUpload}
          className="self-start sm:self-auto px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all flex items-center space-x-2"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Upload & Analyze Signal</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <MetricCard
          label="Analyzed Files"
          value={kpis.total_files}
          sublabel="IQ & WAV files"
          icon={FileAudio}
          variant="cyan"
        />
        <MetricCard
          label="Active Segments"
          value={kpis.total_segments}
          sublabel="Detected Bursts"
          icon={Layers}
          variant="purple"
        />
        <MetricCard
          label="Avg Health Score"
          value={`${kpis.avg_health_score}/100`}
          sublabel="Overall Fleet Health"
          icon={Activity}
          variant={kpis.avg_health_score >= 80 ? 'emerald' : kpis.avg_health_score >= 55 ? 'amber' : 'rose'}
        />
        <MetricCard
          label="Avg Confidence"
          value={`${kpis.avg_confidence_score}%`}
          sublabel="DSP Quality Metric"
          icon={ShieldCheck}
          variant="cyan"
        />
        <MetricCard
          label="Active Anomalies"
          value={kpis.total_anomalies}
          sublabel="Detected Deviations"
          icon={AlertTriangle}
          variant={kpis.total_anomalies > 0 ? 'rose' : 'slate'}
        />
        <MetricCard
          label="High Priority"
          value={kpis.high_priority}
          sublabel="Requiring Triage"
          icon={TrendingUp}
          variant={kpis.high_priority > 0 ? 'rose' : 'slate'}
        />
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Analyses Queue (2 Cols) */}
        <div className="lg:col-span-2 telemetry-card space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white">Recent Signal Analyses</h3>
              <p className="text-[11px] text-slate-400">Processed telemetry files & analyst triage status</p>
            </div>
            <span className="text-xs font-mono text-slate-500">{recent_analyses.length} Records</span>
          </div>

          {recent_analyses.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs font-mono">
              No signal analyses executed yet. Click "Upload & Analyze" or "Load Demo Signals" above.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase font-sans">
                    <th className="pb-2 font-medium">Signal File</th>
                    <th className="pb-2 font-medium">Health Score</th>
                    <th className="pb-2 font-medium">Confidence</th>
                    <th className="pb-2 font-medium">Priority</th>
                    <th className="pb-2 font-medium">Anomalies</th>
                    <th className="pb-2 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {recent_analyses.map((item) => (
                    <tr key={item.analysis_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 text-slate-200 font-sans font-medium flex items-center gap-2">
                        <FileAudio className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span className="truncate max-w-[180px]">{item.filename}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-mono">
                          {item.file_type}
                        </span>
                      </td>
                      <td className="py-2.5">
                        <span className={`font-bold ${
                          item.health_status === 'GOOD'
                            ? 'text-emerald-400'
                            : item.health_status === 'WARNING'
                            ? 'text-amber-400'
                            : 'text-rose-400'
                        }`}>
                          {item.health_score.toFixed(0)} / 100
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-300">
                        {item.confidence_score.toFixed(1)}%
                      </td>
                      <td className="py-2.5">
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                          item.analyst_priority === 'HIGH' || item.analyst_priority === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : item.analyst_priority === 'MEDIUM'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}>
                          {item.analyst_priority}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-300">
                        {item.anomalies_count > 0 ? (
                          <span className="text-rose-400 font-bold">{item.anomalies_count} Issues</span>
                        ) : (
                          <span className="text-emerald-400">0 Nominal</span>
                        )}
                      </td>
                      <td className="py-2.5 text-right">
                        <button
                          onClick={() => onNavigateToAnalysis(item.analysis_id)}
                          className="px-2.5 py-1 rounded bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 border border-cyan-500/30 text-[11px] font-sans font-medium inline-flex items-center gap-1 transition-all"
                        >
                          Inspect <ArrowRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Signal Catalog & Quick Info (1 Col) */}
        <div className="telemetry-card space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white">Signal Catalog</h3>
            <p className="text-[11px] text-slate-400">Files available in local repository</p>
          </div>

          <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
            {files.map((f) => (
              <div
                key={f.id}
                className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-all flex items-center justify-between text-xs"
              >
                <div className="space-y-0.5 truncate pr-2">
                  <div className="font-semibold text-slate-200 truncate">{f.filename}</div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    {(f.sample_rate / 1e3).toFixed(1)} kSps • {f.duration_sec}s • {(f.file_size_bytes / 1024).toFixed(1)} KB
                  </div>
                </div>

                {f.latest_analysis_id ? (
                  <button
                    onClick={() => onNavigateToAnalysis(f.latest_analysis_id!)}
                    className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 font-mono text-[10px] shrink-0"
                  >
                    View #{f.latest_analysis_id}
                  </button>
                ) : (
                  <span className="text-[10px] text-slate-500 font-mono shrink-0">Unanalyzed</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
