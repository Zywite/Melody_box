import io
import math
import struct
import wave
from pathlib import Path

import pytest


def _generate_tone_wav(duration_sec: float = 0.3, sample_rate: int = 22050, freq: float = 440.0) -> io.BytesIO:
    """Generate a tiny valid WAV file with a pure tone."""
    num_samples = int(sample_rate * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        samples = []
        for sample_index in range(num_samples):
            time_s = sample_index / sample_rate
            value = int(16000 * math.sin(2 * math.pi * freq * time_s))
            samples.append(struct.pack("<h", value))
        wf.writeframes(b"".join(samples))
    buf.seek(0)
    return buf


@pytest.fixture
def tone_wav_path(tmp_path) -> Path:
    """Create a real .wav file on disk and return its path."""
    path = tmp_path / "test_tone.wav"
    data = _generate_tone_wav()
    path.write_bytes(data.getvalue())
    return path


@pytest.fixture
def tone_wav_bytes() -> io.BytesIO:
    """Return a BytesIO with valid WAV content (for uploads)."""
    return _generate_tone_wav()


@pytest.fixture
def tone_wav_bytes2() -> io.BytesIO:
    return _generate_tone_wav(duration_sec=0.2, freq=523.25)
