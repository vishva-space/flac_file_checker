from audio.features import AnalysisResult


def print_result(result: AnalysisResult):
    print("\n" + "=" * 60)
    print("FLAC LOSSLESS AUDIO CHECKER")
    print("=" * 60)
    print(f"File: {result.file}")
    print(f"Sample rate: {result.audio.sample_rate} Hz")
    print(f"Channels: {result.audio.channels}")
    print(f"Duration: {result.audio.duration:.2f} seconds")
    print(f"Subtype: {result.audio.subtype}")
    print(f"Nyquist: {result.nyquist_hz:.0f} Hz")
    print(f"Cutoff: {result.cutoff_hz:.0f} Hz" if result.cutoff_hz is not None else "Cutoff: Unknown")
    print("\n" + "-" * 60)
    print(f"VERDICT: {result.verdict}")
    print(f"SCORE: {result.score:.2f}/100")
    print(f"CONFIDENCE: {result.confidence}")
    print("-" * 60)
    print("\nSignal breakdown:")

    for signal in result.signals:
        print(f"\n{signal.name}")
        print(f"  Score: {signal.score:.2f}/100")
        print(f"  Weight: {signal.weight:.2f}")
        print(f"  Contribution: {signal.contribution:.2f}")
        print(f"  Details: {signal.explanation}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    print("\n" + "=" * 60)