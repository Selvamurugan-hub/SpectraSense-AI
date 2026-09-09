# Signal Analysis Assistant (NTRO)
### Automated Model for Analysis of .IQ and .WAV Files with Signal Parameter Extraction

**Problem Statement ID**: 26147  
**Organization**: National Technical Research Organisation (NTRO)  
**Theme**: Space Technology  
**Category**: Software  
**System Name**: Signal Analysis Assistant  

---

## 🛰️ 1. Project Overview

The **Signal Analysis Assistant** is an end-to-end engineering signal processing and telemetry intelligence platform developed for the National Technical Research Organisation (NTRO). The platform ingests raw binary complex `.iq` files (Float32, Int16, Int8, RTL-SDR cu8) and `.wav` audio/telemetry recordings, executes deterministic DSP signal analysis, automatically segments burst signals, extracts comprehensive measured and derived RF parameters, constructs deterministic **Signal Fingerprints**, benchmarks against historical reference baselines, computes directional **"What Changed?"** delta divergence, pinpoints explainable anomalies using statistical and Isolation Forest techniques, calculates **Signal Health (0-100)** and **Confidence** scores, prioritizes signals for defense analysts, and compiles defense-grade technical **PDF Reports**.

---

## ⚡ 2. Core Workflow

```
       [ Upload IQ / WAV File ]
                  ↓
     [ File Validation & Metadata ]
                  ↓
      [ Signal Preprocessing ]
       (DC Removal, Normalization)
                  ↓
  [ Automatic Signal Segmentation ]
       (Energy Envelope & Flux)
                  ↓
      [ Parameter Extraction ]
  (Measured vs. Derived RF Metrics)
                  ↓
   [ Deterministic Fingerprint ]
       (7D Vector + SHA-256 ID)
                  ↓
    [ Historical Baseline Match ]
                  ↓
       [ "What Changed?" ]
   (Directional Deltas: ↑, ↓, →)
                  ↓
   [ Explainable Anomaly Engine ]
  (Z-Score + Isolation Forest Outlier)
                  ↓
 [ Confidence & Signal Health Score ]
    (0-100 Deductive Factor Tree)
                  ↓
  [ Analyst Priority Triage Queue ]
        (HIGH / MEDIUM / LOW)
                  ↓
  [ Explainable Engineering Summary ]
                  ↓
[ Defense-Grade Technical PDF Report ]
```

---

## 🛠️ 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, Plotly.js (`react-plotly.js`), Lucide React Icons.
- **Backend**: Python 3.9+, FastAPI, Uvicorn, SQLAlchemy (SQLite for zero-config MVP, ready for PostgreSQL).
- **Signal Processing & DSP**: NumPy, SciPy (Welch PSD, Hilbert analytic transform, Short-Time Fourier Transform STFT, dynamic thresholding, envelope tracking).
- **Machine Learning & Statistics**: Scikit-Learn (Isolation Forest outlier detection, Mahalanobis distance, Z-score deviation).
- **Report Generation**: ReportLab (High-resolution embedded Matplotlib time-domain, FFT, and spectrogram plots, telemetry tables, fingerprint visualizers).

---

## 📁 4. Supported File Formats

| Format | Extension | Representation | Description |
|---|---|---|---|
| **Raw Complex Float32** | `.iq`, `.raw`, `.fc32` | Interleaved `I0, Q0, I1, Q1...` (32-bit float) | Defense SDR & Spacecraft telemetry downlink |
| **Complex Int16** | `.iq`, `.bin`, `.sc16` | Interleaved `I0, Q0, I1, Q1...` (16-bit signed int) | Standard SDR captures (HackRF, USRP) |
| **Complex Int8 / UInt8** | `.raw`, `.cu8`, `.sc8` | Interleaved `I0, Q0, I1, Q1...` (8-bit int) | RTL-SDR & high-rate compressed telemetry |
| **WAV Audio / Telemetry**| `.wav` | Mono / Stereo 16/24/32-bit PCM | Analogue telemetry, acoustic radar, beacon signals |

---

## 🔬 5. Mathematical & Signal Processing Methodology

### 5.1 Preprocessing
- **DC Offset Removal**: Independent zero-mean centering of In-Phase ($I$) and Quadrature ($Q$) components:
  $$\tilde{I}(t) = I(t) - \frac{1}{N}\sum_{n=1}^N I[n], \quad \tilde{Q}(t) = Q(t) - \frac{1}{N}\sum_{n=1}^N Q[n]$$
- **Peak Normalization**: Scale maximum envelope magnitude to unit peak preserving dynamic range.
- **Noise Floor Estimation**: Median Absolute Deviation (MAD) of the lowest 20th percentile spectral density.

