import os
import json
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)

from app.core.config import REPORT_DIR

class TechnicalReportGenerator:
    """Generates defense-grade executive and technical PDF reports."""

    @staticmethod
    def generate_pdf_report(
        file_meta: Dict[str, Any],
        extracted_params: Dict[str, Any],
        fingerprint: Dict[str, Any],
        segments: list,
        anomalies: list,
        deltas: Dict[str, Any],
        health_score: float,
        health_status: str,
        confidence_score: float,
        priority: str,
        priority_reason: str,
        explainable_summary: str,
        scoring_breakdown: list,
        signal_data: np.ndarray,
        sample_rate: float,
        output_filename: Optional[str] = None
    ) -> str:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        if not output_filename:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_filename = f"NTRO_Signal_Report_{file_meta.get('id', 1)}_{timestamp}.pdf"
            
        pdf_path = REPORT_DIR / output_filename
        
        # 1. Generate Figures for PDF
        chart_img_path = REPORT_DIR / f"temp_charts_{output_filename}.png"
        TechnicalReportGenerator._create_chart_image(signal_data, sample_rate, str(chart_img_path))
        
        # 2. Build Document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#475569')
        )
        section_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#334155')
        )
        badge_style = ParagraphStyle(
            'BadgeText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.white,
            alignment=1
        )
        
        story = []
        
        # Header Banner
        header_data = [
            [
                Paragraph("<b>NATIONAL TECHNICAL RESEARCH ORGANISATION (NTRO)</b><br/><font size=7 color='#64748B'>SIH 2026 Problem Statement ID: 26147 | Theme: Space Technology</font>", subtitle_style),
                Paragraph(f"<b>CLASSIFICATION: RESTRICTED // AI SIGNAL INTEL</b><br/><font size=7 color='#64748B'>Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</font>", subtitle_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[300, 220])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=8))
        
        # Title
        story.append(Paragraph(f"Signal Analysis & Telemetry Extraction Report", title_style))
        story.append(Paragraph(f"Target Recording: <b>{file_meta.get('filename', 'Unknown')}</b> | Format: <b>{file_meta.get('file_type', '').upper()}</b> | Sample Rate: <b>{sample_rate/1e3:.1f} kSps</b>", subtitle_style))
        story.append(Spacer(1, 8))
        
        # KPI Summary Cards (Health, Confidence, Priority)
        health_color = colors.HexColor('#16A34A') if health_status == 'GOOD' else (colors.HexColor('#D97706') if health_status == 'WARNING' else colors.HexColor('#DC2626'))
        priority_color = colors.HexColor('#DC2626') if priority == 'HIGH' else (colors.HexColor('#D97706') if priority == 'MEDIUM' else colors.HexColor('#16A34A'))
        
        kpi_data = [
            [
                Paragraph(f"SIGNAL HEALTH<br/><font size=14><b>{health_score:.0f}/100</b></font><br/>STATUS: {health_status}", badge_style),
                Paragraph(f"ANALYST PRIORITY<br/><font size=14><b>{priority}</b></font><br/>{priority_reason[:25]}...", badge_style),
                Paragraph(f"CONFIDENCE<br/><font size=14><b>{confidence_score:.1f}%</b></font><br/>DSP DATA QUALITY", badge_style),
                Paragraph(f"ANOMALIES<br/><font size=14><b>{len(anomalies)}</b></font><br/>DETECTED ISSUES", badge_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), health_color),
            ('BACKGROUND', (1,0), (1,0), priority_color),
            ('BACKGROUND', (2,0), (2,0), colors.HexColor('#0284C7')),
            ('BACKGROUND', (3,0), (3,0), colors.HexColor('#475569')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 10))
        
        # Section 1: Explainable Engineering Summary
        story.append(Paragraph("1. Explainable Analysis & Executive Summary", section_style))
        story.append(Paragraph(explainable_summary.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 8))
        
        # Section 2: Visual Signal Plots
        if chart_img_path.exists():
            story.append(Paragraph("2. Time-Domain, Spectral & Time-Frequency Visualization", section_style))
            story.append(Image(str(chart_img_path), width=520, height=210))
            story.append(Spacer(1, 8))
            
        # Section 3: Extracted Signal Parameters (Measured vs Derived)
        story.append(Paragraph("3. Extracted Signal Parameters", section_style))
        meas = extracted_params["measured"]
        der = extracted_params["derived"]
        
        param_table_data = [
            [
                Paragraph("<b>MEASURED PARAMETER</b>", body_style), Paragraph("<b>VALUE</b>", body_style),
                Paragraph("<b>DERIVED / ESTIMATED PARAMETER</b>", body_style), Paragraph("<b>VALUE</b>", body_style)
            ],
            [
                Paragraph("Peak Frequency", body_style), Paragraph(meas["peak_frequency_str"], body_style),
                Paragraph("Occupied Bandwidth (99% OBW)", body_style), Paragraph(der["occupied_bandwidth_99_str"], body_style)
            ],
            [
                Paragraph("Spectral Centroid", body_style), Paragraph(meas["spectral_centroid_str"], body_style),
                Paragraph("-3 dB Bandwidth", body_style), Paragraph(der["bandwidth_3db_str"], body_style)
            ],
            [
                Paragraph("Signal Power (dBFS)", body_style), Paragraph(f"{meas['signal_power_db']} dB", body_style),
                Paragraph("-10 dB Bandwidth", body_style), Paragraph(der["bandwidth_10db_str"], body_style)
            ],
            [
                Paragraph("Est. Noise Floor", body_style), Paragraph(f"{meas['estimated_noise_power_db']} dB", body_style),
                Paragraph("Signal Stability Index", body_style), Paragraph(f"{der['signal_stability_index']:.3f} / 1.0", body_style)
            ],
            [
                Paragraph("Measured SNR", body_style), Paragraph(f"<b>{meas['snr_db']} dB</b>", body_style),
                Paragraph("Crest Factor / PAPR", body_style), Paragraph(f"{der['crest_factor_ratio']} ({der['papr_db']} dB)", body_style)
            ],
            [
                Paragraph("Peak Amplitude", body_style), Paragraph(f"{meas['peak_amplitude_v']} V", body_style),
                Paragraph("Spectral Flatness (Entropy)", body_style), Paragraph(f"{der['spectral_flatness']:.4f}", body_style)
            ],
            [
                Paragraph("RMS Amplitude", body_style), Paragraph(f"{meas['rms_amplitude_v']} V", body_style),
                Paragraph("Modulation Classifier Hint", body_style), Paragraph(f"<b>{der['modulation_type_hint']}</b> ({der['modulation_hint_confidence_pct']}%)", body_style)
            ]
        ]
        param_table = Table(param_table_data, colWidths=[140, 120, 140, 120])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(param_table)
        story.append(Spacer(1, 8))
        
        # Section 4: Signal Fingerprint & Baseline Comparison
        story.append(Paragraph(f"4. Signal Fingerprint & 'What Changed?' Analysis (Fingerprint ID: <b>{fingerprint.get('fingerprint_id', 'N/A')}</b>)", section_style))
        
        delta_list = deltas.get("deltas", [])
        if deltas.get("has_baseline") and delta_list:
            delta_table_data = [
                [
                    Paragraph("<b>PARAMETER</b>", body_style),
                    Paragraph("<b>BASELINE MEAN</b>", body_style),
                    Paragraph("<b>CURRENT VALUE</b>", body_style),
                    Paragraph("<b>DELTA (%)</b>", body_style),
                    Paragraph("<b>DIR</b>", body_style),
                    Paragraph("<b>STATUS</b>", body_style)
                ]
            ]
            for d in delta_list:
                delta_table_data.append([
                    Paragraph(d["parameter"], body_style),
                    Paragraph(f"{d['baseline_value']} {d['unit']}", body_style),
                    Paragraph(f"{d['current_value']} {d['unit']}", body_style),
                    Paragraph(f"{d['delta_pct']:+.1f}%", body_style),
                    Paragraph(f"<b>{d['arrow']}</b>", body_style),
                    Paragraph(f"<font color='{'#DC2626' if d['is_significant'] else '#16A34A'}'><b>{d['status']}</b></font>", body_style)
                ])
            delta_table = Table(delta_table_data, colWidths=[120, 90, 90, 70, 40, 110])
            delta_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(delta_table)
        else:
            story.append(Paragraph("<i>No historical baseline available for this frequency band. Baseline comparison skipped.</i>", body_style))
        story.append(Spacer(1, 8))
        
        # Section 5: Detected Anomalies
        story.append(Paragraph(f"5. Anomaly Investigation Log ({len(anomalies)} events)", section_style))
        if anomalies:
            anom_data = [
                [
                    Paragraph("<b>SEVERITY</b>", body_style),
                    Paragraph("<b>AFFECTED PARAMETER</b>", body_style),
                    Paragraph("<b>OBSERVED VALUE</b>", body_style),
                    Paragraph("<b>ENGINEERING REASON</b>", body_style)
                ]
            ]
            for a in anomalies:
                sev_color = '#DC2626' if a['severity'] in ['CRITICAL', 'HIGH'] else '#D97706'
                anom_data.append([
                    Paragraph(f"<font color='{sev_color}'><b>{a['severity']}</b></font>", body_style),
                    Paragraph(a['affected_parameter'], body_style),
                    Paragraph(a['observed_value'], body_style),
                    Paragraph(a['reason'], body_style)
                ])
            anom_table = Table(anom_data, colWidths=[70, 110, 100, 240])
            anom_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(anom_table)
        else:
            story.append(Paragraph("<b>No anomalies detected.</b> All measured parameters fall within nominal mission thresholds.", body_style))
            
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=6))
        story.append(Paragraph("<b>CONFIDENTIAL</b> | Automated Report generated by Signal Analysis Assistant (NTRO Space Technology Division)", subtitle_style))
        
        # Build Document
        doc.build(story)
        
        # Cleanup temporary plot
        if chart_img_path.exists():
            try:
                os.remove(chart_img_path)
            except Exception:
                pass
                
        return str(pdf_path)

    @staticmethod
    def _create_chart_image(sig: np.ndarray, sample_rate: float, save_path: str):
        fig, axes = plt.subplots(1, 3, figsize=(11, 4), dpi=150)
        plt.subplots_adjust(wspace=0.3, bottom=0.2, top=0.88, left=0.08, right=0.96)
        
        # Time array
        n = min(len(sig), 50000)
        sig_chunk = sig[:n]
        t = np.arange(n) / sample_rate
        
        # 1. Waveform
        ax1 = axes[0]
        if np.iscomplexobj(sig_chunk):
            ax1.plot(t[:1000] * 1000, sig_chunk.real[:1000], label='I (In-phase)', color='#0284C7', lw=0.9)
            ax1.plot(t[:1000] * 1000, sig_chunk.imag[:1000], label='Q (Quadrature)', color='#F59E0B', lw=0.8, alpha=0.8)
            ax1.legend(loc='upper right', fontsize=6)
        else:
            ax1.plot(t[:1000] * 1000, sig_chunk[:1000], color='#0284C7', lw=0.9)
        ax1.set_title("Time-Domain Waveform", fontsize=8, fontweight='bold', color='#1E293B')
        ax1.set_xlabel("Time (ms)", fontsize=7)
        ax1.set_ylabel("Amplitude", fontsize=7)
        ax1.grid(True, linestyle='--', alpha=0.4)
        ax1.tick_params(labelsize=6)
        
        # 2. FFT Spectrum
        ax2 = axes[1]
        n_fft = min(2048, len(sig_chunk))
        if np.iscomplexobj(sig_chunk):
            freqs, psd = matplotlib.mlab.psd(sig_chunk, NFFT=n_fft, Fs=sample_rate)
            freqs = np.fft.fftshift(freqs)
            psd = np.fft.fftshift(psd)
        else:
            freqs, psd = matplotlib.mlab.psd(sig_chunk, NFFT=n_fft, Fs=sample_rate)
        psd_clean = np.maximum(1e-15, np.real(psd))
        psd_db = 10 * np.log10(psd_clean)
        ax2.plot(freqs / 1e3, psd_db, color='#8B5CF6', lw=0.9)
        ax2.set_title("FFT Power Spectrum (PSD)", fontsize=8, fontweight='bold', color='#1E293B')
        ax2.set_xlabel("Frequency (kHz)", fontsize=7)
        ax2.set_ylabel("Power (dB/Hz)", fontsize=7)
        ax2.grid(True, linestyle='--', alpha=0.4)
        ax2.tick_params(labelsize=6)
        
        # 3. Spectrogram
        ax3 = axes[2]
        if np.iscomplexobj(sig_chunk):
            real_data = np.abs(sig_chunk)
        else:
            real_data = sig_chunk
        Pxx, freqs_s, bins, im = ax3.specgram(real_data, NFFT=min(512, len(real_data)), Fs=sample_rate, cmap='plasma')
        ax3.set_title("Spectrogram (Time-Frequency)", fontsize=8, fontweight='bold', color='#1E293B')
        ax3.set_xlabel("Time (s)", fontsize=7)
        ax3.set_ylabel("Frequency (Hz)", fontsize=7)
        ax3.tick_params(labelsize=6)
        
        plt.savefig(save_path, dpi=150)
        plt.close(fig)
