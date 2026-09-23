import argparse
from pathlib import Path

from audio.features import AnalysisResult, Config, calculate_stft
from audio.loader import load_audio
from detectors.cutoff import (
    analyze_cutoff_consistency,
    analyze_cutoff_position,
    analyze_cutoff_sharpness,
    detect_cutoff,
)
from detectors.noise_floor import analyze_noise_floor
from detectors.sparsity import analyze_spectral_sparsity
from detectors.stereo import analyze_stereo_correlation
from detectors.upsampling import detect_upsampling
from reports.json_report import write_error_report, write_json_report, write_verdict_log
from scoring.weighted_score import calculate_confidence, calculate_score, classify_verdict


def assess_data_quality(audio, metadata, cutoff, cutoffs, config):
    warnings = []
    if metadata.duration < config.min_duration:
        warnings.append("Audio is shorter than recommended analysis duration")
    rms = (audio ** 2).mean() ** 0.5
    if rms < 1e-5:
        warnings.append("Audio is extremely quiet")
    if len(cutoffs) < config.min_analysis_frames:
        warnings.append("Insufficient valid cutoff frames")
    if cutoff is None:
        warnings.append("No reliable frequency cutoff found")
    return warnings


def analyze_file(file_path: str, config: Config):
    audio, metadata = load_audio(file_path)
    sample_rate = metadata.sample_rate
    nyquist = sample_rate / 2.0
    frequencies, _, magnitude_db = calculate_stft(audio, sample_rate, config)
    cutoff, cutoffs = detect_cutoff(frequencies, magnitude_db, config)
    warnings = assess_data_quality(audio, metadata, cutoff, cutoffs, config)
    signals = [
        analyze_cutoff_sharpness(frequencies, magnitude_db, cutoff, config),
        analyze_noise_floor(frequencies, magnitude_db, cutoff, config),
        analyze_spectral_sparsity(frequencies, magnitude_db, cutoff, config),
        analyze_cutoff_consistency(cutoffs, config),
        analyze_stereo_correlation(audio, sample_rate, cutoff, config),
        analyze_cutoff_position(cutoff, nyquist, config),
    ]
    total_score = calculate_score(signals)
    upsampled, upsample_explanation = detect_upsampling(cutoff, sample_rate, nyquist, config)
    if upsampled:
        warnings.append(upsample_explanation)

    verdict = classify_verdict(
        total_score,
        warnings,
        upsampled,
        config,
        signals,
        cutoff,
        nyquist,
    )
    return AnalysisResult(
        file=str(file_path),
        audio=metadata,
        verdict=verdict,
        score=total_score,
        confidence=calculate_confidence(total_score, warnings),
        cutoff_hz=cutoff,
        nyquist_hz=nyquist,
        signals=signals,
        warnings=warnings,
    )


def find_flac_files(input_directory: Path):
    return sorted(
        path for path in input_directory.rglob("*")
        if path.is_file() and path.suffix.lower() == ".flac"
    )


def process_directory(input_directory: Path, log_directory: Path, config: Config):
    flac_files = find_flac_files(input_directory)
    results = []
    verdict_entries = []

    log_directory.mkdir(parents=True, exist_ok=True)
    individual_results_directory = log_directory / "individual_results"
    total_files = len(flac_files)
    for index, file_path in enumerate(flac_files, start=1):
        print(f"Processing: {file_path.name} ({index}/{total_files})")
        relative_name = file_path.relative_to(input_directory)
        log_name = "__".join(relative_name.with_suffix(".json").parts)
        try:
            result = analyze_file(str(file_path), config)
        except Exception as error:
            print(f"ERROR: Analysis failed for {file_path}: {error}")
            write_error_report(
                file_path,
                error,
                individual_results_directory / log_name,
            )
            verdict_entries.append((file_path.name, "UNKNOWN"))
            continue

        write_json_report(result, individual_results_directory / log_name)
        results.append(result)
        verdict_entries.append((file_path.name, result.verdict))

    write_verdict_log(verdict_entries, log_directory / "verdicts.log")
    return results


def main():
    parser = argparse.ArgumentParser(description="Advanced FLAC Lossless Audio Checker")
    parser.add_argument("directory", help="Directory containing FLAC files")
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="Separate directory for per-file logs and verdicts.log",
    )
    args = parser.parse_args()
    input_directory = Path(args.directory)

    if not input_directory.is_dir():
        print(f"ERROR: Directory not found: {input_directory}")
        return 1

    results = process_directory(input_directory, Path(args.log_dir), Config())
    if not results:
        print(f"No FLAC files found in: {input_directory}")
        return 1

    print(f"\nLogs saved to: {args.log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())