### 5.2 Automatic Signal Segmentation
- Sliding short-time energy window with adaptive noise-gate thresholding and hysteresis to detect active bursts and pulse trains without false triggering.

### 5.3 Parameter Extraction
- **Center Frequency & Spectral Centroid**: Power-weighted centroid:
  $$f_c = \frac{\sum f_k \cdot P(f_k)}{\sum P(f_k)}$$
- **Occupied Bandwidth (99% OBW)**: Numerical integration containing 99.0% of total spectral power.
- **-3 dB & -10 dB Bandwidths**: Dynamic search around peak PSD.
- **Signal-to-Noise Ratio (SNR)**: $SNR_{\text{dB}} = P_{\text{peak, dBFS}} - P_{\text{noise floor, dBFS}}$.
- **Signal Stability Index**: Normalized inverse envelope variance:
  $$S_{\text{stability}} = \frac{1}{1 + \frac{\text{Var}(|x|)}{\text{Mean}(|x|)^2}}$$

### 5.4 Deterministic Signal Fingerprinting
- Multi-dimensional normalized feature vector:
  $$\vec{V}_{\text{FP}} = [f_{c, \text{norm}}, B_{\text{norm}}, P_{\text{norm}}, SNR_{\text{norm}}, S_{\text{norm}}, \text{Flatness}_{\text{norm}}, \text{Crest}_{\text{norm}}]$$
- Cryptographic Signature: Deterministic SHA-256 signature hash formatted as `FP-<16_HEX>`. Same input produces identical signature.

### 5.5 "What Changed?" Comparative Delta Engine
- Real-time parameter-by-parameter comparative delta vs historical baseline:
  $$\Delta \% = \left(\frac{x_{\text{current}} - \mu_{\text{baseline}}}{\mu_{\text{baseline}}}\right) \times 100\%$$
- Status indicators: $\uparrow$ Increase, $\downarrow$ Decrease, $\rightarrow$ Stable with critical threshold flags.

### 5.6 Signal Health Scoring (0 - 100)
Transparent deductive scoring tree starting at 100:
- Critical low SNR ($< 6\text{ dB}$): $-25$
- Sub-optimal SNR ($< 12\text{ dB}$): $-12$
- Envelope instability ($< 0.6$): $-18$
- Critical Anomaly: $-20$ per event
- High Anomaly: $-14$ per event
- Warning Anomaly: $-8$ per event

Status: **GOOD** (80-100) | **WARNING** (55-79) | **CRITICAL** (0-54).

---

## 🚀 6. Installation & Quick Start

### Prerequisites
- Python 3.9+
- Node.js v18+ & npm

### Backend Setup
```bash
# Navigate to workspace
cd "AI signal analysis system"

# Run tests
cd backend
python -m pytest tests

# Start FastAPI backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`.

### Frontend Setup
```bash
# Open new terminal
cd "AI signal analysis system/frontend"

# Install dependencies (already built in production)
npm install

# Start Vite development server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 7. Demo Lab Instructions

The system includes a **Demo Laboratory** featuring 4 pre-built Space & Defense test signals:
1. **DEMO_SAT_QPSK_NOMINAL.iq**: Clean Space QPSK Telemetry ($f_c = 80\text{ kHz}$, SNR $\approx 25\text{ dB}$).
2. **DEMO_SAT_QPSK_DEGRADED.iq**: Anomalous Space QPSK with carrier drift ($+22\text{ kHz}$ error) and high noise (SNR $\approx 9\text{ dB}$).
3. **DEMO_RADAR_CHIRP_PULSED.wav**: 5-pulse LFM Radar Chirp ($2\text{ kHz} \to 12\text{ kHz}$ sweep).
4. **DEMO_FSK_TELEMETRY_BEACON.wav**: 4-ary Frequency Hopping FSK telemetry bursts.

**Quick Demo Walkthrough**:
1. Open the UI at `http://localhost:5173`.
2. Click **"Load Demo Signals"** in the top header.
3. Select **"Upload & Ingest"** and click **"Analyze Signal"** on `DEMO_SAT_QPSK_NOMINAL.iq` to establish baseline.
4. Run analysis on `DEMO_SAT_QPSK_DEGRADED.iq` to observe the **"What Changed?"** delta analysis ($\uparrow +27.6\%$ Frequency Drift, $\downarrow 16\text{ dB}$ SNR Drop) and anomaly alert triggers.
5. Click **"Download Technical PDF Report"** to export the technical document.

---

## 🔒 8. Defense Compliance & Security

- **Strictly Local DSP**: No external third-party cloud AI APIs required. Zero telemetry data leakage.
- **Explainable Predictions**: Every score is accompanied by its underlying physical formulas and measured metrics.
