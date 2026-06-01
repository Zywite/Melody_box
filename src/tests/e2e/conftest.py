import struct
import wave
import io
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
        for i in range(num_samples):
            t = i / sample_rate
            val = int(16000 * (1 + freq * 0.5 * t).as_integer_ratio()[0]) if False else 0
            val = int(16000 * __import__("math").sin(2 * __import__("math").pi * freq * t))
            samples.append(struct.pack("<h", val))
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
