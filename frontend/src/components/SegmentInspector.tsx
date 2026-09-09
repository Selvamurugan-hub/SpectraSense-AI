import React from 'react';
import { Layers, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { SignalSegmentItem } from '../types';

interface SegmentInspectorProps {
  segments: SignalSegmentItem[];
  selectedSegmentIdx: number | null;
  onSelectSegment: (idx: number | null) => void;
}

export const SegmentInspector: React.FC<SegmentInspectorProps> = ({
  segments,
  selectedSegmentIdx,
  onSelectSegment
}) => {
  if (!segments || segments.length === 0) {
    return null;
  }

  return (
    <div className="telemetry-card space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white">Automatic Signal Segmentation</h3>
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
            {segments.length} Burst Segment(s) Detected
          </span>
        </div>

        <button
          onClick={() => onSelectSegment(null)}
          className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
            selectedSegmentIdx === null
              ? 'bg-cyan-600 text-white font-semibold shadow'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          View Full Signal
        </button>
      </div>

      {/* Segments Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
        {segments.map((s) => {
          const isSelected = selectedSegmentIdx === s.segment_index;
          const hasAnomaly = s.is_anomaly;

          return (
            <button
              key={s.segment_index}
              onClick={() => onSelectSegment(s.segment_index)}
              className={`p-2.5 rounded-lg border text-left transition-all font-mono text-xs ${
                isSelected
                  ? 'bg-cyan-950/60 border-cyan-400 text-white shadow-lg ring-1 ring-cyan-400'
                  : hasAnomaly
                  ? 'bg-rose-950/20 border-rose-800/60 text-slate-300 hover:border-rose-600'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-white">Segment #{s.segment_index}</span>
                {hasAnomaly ? (
                  <AlertTriangle className="w-3 h-3 text-rose-400" />
                ) : (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                )}
              </div>
              <div className="text-[10px] text-slate-400 space-y-0.5">
                <div>Time: {s.start_time_sec}s - {s.end_time_sec}s</div>
                <div>Dur: {(s.duration_sec * 1000).toFixed(1)} ms</div>
                <div className="text-cyan-400">Power: {s.estimated_power_db} dB</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
