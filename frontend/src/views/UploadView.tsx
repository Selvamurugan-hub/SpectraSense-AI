import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileAudio, 
  Radio, 
  Sparkles, 
  Sliders, 
  AlertCircle, 
  CheckCircle2, 
  RefreshCw, 
  Play, 
  Cpu 
} from 'lucide-react';
import { ApiService } from '../services/api';

interface UploadViewProps {
  onAnalysisComplete: (analysisId: number) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({ onAnalysisComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [sampleRate, setSampleRate] = useState<number>(500000);
  const [iqFormat, setIqFormat] = useState<string>('float32');
  const [centerFreq, setCenterFreq] = useState<number>(0);
  const [uploading, setUploading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [demoSamples, setDemoSamples] = useState<any[]>([]);
  const [loadingDemo, setLoadingDemo] = useState<boolean>(false);

  useEffect(() => {
    fetchDemoSamples();
  }, []);

  const fetchDemoSamples = async () => {
    try {
      const data = await ApiService.getDemoSamples();
      setDemoSamples(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setErrorMsg(null);
      // Auto adjust defaults if WAV
      if (selected.name.toLowerCase().endsWith('.wav')) {
        setSampleRate(48000);
      }
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) {
      setErrorMsg('Please select a valid IQ or WAV file to upload.');
      return;
    }

    try {
      setUploading(true);
      setErrorMsg(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('sample_rate', sampleRate.toString());
      formData.append('iq_format', iqFormat);
      formData.append('center_freq_hz', centerFreq.toString());

      // 1. Upload & Validate
      const uploadRes = await ApiService.uploadFile(formData);

      // 2. Trigger Full Analysis
      const analysisRes = await ApiService.runAnalysis(uploadRes.file_id);

      // 3. Jump to workbench
      onAnalysisComplete(analysisRes.analysis_id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Signal upload/analysis failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyzeDemoFile = async (demoSample: any) => {
    try {
      setLoadingDemo(true);
      setErrorMsg(null);

      // Seed first to ensure DB has it
      await ApiService.seedDemoData();

      // Find file ID from dashboard
      const summary = await ApiService.getDashboardSummary();
      const matched = summary.files.find(f => f.filename === demoSample.name);

      if (matched) {
        const res = await ApiService.runAnalysis(matched.id);
        onAnalysisComplete(res.analysis_id);
      } else {
        setErrorMsg(`Could not resolve demo file '${demoSample.name}' in catalog.`);
      }
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to analyze demo signal.');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* View Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">
          Signal Ingestion & DSP Preprocessing Laboratory
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Upload real-world .WAV audio/telemetry recordings or raw binary complex .IQ streams.
        </p>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-300 text-xs flex items-center gap-2.5 shadow-lg">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span><b>Validation Error:</b> {errorMsg}</span>
        </div>
      )}

      {/* Main Upload Panel */}
      <div className="telemetry-card space-y-5">
        <div className="border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <UploadCloud className="w-4 h-4 text-cyan-400" />
            File Ingestion & Stream Format Settings
          </h3>
          <p className="text-[11px] text-slate-400">
            Supports .wav (PCM 16/24/32-bit), .iq / raw binary (Float32 complex, Int16 complex, Int8 complex)
          </p>
        </div>

        {/* Drag and drop zone */}
        <div className="border-2 border-dashed border-slate-700 hover:border-cyan-500/70 rounded-xl p-6 text-center transition-all bg-slate-900/40">
          <input
            type="file"
            id="signal-file-input"
            onChange={handleFileChange}
            accept=".wav,.iq,.raw,.bin,.dat,.fc32,.sc16,.sc8,.cu8"
            className="hidden"
          />
          <label htmlFor="signal-file-input" className="cursor-pointer space-y-2 block">
            <div className="w-12 h-12 rounded-full bg-cyan-950/60 border border-cyan-800 text-cyan-400 flex items-center justify-center mx-auto shadow-md">
              <FileAudio className="w-6 h-6" />
            </div>
            <div className="text-sm font-medium text-slate-200">
              {file ? (
                <span className="text-cyan-300 font-mono font-bold">{file.name}</span>
              ) : (
                'Click or drag & drop IQ / WAV telemetry file here'
              )}
            </div>
            <p className="text-[11px] text-slate-500 font-mono">
              {file ? `${(file.size / 1024).toFixed(1)} KB • Ready for Ingestion` : 'MAX FILE SIZE: 200MB • SUPPORTS CHUNKED STREAMING'}
            </p>
          </label>
        </div>

        {/* Metadata Configuration Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              Sample Rate (Fs)
            </label>
            <div className="space-y-1">
              <input
                type="number"
                value={sampleRate}
                onChange={(e) => setSampleRate(parseFloat(e.target.value) || 1000000)}
                placeholder="500000"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
              />
              <div className="flex gap-1 text-[10px] font-mono">
                <button type="button" onClick={() => setSampleRate(48000)} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white">48 kHz</button>
                <button type="button" onClick={() => setSampleRate(500000)} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white">500 kHz</button>
                <button type="button" onClick={() => setSampleRate(1000000)} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white">1 MSps</button>
                <button type="button" onClick={() => setSampleRate(2000000)} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white">2 MSps</button>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-cyan-400" />
              Binary IQ Format
            </label>
            <select
              value={iqFormat}
              onChange={(e) => setIqFormat(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="float32">Float32 Complex (I0, Q0, I1, Q1... 32-bit)</option>
              <option value="int16">Int16 Complex (sc16 16-bit signed)</option>
              <option value="int8">Int8 Complex (sc8 8-bit signed)</option>
              <option value="cu8">UInt8 Complex (cu8 8-bit unsigned RTL-SDR)</option>
              <option value="wav_pcm">WAV Audio / Stereo Analogue</option>
            </select>
            <span className="text-[10px] text-slate-500 mt-1 block">Determines binary unpack layout</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              Center Frequency Offset (Hz)
            </label>
            <input
              type="number"
              value={centerFreq}
              onChange={(e) => setCenterFreq(parseFloat(e.target.value) || 0)}
              placeholder="0 (Baseband)"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">RF carrier translation offset</span>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleUploadAndAnalyze}
            disabled={uploading || !file}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center space-x-2 disabled:opacity-50 transition-all active:scale-95"
          >
            {uploading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            <span>{uploading ? 'Processing DSP Pipeline...' : 'Run Automated Signal Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Built-in Space Telemetry Demo Library */}
      <div className="telemetry-card space-y-4">
        <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-yellow-400" />
              Pre-built Space Telemetry & Defense Radar Signals
            </h3>
            <p className="text-[11px] text-slate-400">
              Zero-configuration synthetic test cases for instant DSP pipeline verification
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
            DEMO LAB
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {demoSamples.map((sample, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-lg border flex flex-col justify-between space-y-3 transition-all ${
                sample.is_anomaly
                  ? 'bg-rose-950/15 border-rose-800/50 hover:border-rose-600'
                  : 'bg-slate-900/60 border-slate-800 hover:border-cyan-500/50'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-bold text-white">{sample.name}</span>
                  {sample.is_anomaly ? (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
                      ANOMALOUS
                    </span>
                  ) : (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                      NOMINAL
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400">{sample.description}</p>
                <div className="text-[10px] font-mono text-slate-500 mt-1">
                  Format: <b className="text-slate-300">{sample.file_type.toUpperCase()}</b> • Sample Rate: <b className="text-slate-300">{(sample.sample_rate / 1e3).toFixed(1)} kSps</b>
                </div>
              </div>

              <button
                onClick={() => handleAnalyzeDemoFile(sample)}
                disabled={loadingDemo}
                className="w-full py-1.5 rounded bg-slate-800 hover:bg-cyan-600 text-slate-200 hover:text-white font-mono text-xs font-medium flex items-center justify-center space-x-1.5 transition-all disabled:opacity-50"
              >
                {loadingDemo ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : (
                  <Play className="w-3 h-3 fill-current" />
                )}
                <span>Analyze Signal</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
