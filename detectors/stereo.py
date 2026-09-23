import numpy as np
from scipy.signal import stft

from audio.features import Config, SignalResult
from scoring.weighted_score import clamp, weighted_contribution


def analyze_stereo_correlation(audio, sample_rate, cutoff, config):
    if audio.shape[1] < 2:
        return SignalResult("stereo_correlation", 0, config.weight_stereo, 0, "Mono audio; stereo signal unavailable")

    left_z = stft(audio[:, 0], fs=sample_rate, window="hann", nperseg=config.fft_size, noverlap=config.overlap, boundary=None)[2]
    freqs, _, right_z = stft(audio[:, 1], fs=sample_rate, window="hann", nperseg=config.fft_size, noverlap=config.overlap, boundary=None)
    lower_frequency = 16000.0 if cutoff is None else max(10000.0, cutoff - 2000.0)
    mask = freqs >= lower_frequency
    if mask.sum() < 3:
        return SignalResult("stereo_correlation", 0, config.weight_stereo, 0, "Insufficient upper-band data")

    left_energy = np.abs(left_z[mask, :])
    right_energy = np.abs(right_z[mask, :])
    correlations = []
    for index in range(left_energy.shape[0]):
        x, y = left_energy[index, :], right_energy[index, :]
        if np.std(x) < 1e-8 or np.std(y) < 1e-8:
            continue
        correlation = np.corrcoef(x, y)[0, 1]
        if np.isfinite(correlation):
            correlations.append(correlation)

    if not correlations:
        return SignalResult("stereo_correlation", 0, config.weight_stereo, 0, "Correlation unavailable")

    mean_correlation = float(np.mean(correlations))
    score = clamp((mean_correlation - 0.80) / 0.20 * 100.0)
    return SignalResult(
        "stereo_correlation", score, config.weight_stereo,
        weighted_contribution(score, config.weight_stereo),
        f"Mean upper-band correlation: {mean_correlation:.3f}",
    )