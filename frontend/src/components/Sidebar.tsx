import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Activity, 
  History, 
  AlertTriangle, 
  FileText,
  Sliders,
  Database
} from 'lucide-react';

export type NavTab = 'dashboard' | 'upload' | 'analysis' | 'baselines' | 'anomalies' | 'reports';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  activeAnalysisId: number | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, activeAnalysisId }) => {
  const navItems: { id: NavTab; label: string; icon: React.FC<any>; badge?: string }[] = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Ingest', icon: UploadCloud },
    { 
      id: 'analysis', 
      label: 'Signal Analysis', 
      icon: Activity, 
      badge: activeAnalysisId ? `#${activeAnalysisId}` : undefined 
    },
    { id: 'baselines', label: 'Historical Baselines', icon: Database },
    { id: 'anomalies', label: 'Anomaly Triage', icon: AlertTriangle },
    { id: 'reports', label: 'Technical Reports', icon: FileText },
  ];

  return (
    <aside className="w-64 bg-[#0A0F1D] border-r border-slate-800/80 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        <div className="px-2 py-1">
          <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500 font-mono">
            Navigation Console
          </p>
        </div>

        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Footer Info */}
      <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/60 text-xs">
        <div className="flex items-center justify-between text-slate-400 font-mono text-[10px] mb-1">
          <span>NTRO PROTOCOL</span>
          <span className="text-emerald-400">ONLINE</span>
        </div>
        <div className="text-[11px] text-slate-300 font-medium">
          Signal Processing Engine v1.0
        </div>
        <p className="text-[10px] text-slate-500 mt-1">
          Space Telemetry & IQ Analysis
        </p>
      </div>
    </aside>
  );
};
