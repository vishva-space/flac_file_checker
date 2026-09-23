from audio.features import Config


def detect_upsampling(cutoff, sample_rate, nyquist, config):
    if sample_rate < config.upsample_min_sample_rate:
        return False, "Sample rate is not high enough for this check"
    if cutoff is None:
        return False, "No reliable cutoff detected"
    if cutoff < config.upsample_content_limit:
        return True, f"Content ceiling {cutoff:.0f} Hz is well below Nyquist {nyquist:.0f} Hz"
    return False, "No strong upsampling indication"