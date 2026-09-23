# FLAC Checker

Analyzes FLAC files for spectral evidence that may indicate transcoding or upsampling. The result is heuristic, not proof of provenance.

## Run

```bash
.venv/bin/python3 flac_checker.py /path/to/flac-directory --log-dir logs
```

The checker recursively processes `.flac` files. It writes one JSON report per file and a summary at `logs/verdicts.log`:

```text
track.flac -> CLEAN
other.flac -> TRANSCODED
unknown.flac -> UNKNOWN
```

## Verdicts

- `CLEAN`: no reliable codec-wall evidence was found.
- `TRANSCODED`: a stable spectral cutoff and supporting evidence were found.
- `UPSAMPLED`: the sample rate is high but the measured content ceiling is much lower.
- `UNKNOWN`: the evidence is ambiguous or the file could not be analyzed reliably.

## What This Tool Cannot See

- A 320 kbps MP3 or a 256+ kbps AAC encoded without a low-pass can keep the full band and leave no spectral trace.
- A lossless file with a steep low-pass, such as an EQ'd stem or bass track, can look like a codec wall. The tool abstains rather than guesses.
- Very quiet material, with peaks under about -45 dBFS, narrows the analysis window; the cutoff reading can walk down the slope.
- Generation loss without a wall, such as a re-encode of a re-encode, cannot be distinguished from the first copy.
- Noise, distortion, and mastering quality are not graded. A noisy file can still be perfectly lossless.

Treat results as spectral evidence, not as a definitive measurement of audio quality or file history.

## Tests

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```
