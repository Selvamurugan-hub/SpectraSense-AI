import React, { useState } from 'react';
import { Fingerprint, Copy, Check, Hash, Cpu } from 'lucide-react';
import { SignalFingerprint } from '../types';

interface FingerprintVisualizerProps {
  fingerprint: SignalFingerprint;
}

export const FingerprintVisualizer: React.FC<FingerprintVisualizerProps> = ({ fingerprint }) => {
  const [copied, setCopied] = useState(false);

  if (!fingerprint) {
    return (
      <div className="telemetry-card text-center py-6 text-slate-500 text-xs">
        No fingerprint data available
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(fingerprint.fingerprint_id || fingerprint.hash_signature);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const barColors: Record<string, string> = {
    Frequency: 'from-cyan-500 to-blue-500',
    Bandwidth: 'from-blue-500 to-indigo-500',
    Power: 'from-purple-500 to-pink-500',
    SNR: 'from-emerald-500 to-teal-500',
    Stability: 'from-amber-500 to-orange-500',
    'Spectral Spread': 'from-rose-500 to-red-500'
  };

  return (
    <div className="telemetry-card space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-md bg-cyan-950 border border-cyan-800 text-cyan-400">
            <Fingerprint className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">Deterministic Signal Fingerprint</h3>
            <p className="text-[11px] text-slate-400">Multi-domain normalized RF signature</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs px-2.5 py-1 bg-slate-900 border border-slate-700 text-cyan-300 rounded font-semibold flex items-center gap-1.5">
            <Hash className="w-3 h-3 text-cyan-400" />
            {fingerprint.fingerprint_id}
          </span>
          <button
            onClick={handleCopy}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-all text-xs"
            title="Copy Signature Hash"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Visual Bar Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {Object.entries(fingerprint.visual_bars || {}).map(([key, val]) => {
          const colorClass = barColors[key] || 'from-cyan-500 to-blue-500';
          return (
            <div key={key} className="space-y-1.5 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/60">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium">{key}</span>
                <span className="font-mono text-slate-200 font-semibold">{val}%</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden p-0.5">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${colorClass} transition-all duration-500`}
                  style={{ width: `${Math.max(4, val)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Underlying Vector Preview */}
      <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1.5">
          <span className="flex items-center gap-1">
            <Cpu className="w-3 h-3 text-slate-400" />
            NUMERICAL FEATURE VECTOR
          </span>
          <span className="text-slate-500">7-DIMENSIONAL</span>
        </div>
        <div className="font-mono text-xs text-cyan-300 break-all bg-slate-900/80 px-2.5 py-1.5 rounded border border-slate-800">
          [{fingerprint.vector ? fingerprint.vector.join(', ') : ''}]
        </div>
      </div>
    </div>
  );
};
