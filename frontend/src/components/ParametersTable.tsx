import React, { useState } from 'react';
import { Sliders, Cpu, Radio, Award, Activity } from 'lucide-react';
import { ParameterSet } from '../types';

interface ParametersTableProps {
  parameters: ParameterSet;
}

export const ParametersTable: React.FC<ParametersTableProps> = ({ parameters }) => {
  const [tab, setTab] = useState<'measured' | 'derived' | 'peaks'>('measured');

  if (!parameters || !parameters.measured) {
    return (
      <div className="telemetry-card text-center py-6 text-slate-500 text-xs">
        No parameter extraction data available
      </div>
    );
  }

  const { measured, derived, dominant_peaks } = parameters;

  return (
    <div className="telemetry-card space-y-3">
      {/* Tab Selector */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setTab('measured')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              tab === 'measured'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400" /> Measured Parameters
          </button>
          <button
            onClick={() => setTab('derived')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              tab === 'derived'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-purple-400" /> Derived & Estimated
          </button>
          <button
            onClick={() => setTab('peaks')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              tab === 'peaks'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" /> Dominant Harmonics ({dominant_peaks?.length || 0})
          </button>
        </div>

        <span className="text-[10px] font-mono text-slate-500 uppercase">
          DSP EXTRACTION ENGINE
        </span>
      </div>

      {/* Measured Parameters Tab */}
      {tab === 'measured' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 font-mono text-xs">
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Peak Frequency</span>
            <span className="text-cyan-300 font-bold">{measured.peak_frequency_str}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Spectral Centroid</span>
            <span className="text-cyan-300 font-bold">{measured.spectral_centroid_str}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Signal Power</span>
            <span className="text-white font-bold">{measured.signal_power_db} dBFS</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Noise Floor Estimate</span>
            <span className="text-slate-300">{measured.estimated_noise_power_db} dBFS</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Signal-to-Noise Ratio (SNR)</span>
            <span className="text-emerald-400 font-bold">{measured.snr_db} dB</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Duration</span>
            <span className="text-white font-bold">{measured.duration_sec} s</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Peak Amplitude</span>
            <span className="text-white">{measured.peak_amplitude_v} V</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">RMS Amplitude</span>
            <span className="text-white">{measured.rms_amplitude_v} V</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Sample Rate</span>
            <span className="text-slate-300">{(measured.sample_rate_hz / 1e3).toFixed(1)} kSps</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Analyzed Samples</span>
            <span className="text-slate-300">{measured.sample_count?.toLocaleString()} pts</span>
          </div>
        </div>
      )}

      {/* Derived Parameters Tab */}
      {tab === 'derived' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 font-mono text-xs">
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Occupied Bandwidth (99% OBW)</span>
            <span className="text-purple-300 font-bold">{derived.occupied_bandwidth_99_str}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">-3 dB Bandwidth</span>
            <span className="text-purple-300 font-bold">{derived.bandwidth_3db_str}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">-10 dB Bandwidth</span>
            <span className="text-purple-300">{derived.bandwidth_10db_str}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Signal Stability Index</span>
            <span className="text-emerald-400 font-bold">{derived.signal_stability_index} / 1.0</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Crest Factor / PAPR</span>
            <span className="text-white">{derived.crest_factor_ratio} ({derived.papr_db} dB)</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Frequency Drift (Std)</span>
            <span className="text-amber-400">{derived.frequency_drift_std_hz} Hz</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Spectral Flatness (Entropy)</span>
            <span className="text-slate-300">{derived.spectral_flatness}</span>
          </div>
          <div className="p-2.5 bg-slate-900/50 rounded-lg border border-slate-800/60 flex items-center justify-between">
            <span className="text-slate-400 font-sans">Spectral Kurtosis / Skew</span>
            <span className="text-slate-300">{derived.spectral_kurtosis} / {derived.spectral_skewness}</span>
          </div>
          <div className="col-span-1 md:col-span-2 p-2.5 bg-gradient-to-r from-purple-950/40 to-slate-900/60 rounded-lg border border-purple-800/50 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Award className="w-4 h-4 text-purple-400" />
              <span className="text-slate-300 font-sans font-medium">Modulation Classification Hint</span>
            </div>
            <div className="flex items-center space-x-2 font-mono">
              <span className="text-white font-bold">{derived.modulation_type_hint}</span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-purple-900 text-purple-200 border border-purple-700">
                {derived.modulation_hint_confidence_pct}% Conf
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Dominant Peaks Tab */}
      {tab === 'peaks' && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="pb-2">Rank</th>
                <th className="pb-2">Frequency</th>
                <th className="pb-2">Power (dBFS)</th>
                <th className="pb-2">Relative to Peak</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(dominant_peaks || []).map((p) => (
                <tr key={p.rank} className="hover:bg-slate-800/30">
                  <td className="py-2 text-cyan-400 font-bold">#{p.rank}</td>
                  <td className="py-2 text-white font-semibold">{p.frequency_str}</td>
                  <td className="py-2 text-slate-300">{p.power_db} dB</td>
                  <td className="py-2 text-slate-400">{p.relative_to_peak_db > 0 ? `+${p.relative_to_peak_db}` : p.relative_to_peak_db} dB</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
