import numpy as np

from audio.features import Config, SignalResult
from scoring.weighted_score import clamp, weighted_contribution


def analyze_noise_floor(frequencies, magnitude_db, cutoff, config):
    if cutoff is None:
        return SignalResult("noise_floor", 0, config.weight_noise_floor, 0, "No cutoff detected")

    upper_mask = frequencies > cutoff
    if upper_mask.sum() < 3:
        return SignalResult("noise_floor", 0, config.weight_noise_floor, 0, "Insufficient upper-frequency region")

    median_energy = float(np.median(magnitude_db[upper_mask, :]))
    score = clamp((-median_energy - 25.0) / 35.0 * 100.0)
    return SignalResult(
        "noise_floor", score, config.weight_noise_floor,
        weighted_contribution(score, config.weight_noise_floor),
        f"Median upper-band level: {median_energy:.2f} dB",
    )