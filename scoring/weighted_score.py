from audio.features import AnalysisResult, Config


def clamp(value: float, low=0.0, high=100.0):
    return float(max(low, min(high, value)))


def weighted_contribution(score: float, weight: float):
    return score * weight / 100.0


def calculate_score(signals):
    return clamp(sum(signal.contribution for signal in signals))


def classify_verdict(score, warnings, upsampled, config: Config, signals=None, cutoff=None, nyquist=None):
    if upsampled:
        return "UPSAMPLED"
    if len(warnings) >= 2:
        return "UNKNOWN"

    if signals is not None:
        consistency = next(
            (signal for signal in signals if signal.name == "cutoff_consistency"),
            None,
        )
        if consistency is not None and consistency.score < 35.0:
            if cutoff is not None and nyquist is not None:
                if cutoff / nyquist < config.ambiguous_cutoff_ratio:
                    return "UNKNOWN"
            return "CLEAN"

    if score >= config.transcoded_score_high:
        return "TRANSCODED"
    if score <= config.unknown_score_low:
        return "CLEAN"
    return "UNKNOWN"


def calculate_confidence(score: float, warnings):
    if len(warnings) >= 2:
        return "LOW"
    if score >= 80 or score <= 20:
        return "MODERATE"
    return "LOW"