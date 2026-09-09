import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, GitCompare, PlusCircle, Database, CheckCircle2 } from 'lucide-react';
import { WhatChangedResult } from '../types';
import { ApiService } from '../services/api';

interface WhatChangedTableProps {
  whatChanged: WhatChangedResult;
  analysisId: number;
  onBaselineCreated?: () => void;
}

export const WhatChangedTable: React.FC<WhatChangedTableProps> = ({
  whatChanged,
  analysisId,
  onBaselineCreated
}) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [baselineName, setBaselineName] = useState('');
  const [baselineDesc, setBaselineDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [createdMsg, setCreatedMsg] = useState(false);

  const handleCreateBaseline = async () => {
    if (!baselineName.trim()) return;
    try {
      setCreating(true);
      await ApiService.createBaseline(baselineName, baselineDesc, analysisId);
      setCreatedMsg(true);
      setShowCreateModal(false);
      if (onBaselineCreated) onBaselineCreated();
      setTimeout(() => setCreatedMsg(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  if (!whatChanged || !whatChanged.has_baseline) {
    return (
      <div className="telemetry-card border-dashed border-slate-700 bg-slate-900/30 text-center py-6 px-4 space-y-3">
        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
          <Database className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-200">No Historical Baseline Available</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
            This signal frequency band has not been linked to a reference baseline yet. You can promote this signal as the baseline reference profile.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Register as Historical Baseline</span>
        </button>

        {showCreateModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 max-w-md w-full space-y-4 text-left shadow-2xl">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                Register Historical Baseline
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Baseline Name</label>
                  <input
                    type="text"
                    value={baselineName}
                    onChange={(e) => setBaselineName(e.target.value)}
                    placeholder="e.g. S-BAND-TELEMETRY-NOMINAL"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Description</label>
                  <input
                    type="text"
                    value={baselineDesc}
                    onChange={(e) => setBaselineDesc(e.target.value)}
                    placeholder="e.g. Reference profile for Spacecraft Downlink"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateBaseline}
                  disabled={creating || !baselineName.trim()}
                  className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold disabled:opacity-50"
                >
                  {creating ? 'Saving...' : 'Confirm Registration'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="telemetry-card space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded bg-blue-950 border border-blue-800 text-blue-400">
            <GitCompare className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              WHAT CHANGED?
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono font-normal">
                Ref: {whatChanged.baseline_name}
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Comparative delta against historical baseline ({whatChanged.sample_count} prior observation(s))
            </p>
          </div>
        </div>

        {createdMsg && (
          <span className="text-xs text-emerald-400 flex items-center gap-1 font-mono">
            <CheckCircle2 className="w-3.5 h-3.5" /> Baseline Updated
          </span>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase">
              <th className="pb-2 font-medium">Parameter</th>
              <th className="pb-2 font-medium">Normal Baseline</th>
              <th className="pb-2 font-medium">Current Value</th>
              <th className="pb-2 font-medium text-center">Direction</th>
              <th className="pb-2 font-medium text-right">Delta (%)</th>
              <th className="pb-2 font-medium text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {whatChanged.deltas.map((d, i) => {
              const isGreen = d.badge_color === 'green';
              const isAmber = d.badge_color === 'amber';
              const isRed = d.badge_color === 'red';

              return (
                <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 text-slate-200 font-sans font-medium">{d.parameter}</td>
                  <td className="py-2.5 text-slate-400 text-[11px]">
                    {d.baseline_value} {d.unit}
                    <span className="block text-[10px] text-slate-500">{d.normal_range_str}</span>
                  </td>
                  <td className="py-2.5 text-white font-semibold">
                    {d.current_value} {d.unit}
                  </td>
                  <td className="py-2.5 text-center">
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-bold ${
                      d.direction === 'STABLE'
                        ? 'text-slate-400 bg-slate-800'
                        : d.direction === 'INCREASE'
                        ? 'text-rose-400 bg-rose-950/60 border border-rose-800/60'
                        : 'text-amber-400 bg-amber-950/60 border border-amber-800/60'
                    }`}>
                      {d.direction === 'INCREASE' && <ArrowUpRight className="w-3 h-3" />}
                      {d.direction === 'DECREASE' && <ArrowDownRight className="w-3 h-3" />}
                      {d.direction === 'STABLE' && <Minus className="w-3 h-3" />}
                      {d.arrow} {d.direction}
                    </span>
                  </td>
                  <td className={`py-2.5 text-right font-bold ${
                    isRed ? 'text-rose-400' : isAmber ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {d.delta_pct > 0 ? `+${d.delta_pct}%` : `${d.delta_pct}%`}
                  </td>
                  <td className="py-2.5 text-right">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                      isRed 
                        ? 'bg-rose-950 text-rose-300 border border-rose-800' 
                        : isAmber 
                        ? 'bg-amber-950 text-amber-300 border border-amber-800' 
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}>
                      {d.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
