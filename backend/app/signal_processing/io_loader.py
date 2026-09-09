import os
import wave
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from typing import Tuple, Dict, Any, Optional

class SignalLoader:
    """Robust IO Loader for WAV, IQ, and raw binary telemetry signals."""
    
    @staticmethod
    def load_file(
        file_path: str,
        file_type: Optional[str] = None,
        sample_rate: Optional[float] = None,
        iq_format: str = "float32",
        center_freq: float = 0.0,
        max_samples: int = 2000000  # Load up to 2M samples for interactive analysis
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Signal file not found: {file_path}")
            
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")
            
        ext = path.suffix.lower().lstrip(".")
        if file_type:
            ext = file_type.lower().lstrip(".")
            
        if ext in ["wav", "wave"]:
            return SignalLoader._load_wav(file_path, max_samples)
        elif ext in ["iq", "raw", "bin", "dat", "fc32", "sc16", "sc8", "cu8"]:
            return SignalLoader._load_iq(file_path, sample_rate, iq_format, center_freq, max_samples)
        else:
            # Attempt auto-detection
            try:
                return SignalLoader._load_wav(file_path, max_samples)
            except Exception:
                return SignalLoader._load_iq(file_path, sample_rate, iq_format, center_freq, max_samples)

    @staticmethod
    def _load_wav(file_path: str, max_samples: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        try:
            sr, data = wavfile.read(file_path)
        except Exception as e:
            raise ValueError(f"Corrupted or invalid WAV file: {str(e)}")
            
        file_size = os.path.getsize(file_path)
        channels = 1
        is_complex = False
        
        # Format conversion
        if data.ndim > 1:
            channels = data.shape[1]
            if channels == 2:
                # Can be treated as complex IQ if both channels present (I on Left, Q on Right) or stereo
                # Convert to complex for full analytic power
                i_channel = data[:, 0].astype(np.float64)
                q_channel = data[:, 1].astype(np.float64)
                # Normalize if integer
                if np.issubdtype(data.dtype, np.integer):
                    max_val = float(np.iinfo(data.dtype).max)
                    i_channel /= max_val
                    q_channel /= max_val
                signal_data = i_channel + 1j * q_channel
                is_complex = True
            else:
                signal_data = data[:, 0].astype(np.float64)
                if np.issubdtype(data.dtype, np.integer):
                    signal_data /= float(np.iinfo(data.dtype).max)
        else:
            signal_data = data.astype(np.float64)
            if np.issubdtype(data.dtype, np.integer):
                signal_data /= float(np.iinfo(data.dtype).max)
                
        total_samples = len(signal_data)
        if total_samples > max_samples:
            # Take representative chunk
            signal_data = signal_data[:max_samples]
            
        duration = float(total_samples) / float(sr)
        
        metadata = {
            "file_type": "wav",
            "sample_rate": float(sr),
            "num_samples": total_samples,
            "loaded_samples": len(signal_data),
            "duration_sec": round(duration, 4),
            "channels": channels,
            "is_complex": is_complex,
            "iq_format": "wav_pcm",
            "file_size_bytes": file_size,
            "bit_depth": str(data.dtype)
        }
        return signal_data, metadata

    @staticmethod
    def _load_iq(
        file_path: str,
        sample_rate: Optional[float],
        iq_format: str,
        center_freq: float,
        max_samples: int
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        file_size = os.path.getsize(file_path)
        sr = float(sample_rate) if sample_rate and sample_rate > 0 else 1000000.0  # 1 MSps default
        
        iq_format = iq_format.lower()
        if "16" in iq_format or iq_format in ["sc16", "int16"]:
            # Complex int16: interleaved (I0, Q0, I1, Q1, ...) as int16
            raw_data = np.fromfile(file_path, dtype=np.int16, count=max_samples * 2)
            if len(raw_data) % 2 != 0:
                raw_data = raw_data[:-1]
            i_samples = raw_data[0::2].astype(np.float64) / 32768.0
            q_samples = raw_data[1::2].astype(np.float64) / 32768.0
            signal_data = i_samples + 1j * q_samples
            actual_format = "int16"
        elif "8" in iq_format or iq_format in ["sc8", "cu8", "int8", "uint8"]:
            if "u" in iq_format or "cu8" in iq_format or "uint8" in iq_format:
                raw_data = np.fromfile(file_path, dtype=np.uint8, count=max_samples * 2)
                raw_data = raw_data.astype(np.float64) - 127.5
                raw_data /= 127.5
            else:
                raw_data = np.fromfile(file_path, dtype=np.int8, count=max_samples * 2)
                raw_data = raw_data.astype(np.float64) / 128.0
            if len(raw_data) % 2 != 0:
                raw_data = raw_data[:-1]
            signal_data = raw_data[0::2] + 1j * raw_data[1::2]
            actual_format = "int8"
        else:
            # Default: float32 interleaved (I0, Q0, I1, Q1, ...)
            raw_data = np.fromfile(file_path, dtype=np.float32, count=max_samples * 2)
            if len(raw_data) % 2 != 0:
                raw_data = raw_data[:-1]
            if len(raw_data) == 0:
                raise ValueError("Could not parse binary IQ data - file too small or empty.")
            signal_data = (raw_data[0::2] + 1j * raw_data[1::2]).astype(np.complex128)
            actual_format = "float32"
            
        bytes_per_sample = 8 if actual_format == "float32" else (4 if actual_format == "int16" else 2)
        total_samples = file_size // bytes_per_sample
        if total_samples <= 0:
            total_samples = len(signal_data)
            
        duration = float(total_samples) / float(sr)
        
        metadata = {
            "file_type": "iq",
            "sample_rate": sr,
            "num_samples": total_samples,
            "loaded_samples": len(signal_data),
            "duration_sec": round(duration, 4),
            "channels": 2,
            "is_complex": True,
            "iq_format": actual_format,
            "file_size_bytes": file_size,
            "center_freq_hz": center_freq
        }
        return signal_data, metadata
