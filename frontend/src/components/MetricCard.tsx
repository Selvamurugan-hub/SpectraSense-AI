import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  sublabel?: string;
  icon?: React.FC<any>;
  variant?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'slate' | 'purple';
  trend?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  sublabel,
  icon: Icon,
  variant = 'slate',
  trend
}) => {
  const variantStyles = {
    cyan: 'border-cyan-800/40 bg-gradient-to-b from-cyan-950/20 to-slate-900/60 text-cyan-400',
    emerald: 'border-emerald-800/40 bg-gradient-to-b from-emerald-950/20 to-slate-900/60 text-emerald-400',
    amber: 'border-amber-800/40 bg-gradient-to-b from-amber-950/20 to-slate-900/60 text-amber-400',
    rose: 'border-rose-800/40 bg-gradient-to-b from-rose-950/20 to-slate-900/60 text-rose-400',
    purple: 'border-purple-800/40 bg-gradient-to-b from-purple-950/20 to-slate-900/60 text-purple-400',
    slate: 'border-slate-800 bg-slate-900/60 text-slate-300'
  };

  return (
    <div className={`rounded-xl border p-4 shadow-md transition-all hover:border-slate-700 ${variantStyles[variant]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
        {Icon && <Icon className="w-4 h-4 opacity-80" />}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">{value}</span>
        {trend && <span className="text-xs font-medium text-emerald-400">{trend}</span>}
      </div>
      {sublabel && <p className="text-[11px] text-slate-400 mt-1 font-sans">{sublabel}</p>}
    </div>
  );
};
