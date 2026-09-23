# FLAC Checker

Reference website: [BRIZM Lossless Audio Checker](https://brizm.dev/lossless-audio-checker/)

FLAC Checker is a command-line tool that examines FLAC files for spectral evidence that may indicate lossy transcoding or upsampling.

The project does not decode a hidden provenance tag and cannot prove where an audio file came from. It analyzes the audio spectrum and reports whether the evidence looks clean, transcoded, upsampled, or ambiguous.

## What The Project Does

For every FLAC file, the analyzer:

1. Loads the file and validates that it is a readable FLAC.
2. Reads the sample rate, channel count, duration, frame count, and subtype.
3. Calculates a short-time Fourier transform (STFT).
4. Estimates the highest sustained frequency content and possible cutoff.
5. Measures cutoff sharpness, upper-band noise floor, spectral sparsity, cutoff consistency, stereo correlation, and cutoff position relative to Nyquist frequency.
6. Combines the detector results into a weighted score.
7. Writes a detailed JSON report and one summary verdict.

The cutoff-consistency check is important. A steep edge by itself is not enough to call a file transcoded: a naturally band-limited or mastered lossless file can have a similar shape. Unstable or ambiguous evidence is reported as `UNKNOWN` or `CLEAN` depending on the measured cutoff position.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| `CLEAN` | No reliable codec-wall evidence was found. This does not prove the file has never been transcoded. |
| `TRANSCODED` | A stable spectral cutoff and supporting evidence were found. |
| `UPSAMPLED` | The sample rate is high, but the measured content ceiling is far below Nyquist. |
| `UNKNOWN` | The evidence is ambiguous, the cutoff is unstable, or the file could not be analyzed reliably. |

## Project Structure

```text
flac_checker.py          CLI and directory-processing workflow

audio/
	loader.py              FLAC loading and metadata validation
	stft.py                STFT exports
	features.py            Shared data classes and signal helpers

detectors/
	cutoff.py              Cutoff, sharpness, consistency, and position checks
	noise_floor.py         Upper-band noise-floor detector
	sparsity.py            Upper-band spectral sparsity detector
	stereo.py              Upper-band stereo correlation detector
	upsampling.py          High-sample-rate upsampling detector

scoring/
	weighted_score.py      Weighted score and verdict classification

reports/
	console.py             Human-readable report formatting
	json_report.py         Per-file and summary log writers

tests/
	test_cutoff.py
	test_directory_processing.py
	test_loader.py
	test_scoring.py
```

## Requirements

- Python 3.12 or newer is recommended.
- Dependencies are listed in `requirements.txt`.

Create and install into a virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
```

On Linux, `soundfile` may also require the system `libsndfile` package. The exact package name depends on the distribution.

## Analyze A Directory

The input is a directory, not an individual file. FLAC files are found recursively, so nested folders are supported.

```bash
.venv/bin/python3 flac_checker.py /path/to/flac-directory --log-dir logs
```

While running, the command prints only progress:

```text
Processing: 123.flac (1/10)
Processing: another-file.flac (2/10)
```

Detailed signal results are not printed to the terminal. They are saved as JSON logs.

## Check The Included Samples

The repository includes these sample files under `sample_files/`:

```text
sample_files/
	fake_flac.flac
	orginal_flac_1.flac
	original_flac_2.flac
```

Run the sample set with:

```bash
.venv/bin/python3 flac_checker.py sample_files --log-dir logs
```

The filename `orginal_flac_1.flac` intentionally follows the spelling of the file currently present in the sample directory. File names do not affect classification.

## Generated Logs

The default output is:

```text
logs/
	verdicts.log
	individual_results/
		fake_flac.json
		orginal_flac_1.json
		original_flac_2.json
```

`logs/verdicts.log` contains one concise line per input file:

```text
fake_flac.flac -> UNKNOWN
orginal_flac_1.flac -> CLEAN
original_flac_2.flac -> TRANSCODED
```

Each file in `logs/individual_results/` contains the sample rate, channels, duration, cutoff, Nyquist frequency, score, confidence, warnings, and every detector contribution. If a file cannot be analyzed, its JSON report contains `UNKNOWN` and the error message.

Generated logs are excluded from Git by `.gitignore`.

## Compare With The Reference Website

The reference website is used as an independent visual and verdict comparison. It should be treated as a comparison tool, not as an implementation dependency.

To compare a file:

1. Run this project on the directory containing the file.
2. Open the same FLAC file in the reference website.
3. Compare the website's headline verdict with the matching line in `logs/verdicts.log`.
4. If the verdicts differ, open the matching JSON file under `logs/individual_results/`.
5. Compare the website's spectrum with `cutoff_hz`, `nyquist_hz`, cutoff consistency, upper-band noise floor, sparsity, and warnings.

Example comparison:

```text
Reference website: NO TRANSCODE FOUND
This project:      CLEAN
```

This is an expected type of comparison for a file whose content reaches a plausible frequency ceiling but does not show a stable codec wall. A website result such as `UNKNOWN` should generally correspond to ambiguous or unstable evidence in the JSON report.

The reference website URL is not required by this command-line tool and is intentionally not hard-coded into the repository. Replace the comparison site with the specific website used by your evaluation workflow.

## What This Tool Cannot See

- A 320 kbps MP3 or a 256+ kbps AAC encoded without a low-pass can keep the full band and leave no spectral trace.
- A lossless file with a steep low-pass, such as an EQ'd stem or bass track, can look like a codec wall. The tool abstains rather than guesses.
- Very quiet material, with peaks under about -45 dBFS, narrows the analysis window; the cutoff reading can walk down the slope.
- Generation loss without a wall, such as a re-encode of a re-encode, cannot be distinguished from the first copy.
- Noise, distortion, and mastering quality are not graded. A noisy file can still be perfectly lossless.

Treat results as spectral evidence, not as a definitive measurement of audio quality or file history.

## Run Tests

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```

Compile-check all modules:

```bash
.venv/bin/python3 -m compileall -q flac_checker.py audio detectors scoring reports tests
```
