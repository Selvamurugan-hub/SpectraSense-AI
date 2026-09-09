import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, NavTab } from './components/Sidebar';
import { DashboardView } from './views/DashboardView';
import { UploadView } from './views/UploadView';
import { SignalAnalysisView } from './views/SignalAnalysisView';
import { HistoricalBaselinesView } from './views/HistoricalBaselinesView';
import { AnomalyInvestigationView } from './views/AnomalyInvestigationView';
import { ReportsView } from './views/ReportsView';
import { DashboardSummary } from './types';
import { ApiService } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');
  const [activeAnalysisId, setActiveAnalysisId] = useState<number | null>(null);
  const [dashboardSummary, setDashboardSummary] = useState<DashboardSummary | null>(null);
  const [loadingDashboard, setLoadingDashboard] = useState<boolean>(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoadingDashboard(true);
      const data = await ApiService.getDashboardSummary();
      setDashboardSummary(data);
      // If there are recent analyses, default active analysis to latest
      if (data.recent_analyses.length > 0 && activeAnalysisId === null) {
        setActiveAnalysisId(data.recent_analyses[0].analysis_id);
      }
    } catch (e) {
      console.error('Failed to load dashboard:', e);
    } finally {
      setLoadingDashboard(false);
    }
  };

  const handleNavigateToAnalysis = (analysisId: number) => {
    setActiveAnalysisId(analysisId);
    setActiveTab('analysis');
  };

  const handleAnalysisComplete = (analysisId: number) => {
    setActiveAnalysisId(analysisId);
    setActiveTab('analysis');
    loadDashboard();
  };

  const handleDemoSeeded = async () => {
    await loadDashboard();
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#0B1120] text-slate-100 font-sans">
      {/* Top Header */}
      <Header onDemoSeeded={handleDemoSeeded} />

      {/* Main Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          activeAnalysisId={activeAnalysisId}
        />

        {/* Viewport Content */}
        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-61px)]">
          {activeTab === 'dashboard' && (
            <DashboardView
              summary={dashboardSummary}
              loading={loadingDashboard}
              onNavigateToAnalysis={handleNavigateToAnalysis}
              onNavigateToUpload={() => setActiveTab('upload')}
            />
          )}

          {activeTab === 'upload' && (
            <UploadView
              onAnalysisComplete={handleAnalysisComplete}
            />
          )}

          {activeTab === 'analysis' && (
            activeAnalysisId ? (
              <SignalAnalysisView
                analysisId={activeAnalysisId}
                onNavigateToReports={() => setActiveTab('reports')}
              />
            ) : (
              <div className="telemetry-card text-center py-16 space-y-4 max-w-lg mx-auto">
                <div className="text-sm font-bold text-white">No Signal Selected For Analysis</div>
                <p className="text-xs text-slate-400">
                  Please upload a signal file or select one from the demo laboratory to open the workbench.
                </p>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold"
                >
                  Go to Upload & Ingestion
                </button>
              </div>
            )
          )}

          {activeTab === 'baselines' && (
            <HistoricalBaselinesView />
          )}

          {activeTab === 'anomalies' && (
            <AnomalyInvestigationView
              onNavigateToAnalysis={handleNavigateToAnalysis}
            />
          )}

          {activeTab === 'reports' && (
            <ReportsView
              onNavigateToAnalysis={handleNavigateToAnalysis}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
