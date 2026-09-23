from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.signal import stft


@dataclass
class Config:
    fft_size: int = 4096
    overlap: int = 2048
    min_frequency: float = 10000.0
    noise_threshold_db: float = -60.0
    min_duration: float = 10.0
    min_analysis_frames: int = 10
    unknown_score_low: float = 35.0
    transcoded_score_high: float = 65.0
    upsample_min_sample_rate: int = 88200
    upsample_content_limit: float = 20000.0
    ambiguous_cutoff_ratio: float = 0.55
    weight_sharpness: float = 25.0
    weight_noise_floor: float = 20.0
    weight_sparsity: float = 15.0
    weight_consistency: float = 15.0
    weight_stereo: float = 10.0
    weight_cutoff_position: float = 15.0


@dataclass
class AudioInfo:
    sample_rate: int
    channels: int
    duration: float
    frames: int
    subtype: str


@dataclass
class SignalResult:
    name: str
    score: float
    weight: float
    contribution: float
    explanation: str


@dataclass
class AnalysisResult:
    file: str
    audio: AudioInfo
    verdict: str
    score: float
    confidence: str
    cutoff_hz: Optional[float]
    nyquist_hz: float
    signals: list
    warnings: list


def calculate_stft(audio: np.ndarray, sample_rate: int, config: Config):
    mono = np.mean(audio, axis=1)
    nperseg = min(config.fft_size, len(mono))

    if nperseg < 256:
        raise ValueError("Audio is too short for spectral analysis")

    noverlap = min(config.overlap, nperseg // 2)
    frequencies, times, spectrum = stft(
        mono,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
    )
    magnitude_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
    frame_max = np.max(magnitude_db, axis=0, keepdims=True)
    return frequencies, times, magnitude_db - frame_max


def get_frequency_mask(frequencies: np.ndarray, low: float, high: float):
    return (frequencies >= low) & (frequencies <= high)