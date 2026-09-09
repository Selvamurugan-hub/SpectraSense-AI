import {
  DashboardSummary,
  AnalysisDetail,
  VisualizationsData,
  BaselineItem,
  SignalAnomalyItem
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export const ApiService = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  async uploadFile(formData: FormData): Promise<{ status: string; file_id: number; metadata: any }> {
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async runAnalysis(fileId: number, baselineId?: number): Promise<{ analysis_id: number }> {
    const url = baselineId 
      ? `${API_BASE}/analysis/run/${fileId}?baseline_id=${baselineId}`
      : `${API_BASE}/analysis/run/${fileId}`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(err.detail || 'Analysis execution failed');
    }
    return res.json();
  },

  async getAnalysisDetails(analysisId: number): Promise<AnalysisDetail> {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}`);
    if (!res.ok) throw new Error(`Failed to fetch analysis #${analysisId}`);
    return res.json();
  },

  async getVisualizations(analysisId: number, segmentIdx?: number): Promise<VisualizationsData> {
    const url = segmentIdx !== undefined
      ? `${API_BASE}/analysis/${analysisId}/visualizations?segment_idx=${segmentIdx}`
      : `${API_BASE}/analysis/${analysisId}/visualizations`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch signal visualizations');
    return res.json();
  },

  async getBaselines(): Promise<BaselineItem[]> {
    const res = await fetch(`${API_BASE}/baselines`);
    if (!res.ok) throw new Error('Failed to fetch baselines');
    return res.json();
  },

  async createBaseline(name: string, description: string, analysisId: number, signalType: string = 'space_telemetry'): Promise<any> {
    const res = await fetch(`${API_BASE}/baselines/create-from-analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, analysis_id: analysisId, signal_type: signalType })
    });
    if (!res.ok) throw new Error('Failed to create baseline');
    return res.json();
  },

  async deleteBaseline(baselineId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/baselines/${baselineId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete baseline');
    return res.json();
  },

  async getAnomalies(severity?: string): Promise<SignalAnomalyItem[]> {
    const url = severity ? `${API_BASE}/anomalies?severity=${severity}` : `${API_BASE}/anomalies`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch anomalies');
    return res.json();
  },

  async generateReport(analysisId: number): Promise<{ report_id: number; download_url: string; pdf_filename: string }> {
    const res = await fetch(`${API_BASE}/reports/generate/${analysisId}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to generate technical report');
    return res.json();
  },

  async getReportsList(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/reports/list`);
    if (!res.ok) throw new Error('Failed to fetch reports list');
    return res.json();
  },

  async seedDemoData(): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/seed`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to seed demo data');
    return res.json();
  },

  async getDemoSamples(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/demo/samples`);
    if (!res.ok) throw new Error('Failed to fetch demo samples');
    return res.json();
  }
};
