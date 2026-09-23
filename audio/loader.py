import numpy as np
import soundfile as sf

from .features import AudioInfo


def load_audio(file_path: str):
    info = sf.info(file_path)

    if info.format != "FLAC":
        raise ValueError(f"Expected FLAC format, got {info.format}")
    if info.frames <= 0:
        raise ValueError("Audio file is empty")

    audio, sample_rate = sf.read(
        file_path,
        always_2d=True,
        dtype="float32",
    )

    if not np.isfinite(audio).all():
        raise ValueError("Audio contains invalid numerical values")

    metadata = AudioInfo(
        sample_rate=sample_rate,
        channels=info.channels,
        duration=info.duration,
        frames=info.frames,
        subtype=info.subtype,
    )
    return audio, metadata