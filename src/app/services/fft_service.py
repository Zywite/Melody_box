import numpy as np
import librosa
import json
from pathlib import Path
from typing import Optional, Dict, Any

class FFTService:
    @staticmethod
    def compute_fft_from_file(file_path: str, fft_size: int = 2048, hop_size: int = 512) -> Optional[Dict[str, Any]]:
        """
        Compute FFT analysis from an audio file.
        Returns a dictionary with FFT data that can be stored as JSON.
        """
        try:
            file_path = str(Path(file_path).resolve())
            
            # Load audio file
            y, sr = librosa.load(file_path, sr=None, mono=True)
            
            duration = len(y) / sr
            
            # Compute full FFT for the entire file (average spectrum)
            D = np.abs(librosa.stft(y, n_fft=fft_size, hop_length=hop_size))
            D_db = librosa.amplitude_to_db(D, ref=np.max)
            
            # Average spectrogram to get single spectrum
            avg_spectrum = np.mean(D_db, axis=1)
            
            # Normalize to 0-255 range for storage
            avg_spectrum_norm = np.clip((avg_spectrum - avg_spectrum.min()) / (avg_spectrum.max() - avg_spectrum.min() + 1e-10) * 255, 0, 255).astype(int)
            
            # Compute spectrogram for visualization (reduce frames for storage)
            num_frames = min(D_db.shape[1], 200)  # Limit frames for storage
            frame_indices = np.linspace(0, D_db.shape[1] - 1, num_frames).astype(int)
            spectrogram_data = D_db[:, frame_indices]
            
            # Normalize spectrogram
            spec_min, spec_max = spectrogram_data.min(), spectrogram_data.max()
            spectrogram_norm = np.clip((spectrogram_data - spec_min) / (spec_max - spec_min + 1e-10) * 255, 0, 255).astype(int)
            
            # Compute frequency bands
            nyquist = sr / 2
            bins = len(avg_spectrum_norm)
            bin_width = nyquist / bins
            
            bass_end = int(250 / bin_width)
            mid_end = int(2000 / bin_width)
            
            bass_power = float(np.mean(avg_spectrum_norm[:bass_end])) if bass_end > 0 else 0.0
            mid_power = float(np.mean(avg_spectrum_norm[bass_end:mid_end])) if mid_end > bass_end else 0.0
            treble_power = float(np.mean(avg_spectrum_norm[mid_end:])) if mid_end < len(avg_spectrum_norm) else 0.0
            
            # Normalize powers to percentage
            total_power = bass_power + mid_power + treble_power + 1e-10
            
            result = {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1,
                "bins": avg_spectrum_norm.tolist(),
                "spectrogram": spectrogram_norm.tolist(),
                "bass_power": (bass_power / total_power) * 100,
                "mid_power": (mid_power / total_power) * 100,
                "treble_power": (treble_power / total_power) * 100,
                "fft_size": fft_size,
                "hop_size": hop_size,
                "nyquist": nyquist,
                "bin_count": bins
            }
            
            return result
            
        except Exception as e:
            print(f"Error computing FFT: {e}")
            return None
    
    @staticmethod
    def get_fft_data_json(fft_data: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Parse FFT data from JSON string stored in database.
        """
        if not fft_data:
            return None
        try:
            return json.loads(fft_data)
        except Exception:
            return None
    
    @staticmethod
    def to_json(result: Dict[str, Any]) -> str:
        """
        Convert FFT result to JSON string for storage.
        """
        return json.dumps(result)
