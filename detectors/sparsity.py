import numpy as np

from audio.features import Config, SignalResult
from scoring.weighted_score import clamp, weighted_contribution


def analyze_spectral_sparsity(frequencies, magnitude_db, cutoff, config):
    if cutoff is None:
        return SignalResult("spectral_sparsity", 0, config.weight_sparsity, 0, "No cutoff detected")

    upper_mask = frequencies > cutoff
    if upper_mask.sum() < 3:
        return SignalResult("spectral_sparsity", 0, config.weight_sparsity, 0, "Insufficient upper-band data")

    sparsity = float(np.mean(magnitude_db[upper_mask, :] < config.noise_threshold_db))
    score = clamp(sparsity * 100.0)
    return SignalResult(
        "spectral_sparsity", score, config.weight_sparsity,
        weighted_contribution(score, config.weight_sparsity),
        f"Silent-bin ratio: {sparsity:.2%}",
    )