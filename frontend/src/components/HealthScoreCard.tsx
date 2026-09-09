import React from 'react';
import { HeartPulse, ShieldCheck, AlertCircle, AlertOctagon, HelpCircle, CheckCircle2, ChevronRight } from 'lucide-react';
import { ScoringBreakdownItem } from '../types';

interface HealthScoreCardProps {
  healthScore: number;
  healthStatus: 'GOOD' | 'WARNING' | 'CRITICAL';
  confidenceScore: number;
  analystPriority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priorityReason: string;
  scoringBreakdown: ScoringBreakdownItem[];
}

export const HealthScoreCard: React.FC<HealthScoreCardProps> = ({
  healthScore,
  healthStatus,
  confidenceScore,
  analystPriority,
  priorityReason,
  scoringBreakdown
}) => {
  const isGood = healthStatus === 'GOOD';
  const isWarning = healthStatus === 'WARNING';
  const isCritical = healthStatus === 'CRITICAL';

  const statusColor = isGood
    ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800'
    : isWarning
    ? 'text-amber-400 bg-amber-950/60 border-amber-800'
    : 'text-rose-400 bg-rose-950/60 border-rose-800';

  const priorityColor = analystPriority === 'HIGH' || analystPriority === 'CRITICAL'
    ? 'text-rose-400 bg-rose-950 border-rose-800'
    : analystPriority === 'MEDIUM'
    ? 'text-amber-400 bg-amber-950 border-amber-800'
    : 'text-emerald-400 bg-emerald-950 border-emerald-800';

  return (
    <div className="telemetry-card space-y-4">
      {/* Top Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Health Score Gauge Card */}
        <div className="bg-[#0B1120] p-3.5 rounded-lg border border-slate-800 flex items-center space-x-3.5">
          <div className="relative flex items-center justify-center">
            <svg className="w-16 h-16 transform -rotate-90">
              <circle
                cx="32"
                cy="32"
                r="28"
                stroke="#1E293B"
                strokeWidth="5"
                fill="transparent"
              />
              <circle
                cx="32"
                cy="32"
                r="28"
                stroke={isGood ? '#10B981' : isWarning ? '#F59E0B' : '#F43F5E'}
                strokeWidth="5"
                strokeDasharray={175}
                strokeDashoffset={175 - (175 * healthScore) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <span className="absolute text-sm font-bold font-mono text-white">{Math.round(healthScore)}</span>
          </div>

          <div>
            <div className="text-[11px] text-slate-400 uppercase font-mono">Signal Health</div>
            <div className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold mt-1 border ${statusColor}`}>
              {healthStatus}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Scale: 0 - 100</div>
          </div>
        </div>

        {/* Confidence Score Card */}
        <div className="bg-[#0B1120] p-3.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>CONFIDENCE SCORE</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="text-2xl font-bold font-mono text-cyan-300">
              {confidenceScore.toFixed(1)}%
            </div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Composite SNR & DSP Data Integrity
            </p>
          </div>
        </div>

        {/* Analyst Priority Card */}
        <div className="bg-[#0B1120] p-3.5 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>ANALYST PRIORITY</span>
            <HeartPulse className="w-4 h-4 text-rose-400" />
          </div>
          <div>
            <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-bold font-mono border ${priorityColor}`}>
              {analystPriority} PRIORITY
            </span>
            <p className="text-[10px] text-slate-400 mt-1 line-clamp-1">
              {priorityReason}
            </p>
          </div>
        </div>
      </div>

      {/* Deductive Factor Scoring Tree */}
      {scoringBreakdown && scoringBreakdown.length > 0 && (
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
              Explainable Health Scoring Factor Breakdown
            </span>
            <span className="text-[10px] text-slate-500 font-mono">BASE SCORE: 100</span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            {scoringBreakdown.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-1.5 rounded bg-slate-900/50 border border-slate-800/50 text-[11px]">
                <div className="flex items-center space-x-2">
                  <span className={`font-bold ${item.impact < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {item.impact === 0 ? '+0' : item.impact}
                  </span>
                  <span className="text-slate-300 font-sans">{item.factor}</span>
                </div>
                <span className="text-slate-400 text-[10px]">{item.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
