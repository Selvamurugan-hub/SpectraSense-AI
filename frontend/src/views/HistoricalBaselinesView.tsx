import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, Sliders, Activity, RefreshCw } from 'lucide-react';
import { BaselineItem } from '../types';
import { ApiService } from '../services/api';

export const HistoricalBaselinesView: React.FC = () => {
  const [baselines, setBaselines] = useState<BaselineItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBaselines();
  }, []);

  const fetchBaselines = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getBaselines();
      setBaselines(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this baseline profile?')) return;
    try {
      await ApiService.deleteBaseline(id);
      fetchBaselines();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" />
            Historical Baseline Profiles Library
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Reference parametric models & statistical envelopes for Spacecraft & Defense RF channels.
          </p>
        </div>
        <button
          onClick={fetchBaselines}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {baselines.length === 0 ? (
        <div className="telemetry-card text-center py-12 text-slate-400 space-y-3">
          <Database className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="text-sm font-semibold text-slate-300">No Historical Baselines Registered</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Baselines are automatically matched or manually created from nominal signal analyses. Click "Load Demo Signals" to seed the default satellite baseline.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {baselines.map((b) => (
            <div key={b.id} className="telemetry-card space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white font-mono">{b.name}</h3>
                    <p className="text-[11px] text-slate-400">{b.description || 'Reference RF Baseline'}</p>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                    {b.signal_type}
                  </span>
                </div>

                {/* Parametric Statistical Envelopes */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">CENTER FREQ (μ ± σ)</span>
                    <span className="text-cyan-300 font-bold">
                      {(b.center_freq_mean / 1e3).toFixed(2)} kHz
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      ± {(b.center_freq_std).toFixed(1)} Hz
                    </span>
                  </div>

                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">BANDWIDTH (99% OBW)</span>
                    <span className="text-purple-300 font-bold">
                      {(b.bandwidth_mean / 1e3).toFixed(2)} kHz
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      ± {(b.bandwidth_std).toFixed(1)} Hz
                    </span>
                  </div>

                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">NOMINAL SNR (μ)</span>
                    <span className="text-emerald-400 font-bold">
                      {b.snr_mean.toFixed(1)} dB
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      ± {b.snr_std.toFixed(1)} dB
                    </span>
                  </div>

                  <div className="p-2 rounded bg-slate-900/60 border border-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">SIGNAL STABILITY</span>
                    <span className="text-amber-400 font-bold">
                      {b.stability_mean.toFixed(3)}
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      Observed: {b.sample_count} runs
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono">
                <span>Updated: {b.updated_at?.slice(0, 10)}</span>
                <button
                  onClick={() => handleDelete(b.id)}
                  className="p-1 rounded text-slate-400 hover:text-rose-400 transition-colors"
                  title="Delete Baseline"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
