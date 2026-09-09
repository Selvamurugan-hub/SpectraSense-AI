import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import { Waves, Activity, Grid, Compass, RefreshCw } from 'lucide-react';
import { VisualizationsData } from '../types';

interface SignalChartsProps {
  data: VisualizationsData | null;
  loading: boolean;
  onRefresh?: () => void;
}

export const SignalCharts: React.FC<SignalChartsProps> = ({ data, loading, onRefresh }) => {
  const [activeTab, setActiveTab] = useState<'all' | 'waveform' | 'fft' | 'spectrogram' | 'constellation'>('all');

  if (loading || !data) {
    return (
      <div className="telemetry-card h-[460px] flex flex-col items-center justify-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-xs font-mono">RENDERING INTERACTIVE PLOTLY DSP VISUALIZATIONS...</p>
      </div>
    );
  }

  // Dark Theme Plotly Layout defaults
  const darkLayoutDefaults: any = {
    paper_bgcolor: '#0F172A',
    plot_bgcolor: '#0B1120',
    font: { color: '#94A3B8', family: 'Inter, sans-serif', size: 10 },
    margin: { l: 48, r: 24, t: 36, b: 40 },
    xaxis: {
      gridcolor: '#1E293B',
      zerolinecolor: '#334155',
      tickfont: { size: 9, color: '#64748B' },
      titlefont: { size: 10, color: '#94A3B8' }
    },
    yaxis: {
      gridcolor: '#1E293B',
      zerolinecolor: '#334155',
      tickfont: { size: 9, color: '#64748B' },
      titlefont: { size: 10, color: '#94A3B8' }
    },
    showlegend: true,
    legend: {
      font: { size: 9, color: '#94A3B8' },
      bgcolor: 'rgba(15, 23, 42, 0.7)',
      bordercolor: '#334155',
      borderwidth: 1,
      x: 0.98,
      y: 0.98,
      xanchor: 'right'
    }
  };

  // 1. Waveform Traces
  const waveformTraces: any[] = [];
  if (data.waveform.is_complex && data.waveform.q_channel) {
    waveformTraces.push({
      x: data.waveform.time,
      y: data.waveform.i_channel,
      type: 'scatter',
      mode: 'lines',
      name: 'I (In-Phase)',
      line: { color: '#06B6D4', width: 1.2 }
    });
    waveformTraces.push({
      x: data.waveform.time,
      y: data.waveform.q_channel,
      type: 'scatter',
      mode: 'lines',
      name: 'Q (Quadrature)',
      line: { color: '#F59E0B', width: 1.1 }
    });
  } else {
    waveformTraces.push({
      x: data.waveform.time,
      y: data.waveform.i_channel,
      type: 'scatter',
      mode: 'lines',
      name: 'Signal Amplitude',
      line: { color: '#06B6D4', width: 1.2 }
    });
  }

  // 2. FFT PSD Traces
  const fftTraces: any[] = [
    {
      x: data.fft.frequencies_khz,
      y: data.fft.psd_db,
      type: 'scatter',
      mode: 'lines',
      name: 'Welch PSD',
      line: { color: '#8B5CF6', width: 1.4 },
      fill: 'tozeroy',
      fillcolor: 'rgba(139, 92, 246, 0.1)'
    }
  ];

  // 3. Spectrogram Traces (Heatmap)
  const specTraces: any[] = [
    {
      x: data.spectrogram.time_sec,
      y: data.spectrogram.freq_khz,
      z: data.spectrogram.power_mesh_db,
      type: 'heatmap',
      colorscale: 'Plasma',
      colorbar: {
        title: 'dB',
        titleside: 'right',
        tickfont: { size: 9, color: '#94A3B8' },
        thickness: 10,
        len: 0.9
      }
    }
  ];

  // 4. Constellation Traces (I vs Q)
  const constTraces: any[] = data.constellation ? [
    {
      x: data.constellation.i,
      y: data.constellation.q,
      type: 'scatter',
      mode: 'markers',
      name: 'I/Q Symbols',
      marker: {
        color: '#06B6D4',
        size: 4,
        opacity: 0.6,
        line: { color: '#0891B2', width: 0.5 }
      }
    }
  ] : [];

  return (
    <div className="telemetry-card space-y-3">
      {/* Visualizer Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === 'all'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Grid className="w-3.5 h-3.5" /> Multi-Spectral Grid
          </button>
          <button
            onClick={() => setActiveTab('waveform')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === 'waveform'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Activity className="w-3.5 h-3.5" /> Waveform
          </button>
          <button
            onClick={() => setActiveTab('fft')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === 'fft'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Activity className="w-3.5 h-3.5" /> FFT Spectrum
          </button>
          <button
            onClick={() => setActiveTab('spectrogram')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              activeTab === 'spectrogram'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Waves className="w-3.5 h-3.5" /> Spectrogram
          </button>
          {data.waveform.is_complex && (
            <button
              onClick={() => setActiveTab('constellation')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                activeTab === 'constellation'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Compass className="w-3.5 h-3.5" /> Constellation
            </button>
          )}
        </div>

        <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
          <span className="hidden sm:inline">INTERACTIVE ZOOM / PAN ENABLED</span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded bg-slate-900 border border-slate-700 hover:bg-slate-800 text-slate-300"
              title="Reset Zoom"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Grid View (Multi-Spectral 2x2 or Single View) */}
      {activeTab === 'all' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3.5">
          {/* Waveform */}
          <div className="bg-[#0B1120] rounded-lg p-2 border border-slate-800/80">
            <h4 className="text-xs font-semibold text-slate-300 px-2 py-1 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" /> Time-Domain Waveform (I/Q)
            </h4>
            <Plot
              data={waveformTraces}
              layout={{
                ...darkLayoutDefaults,
                title: undefined,
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Time (s)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Norm. Amplitude' },
                height: 230,
                autosize: true
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>

          {/* FFT Spectrum */}
          <div className="bg-[#0B1120] rounded-lg p-2 border border-slate-800/80">
            <h4 className="text-xs font-semibold text-slate-300 px-2 py-1 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-purple-400" /> FFT Power Spectral Density
            </h4>
            <Plot
              data={fftTraces}
              layout={{
                ...darkLayoutDefaults,
                title: undefined,
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Frequency (kHz)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'PSD (dB/Hz)' },
                height: 230,
                autosize: true
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>

          {/* Spectrogram */}
          <div className="bg-[#0B1120] rounded-lg p-2 border border-slate-800/80">
            <h4 className="text-xs font-semibold text-slate-300 px-2 py-1 flex items-center gap-1.5">
              <Waves className="w-3.5 h-3.5 text-pink-400" /> Spectrogram (Time-Frequency Heatmap)
            </h4>
            <Plot
              data={specTraces}
              layout={{
                ...darkLayoutDefaults,
                title: undefined,
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Time (s)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Freq (kHz)' },
                height: 230,
                autosize: true
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>

          {/* Constellation or Dominant Summary */}
          <div className="bg-[#0B1120] rounded-lg p-2 border border-slate-800/80">
            <h4 className="text-xs font-semibold text-slate-300 px-2 py-1 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-emerald-400" />
              {data.waveform.is_complex ? 'I/Q Constellation Diagram' : 'Envelope Dynamic Power Profile'}
            </h4>
            {data.waveform.is_complex && constTraces.length > 0 ? (
              <Plot
                data={constTraces}
                layout={{
                  ...darkLayoutDefaults,
                  title: undefined,
                  xaxis: { ...darkLayoutDefaults.xaxis, title: 'In-Phase (I)', range: [-1.2, 1.2] },
                  yaxis: { ...darkLayoutDefaults.yaxis, title: 'Quadrature (Q)', range: [-1.2, 1.2] },
                  height: 230,
                  autosize: true
                }}
                config={{ responsive: true, displayModeBar: false }}
                style={{ width: '100%' }}
              />
            ) : (
              <Plot
                data={[{
                  x: data.waveform.time,
                  y: data.waveform.envelope,
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#10B981', width: 1.2 },
                  fill: 'tozeroy',
                  fillcolor: 'rgba(16, 185, 129, 0.1)'
                }]}
                layout={{
                  ...darkLayoutDefaults,
                  title: undefined,
                  xaxis: { ...darkLayoutDefaults.xaxis, title: 'Time (s)' },
                  yaxis: { ...darkLayoutDefaults.yaxis, title: 'Envelope Mag' },
                  height: 230,
                  autosize: true
                }}
                config={{ responsive: true, displayModeBar: false }}
                style={{ width: '100%' }}
              />
            )}
          </div>
        </div>
      ) : (
        /* Single Full View */
        <div className="bg-[#0B1120] rounded-lg p-3 border border-slate-800/80">
          {activeTab === 'waveform' && (
            <Plot
              data={waveformTraces}
              layout={{
                ...darkLayoutDefaults,
                title: 'Time-Domain Waveform (I/Q Channels)',
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Time (s)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Normalized Amplitude' },
                height: 400,
                autosize: true
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          )}
          {activeTab === 'fft' && (
            <Plot
              data={fftTraces}
              layout={{
                ...darkLayoutDefaults,
                title: 'FFT Power Spectral Density (PSD)',
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Frequency (kHz)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Power (dB/Hz)' },
                height: 400,
                autosize: true
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          )}
          {activeTab === 'spectrogram' && (
            <Plot
              data={specTraces}
              layout={{
                ...darkLayoutDefaults,
                title: 'Spectrogram (Time-Frequency Energy Heatmap)',
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'Time (s)' },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Frequency (kHz)' },
                height: 400,
                autosize: true
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          )}
          {activeTab === 'constellation' && constTraces.length > 0 && (
            <Plot
              data={constTraces}
              layout={{
                ...darkLayoutDefaults,
                title: 'I/Q Constellation Diagram (Symbol Cloud)',
                xaxis: { ...darkLayoutDefaults.xaxis, title: 'In-Phase (I)', range: [-1.2, 1.2] },
                yaxis: { ...darkLayoutDefaults.yaxis, title: 'Quadrature (Q)', range: [-1.2, 1.2] },
                height: 400,
                autosize: true
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          )}
        </div>
      )}
    </div>
  );
};
