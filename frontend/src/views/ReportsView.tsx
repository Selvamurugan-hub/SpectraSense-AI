import React, { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, FileCheck, ArrowRight, ExternalLink } from 'lucide-react';
import { ApiService } from '../services/api';

interface ReportsViewProps {
  onNavigateToAnalysis: (analysisId: number) => void;
}

export const ReportsView: React.FC<ReportsViewProps> = ({ onNavigateToAnalysis }) => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getReportsList();
      setReports(data);
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
            <FileText className="w-5 h-5 text-cyan-400" />
            Technical Reports & Defense Intelligence Archive
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Downloadable executive PDF reports with embedded time-domain waveforms, FFT spectra, fingerprints, and anomaly logs.
          </p>
        </div>
        <button
          onClick={fetchReports}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <div className="telemetry-card text-center py-12 text-slate-400 space-y-3">
          <FileCheck className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="text-sm font-semibold text-slate-200">No PDF Reports Compiled Yet</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Go to any completed signal analysis workbench and click <b>"Download Technical PDF Report"</b> to compile and archive formal PDF documentation.
          </p>
        </div>
      ) : (
        <div className="telemetry-card space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase font-sans">
                  <th className="pb-2.5 font-medium">Report Title / Target Signal</th>
                  <th className="pb-2.5 font-medium">Analysis ID</th>
                  <th className="pb-2.5 font-medium">Generation Date</th>
                  <th className="pb-2.5 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 text-white font-medium flex items-center gap-2.5">
                      <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                      <div>
                        <div className="font-sans font-bold">{r.report_title}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{r.filename}</div>
                      </div>
                    </td>
                    <td className="py-3 text-slate-300">
                      #{r.analysis_id}
                    </td>
                    <td className="py-3 text-slate-400 text-[11px]">
                      {r.generated_at?.replace('T', ' ').slice(0, 19)} UTC
                    </td>
                    <td className="py-3 text-right space-x-2">
                      <button
                        onClick={() => onNavigateToAnalysis(r.analysis_id)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-sans"
                      >
                        Workbench
                      </button>
                      <a
                        href={`http://localhost:8000${r.download_url}`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-sans font-semibold inline-flex items-center gap-1.5 shadow"
                      >
                        <Download className="w-3 h-3" /> Download PDF
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
