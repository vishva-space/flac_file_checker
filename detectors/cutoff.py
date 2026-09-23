import numpy as np

from audio.features import Config, SignalResult, get_frequency_mask
from scoring.weighted_score import clamp, weighted_contribution


def get_cutoff_per_frame(frequencies, magnitude_db, config):
    high_frequency_mask = frequencies >= config.min_frequency
    high_freqs = frequencies[high_frequency_mask]
    high_energy = magnitude_db[high_frequency_mask, :]
    cutoffs = []

    for frame in high_energy.T:
        valid = np.where(frame > config.noise_threshold_db)[0]
        if len(valid) > 0:
            cutoffs.append(high_freqs[valid[-1]])

    return np.asarray(cutoffs)


def detect_cutoff(frequencies, magnitude_db, config):
    cutoffs = get_cutoff_per_frame(frequencies, magnitude_db, config)
    if len(cutoffs) == 0:
        return None, cutoffs
    return float(np.percentile(cutoffs, 25)), cutoffs


def analyze_cutoff_sharpness(frequencies, magnitude_db, cutoff, config):
    if cutoff is None:
        return SignalResult("cutoff_sharpness", 0, config.weight_sharpness, 0, "No measurable cutoff")

    mask = get_frequency_mask(frequencies, cutoff - 1500, cutoff + 1500)
    if np.sum(mask) < 3:
        return SignalResult("cutoff_sharpness", 0, config.weight_sharpness, 0, "Insufficient frequency resolution")

    average_energy = np.mean(magnitude_db[mask, :], axis=1)
    if len(average_energy) >= 3:
        average_energy = np.convolve(average_energy, np.ones(3) / 3, mode="same")

    drop = max(0.0, -np.min(np.diff(average_energy)))
    score = clamp((drop - 2.0) / 8.0 * 100.0)
    return SignalResult(
        "cutoff_sharpness", score, config.weight_sharpness,
        weighted_contribution(score, config.weight_sharpness),
        f"Steepest spectral drop: {drop:.2f} dB/bin",
    )


def analyze_cutoff_consistency(cutoffs, config):
    if len(cutoffs) < config.min_analysis_frames:
        return SignalResult("cutoff_consistency", 0, config.weight_consistency, 0, "Too few valid frames")

    median_cutoff = np.median(cutoffs)
    mad = np.median(np.abs(cutoffs - median_cutoff))
    score = clamp((500.0 - mad) / 500.0 * 100.0)
    return SignalResult(
        "cutoff_consistency", score, config.weight_consistency,
        weighted_contribution(score, config.weight_consistency),
        f"Median absolute deviation: {mad:.2f} Hz",
    )


def analyze_cutoff_position(cutoff, nyquist, config):
    if cutoff is None:
        return SignalResult("cutoff_position", 0, config.weight_cutoff_position, 0, "No cutoff detected")

    ratio = cutoff / nyquist
    if ratio >= 0.93:
        score = 0.0
    elif ratio >= 0.85:
        score = 30.0
    elif ratio >= 0.75:
        score = 60.0
    else:
        score = 100.0

    return SignalResult(
        "cutoff_position", score, config.weight_cutoff_position,
        weighted_contribution(score, config.weight_cutoff_position),
        f"Cutoff/Nyquist ratio: {ratio:.3f}",
    )