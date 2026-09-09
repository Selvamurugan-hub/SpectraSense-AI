import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, ArrowRight, Filter, RefreshCw, CheckCircle2 } from 'lucide-react';
import { SignalAnomalyItem } from '../types';
import { ApiService } from '../services/api';

interface AnomalyInvestigationViewProps {
  onNavigateToAnalysis: (analysisId: number) => void;
}

export const AnomalyInvestigationView: React.FC<AnomalyInvestigationViewProps> = ({
  onNavigateToAnalysis
}) => {
  const [anomalies, setAnomalies] = useState<SignalAnomalyItem[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchAnomalies();
  }, [severityFilter]);

  const fetchAnomalies = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getAnomalies(severityFilter || undefined);
      setAnomalies(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            Anomaly Investigation & Incident Triage Board
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Prioritized engineering incidents across statistical, RF drift, and Isolation Forest detections.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 p-1 rounded-lg text-xs font-mono">
            <button
              onClick={() => setSeverityFilter('')}
              className={`px-2.5 py-1 rounded transition-all ${
                severityFilter === '' ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              ALL
            </button>
            <button
              onClick={() => setSeverityFilter('CRITICAL')}
              className={`px-2.5 py-1 rounded transition-all ${
                severityFilter === 'CRITICAL' ? 'bg-rose-600 text-white font-bold' : 'text-rose-400 hover:bg-rose-950'
              }`}
            >
              CRITICAL
            </button>
            <button
              onClick={() => setSeverityFilter('HIGH')}
              className={`px-2.5 py-1 rounded transition-all ${
                severityFilter === 'HIGH' ? 'bg-orange-600 text-white font-bold' : 'text-orange-400 hover:bg-orange-950'
              }`}
            >
              HIGH
            </button>
            <button
              onClick={() => setSeverityFilter('WARNING')}
              className={`px-2.5 py-1 rounded transition-all ${
                severityFilter === 'WARNING' ? 'bg-amber-600 text-white font-bold' : 'text-amber-400 hover:bg-amber-950'
              }`}
            >
              WARNING
            </button>
          </div>

          <button
            onClick={fetchAnomalies}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-mono"
            title="Refresh"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Anomalies List */}
      {anomalies.length === 0 ? (
        <div className="telemetry-card text-center py-12 text-slate-400 space-y-3">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto" />
          <div className="text-sm font-semibold text-slate-200">No Anomalies Found</div>
          <p className="text-xs text-slate-500">All analyzed telemetry signals conform to standard baseline envelopes.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.map((anom) => {
            const isCritical = anom.severity === 'CRITICAL';
            const isHigh = anom.severity === 'HIGH';
            const isWarning = anom.severity === 'WARNING';

            const borderCol = isCritical
              ? 'border-rose-700/80 bg-rose-950/20'
              : isHigh
              ? 'border-orange-700/80 bg-orange-950/20'
              : 'border-amber-700/80 bg-amber-950/20';

            return (
              <div
                key={anom.id}
                className={`rounded-xl border p-4 shadow-md transition-all hover:border-slate-600 flex flex-col md:flex-row md:items-center justify-between gap-4 ${borderCol}`}
              >
                <div className="space-y-1.5 max-w-3xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase border ${
                      isCritical
                        ? 'bg-rose-950 text-rose-300 border-rose-800'
                        : isHigh
                        ? 'bg-orange-950 text-orange-300 border-orange-800'
                        : 'bg-amber-950 text-amber-300 border-amber-800'
                    }`}>
                      {anom.severity} ANOMALY
                    </span>

                    <span className="text-sm font-bold text-white font-mono">
                      {anom.affected_parameter}
                    </span>

                    {anom.filename && (
                      <span className="text-xs text-slate-400 font-sans">
                        in <b className="text-cyan-300">{anom.filename}</b>
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-300 font-sans leading-relaxed">
                    {anom.reason}
                  </p>

                  <div className="flex flex-wrap gap-4 text-[11px] font-mono text-slate-400 pt-1">
                    <div>Observed: <b className="text-white">{anom.observed_value}</b></div>
                    {anom.expected_range && <div>Expected: <b className="text-slate-300">{anom.expected_range}</b></div>}
                    <div>Deviation: <b className={anom.deviation_pct > 0 ? 'text-rose-400' : 'text-amber-400'}>{anom.deviation_pct > 0 ? `+${anom.deviation_pct}%` : `${anom.deviation_pct}%`}</b></div>
                  </div>
                </div>

                {anom.analysis_id && (
                  <button
                    onClick={() => onNavigateToAnalysis(anom.analysis_id!)}
                    className="self-start md:self-auto px-3.5 py-2 bg-slate-800 hover:bg-cyan-600 text-slate-200 hover:text-white rounded-lg text-xs font-mono font-semibold flex items-center space-x-1.5 shrink-0 transition-all"
                  >
                    <span>Investigate</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
