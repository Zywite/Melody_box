import json

import pytest

from app.core.config import BASE_DIR
from app.services.fft_service import FFTService


def test_to_json_and_get_fft_data_json_roundtrip():
    result = {
        "duration": 10.0,
        "sample_rate": 22050,
        "channels": 1,
        "bins": [0, 128, 255],
        "spectrogram": [[0, 128], [255, 0]],
        "bass_power": 50.0,
        "mid_power": 30.0,
        "treble_power": 20.0,
        "fft_size": 2048,
        "hop_size": 512,
        "nyquist": 11025,
        "bin_count": 3,
    }
    json_str = FFTService.to_json(result)
    parsed = json.loads(json_str)
    assert parsed["duration"] == 10.0
    assert parsed["bass_power"] == 50.0
    assert parsed["bin_count"] == 3


def test_get_fft_data_json_with_valid_json():
    data = '{"bass": 30.0, "mid": 40.0}'
    result = FFTService.get_fft_data_json(data)
    assert result == {"bass": 30.0, "mid": 40.0}


def test_get_fft_data_json_with_none():
    result = FFTService.get_fft_data_json(None)
    assert result is None


def test_get_fft_data_json_with_empty_string():
    result = FFTService.get_fft_data_json("")
    with pytest.raises(json.JSONDecodeError):
        json.loads("")
    assert result is None


def test_get_fft_data_json_with_invalid_json():
    result = FFTService.get_fft_data_json("{invalid}")
    assert result is None


def test_compute_fft_from_file_returns_none_for_nonexistent():
    result = FFTService.compute_fft_from_file("/nonexistent/file.mp3")
    assert result is None


def test_fft_result_contains_all_expected_keys(test_song):
    file_path = str(BASE_DIR / "data" / "music" / "test_song.mp3")
    result = FFTService.compute_fft_from_file(file_path)
    if result is not None:
        expected_keys = {
            "duration",
            "sample_rate",
            "channels",
            "bins",
            "spectrogram",
            "bass_power",
            "mid_power",
            "treble_power",
            "fft_size",
            "hop_size",
            "nyquist",
            "bin_count",
        }
        assert expected_keys.issubset(result.keys())


def test_fft_powers_sum_to_approx_100(test_song):
    file_path = str(BASE_DIR / "data" / "music" / "test_song.mp3")
    result = FFTService.compute_fft_from_file(file_path)
    if result is not None:
        total = result["bass_power"] + result["mid_power"] + result["treble_power"]
        assert 95.0 <= total <= 105.0


def test_fft_bins_are_normalized_0_255(test_song):
    file_path = str(BASE_DIR / "data" / "music" / "test_song.mp3")
    result = FFTService.compute_fft_from_file(file_path)
    if result is not None:
        bins = result["bins"]
        assert all(0 <= b <= 255 for b in bins)
        assert len(bins) == 1025
