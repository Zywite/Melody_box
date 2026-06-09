import json
import logging
from pathlib import Path

import librosa
import numpy as np
from typing_extensions import TypedDict

from app.core.constants import (
    BASS_FREQUENCY_CUTOFF_HZ,
    DEFAULT_FFT_HOP_SIZE,
    DEFAULT_FFT_SIZE,
    ERROR_FFT_NO_RESULT,
    FFT_NORMALIZATION_EPSILON,
    FFT_NORMALIZATION_RANGE,
    FFT_TARGET_SAMPLE_RATE,
    MAX_FFT_INPUT_DURATION_SECONDS,
    MAX_SPECTROGRAM_FRAMES,
    MID_FREQUENCY_CUTOFF_HZ,
    POWER_PERCENT_MULTIPLIER,
    TASK_PROGRESS_COMPLETE,
    TASK_STATUS_DONE,
    TASK_STATUS_FAILED,
)

logger = logging.getLogger(__name__)


class FFTResult(TypedDict):
    duration: float
    sample_rate: int
    channels: int
    bins: list[int]
    spectrogram: list[list[int]]
    bass_power: float
    mid_power: float
    treble_power: float
    fft_size: int
    hop_size: int
    nyquist: float
    bin_count: int


class FFTService:
    @staticmethod
    def compute_fft_from_file(
        file_path: str, fft_size: int = DEFAULT_FFT_SIZE, hop_size: int = DEFAULT_FFT_HOP_SIZE
    ) -> FFTResult | None:
        """
        Compute FFT analysis from an audio file.
        Returns a dictionary with FFT data that can be stored as JSON.
        """
        try:
            # Handle old paths (src/music_storage/) vs new paths (data/music/)
            filename = Path(file_path).name
            parents = Path(file_path).parents
            if len(parents) >= 3:
                base_dir = parents[2]  # Go up to project root
                new_path = base_dir / "data" / "music" / filename
                if new_path.exists():
                    file_path = str(new_path)
                else:
                    file_path = str(Path(file_path).resolve())
            else:
                file_path = str(Path(file_path).resolve())

            # Load audio file. Downsample and clip duration to keep memory
            # bounded for very long tracks (raw float32 at 44.1kHz mono is
            # ~176KB/s; a 10-minute track would be ~100MB).
            y, sr = librosa.load(
                file_path,
                sr=FFT_TARGET_SAMPLE_RATE,
                mono=True,
                duration=MAX_FFT_INPUT_DURATION_SECONDS,
            )

            duration = len(y) / sr

            # Compute full FFT for the entire file (average spectrum)
            D = np.abs(librosa.stft(y, n_fft=fft_size, hop_length=hop_size))
            D_db = librosa.amplitude_to_db(D, ref=np.max)

            # Average spectrogram to get single spectrum
            avg_spectrum = np.mean(D_db, axis=1)

            # Normalize to 0-255 range for storage
            avg_spectrum_norm = np.clip(
                (avg_spectrum - avg_spectrum.min())
                / (avg_spectrum.max() - avg_spectrum.min() + FFT_NORMALIZATION_EPSILON)
                * FFT_NORMALIZATION_RANGE,
                0,
                FFT_NORMALIZATION_RANGE,
            ).astype(int)

            # Compute spectrogram for visualization (reduce frames for storage)
            num_frames = min(D_db.shape[1], MAX_SPECTROGRAM_FRAMES)
            frame_indices = np.linspace(0, D_db.shape[1] - 1, num_frames).astype(int)
            spectrogram_data = D_db[:, frame_indices]

            # Normalize spectrogram
            spec_min, spec_max = spectrogram_data.min(), spectrogram_data.max()
            spectrogram_norm = np.clip(
                (spectrogram_data - spec_min)
                / (spec_max - spec_min + FFT_NORMALIZATION_EPSILON)
                * FFT_NORMALIZATION_RANGE,
                0,
                FFT_NORMALIZATION_RANGE,
            ).astype(int)

            # Compute frequency bands
            nyquist = sr / 2
            bins = len(avg_spectrum_norm)
            bin_width = nyquist / bins

            bass_end = int(BASS_FREQUENCY_CUTOFF_HZ / bin_width)
            mid_end = int(MID_FREQUENCY_CUTOFF_HZ / bin_width)

            bass_power = float(np.mean(avg_spectrum_norm[:bass_end])) if bass_end > 0 else 0.0
            mid_power = float(np.mean(avg_spectrum_norm[bass_end:mid_end])) if mid_end > bass_end else 0.0
            treble_power = float(np.mean(avg_spectrum_norm[mid_end:])) if mid_end < len(avg_spectrum_norm) else 0.0

            # Normalize powers to percentage
            total_power = bass_power + mid_power + treble_power + FFT_NORMALIZATION_EPSILON

            result: FFTResult = {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1,
                "bins": avg_spectrum_norm.tolist(),
                "spectrogram": spectrogram_norm.tolist(),
                "bass_power": (bass_power / total_power) * POWER_PERCENT_MULTIPLIER,
                "mid_power": (mid_power / total_power) * POWER_PERCENT_MULTIPLIER,
                "treble_power": (treble_power / total_power) * POWER_PERCENT_MULTIPLIER,
                "fft_size": fft_size,
                "hop_size": hop_size,
                "nyquist": nyquist,
                "bin_count": bins,
            }

            return result

        except (OSError, ValueError) as e:
            logger.error("Error computing FFT: %s", e)
            return None
        except Exception as e:
            logger.exception("Unexpected error computing FFT: %s", e)
            return None

    @staticmethod
    def get_fft_data_json(fft_data: str | None) -> FFTResult | None:
        """
        Parse FFT data from JSON string stored in database.
        """
        if not fft_data:
            return None
        try:
            return json.loads(fft_data)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def to_json(result: FFTResult) -> str:
        """
        Convert FFT result to JSON string for storage.
        """
        return json.dumps(result)

    @staticmethod
    async def process_and_store_fft(db, song, task=None):
        """
        Compute FFT, store result on song and task, commit, and cache.
        Shared by worker.py and songs.py route fallback.

        The CPU-bound librosa computation runs in a thread to avoid
        blocking the async event loop.
        """
        import asyncio

        result = await asyncio.to_thread(FFTService.compute_fft_from_file, song.file_path)
        if result:
            fft_json = FFTService.to_json(result)
            song.fft_data = fft_json
            if task:
                task.status = TASK_STATUS_DONE
                task.result = result
                task.progress = TASK_PROGRESS_COMPLETE
            db.commit()
            from app.core.redis_helper import cache_set_fft

            await cache_set_fft(song.id, fft_json)
        else:
            if task:
                task.status = TASK_STATUS_FAILED
                task.error = ERROR_FFT_NO_RESULT
                db.commit()
        return result
