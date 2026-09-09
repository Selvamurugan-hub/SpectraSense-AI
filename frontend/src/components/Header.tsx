import React, { useState } from 'react';
import { Radio, ShieldAlert, Cpu, Sparkles, CheckCircle2, RefreshCw } from 'lucide-react';
import { ApiService } from '../services/api';

interface HeaderProps {
  onDemoSeeded?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onDemoSeeded }) => {
  const [seeding, setSeeding] = useState(false);
  const [seededMsg, setSeededMsg] = useState(false);

  const handleSeed = async () => {
    try {
      setSeeding(true);
      await ApiService.seedDemoData();
      setSeededMsg(true);
      if (onDemoSeeded) onDemoSeeded();
      setTimeout(() => setSeededMsg(false), 4000);
    } catch (e) {
      console.error(e);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <header className="bg-[#0B132B]/95 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md px-6 py-3.5 flex items-center justify-between shadow-lg">
      <div className="flex items-center space-x-4">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
          <Radio className="w-5 h-5 text-white animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              Signal Analysis Assistant
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                NTRO • PS #26147
              </span>
            </h1>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Automated .IQ & .WAV Telemetry Intelligence • Space Technology Division
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-3 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
          <div className="flex items-center text-slate-300 gap-1.5 font-mono">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>DSP ENGINE: <b className="text-emerald-400">ACTIVE</b></span>
          </div>
          <span className="text-slate-600">|</span>
          <div className="flex items-center text-slate-300 gap-1.5 font-mono">
            <span>FORMATS: <b className="text-slate-200">.WAV • .IQ • RAW BINARY</b></span>
          </div>
        </div>

        <button
          onClick={handleSeed}
          disabled={seeding}
          className="flex items-center space-x-2 px-3.5 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all active:scale-95 disabled:opacity-50"
        >
          {seeding ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
          )}
          <span>{seeding ? 'Generating...' : seededMsg ? 'Demo Data Ready!' : 'Load Demo Signals'}</span>
        </button>
      </div>
    </header>
  );
};
