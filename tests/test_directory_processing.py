import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audio.features import AnalysisResult, AudioInfo
from flac_checker import process_directory


class DirectoryProcessingTests(unittest.TestCase):
    def test_writes_per_file_reports_and_summary(self):
        def fake_analyze(file_path, config):
            return AnalysisResult(
                file=file_path,
                audio=AudioInfo(44100, 1, 1.0, 44100, "PCM_16"),
                verdict="CLEAN",
                score=10.0,
                confidence="MODERATE",
                cutoff_hz=None,
                nyquist_hz=22050.0,
                signals=[],
                warnings=[],
            )

        with tempfile.TemporaryDirectory() as directory:
            input_directory = Path(directory) / "input"
            log_directory = Path(directory) / "logs"
            input_directory.mkdir()
            (input_directory / "song.flac").touch()
            (input_directory / "other.flac").touch()

            with patch("flac_checker.analyze_file", side_effect=fake_analyze):
                process_directory(input_directory, log_directory, None)

            individual_results_directory = log_directory / "individual_results"
            self.assertTrue((individual_results_directory / "song.json").exists())
            self.assertEqual(
                json.loads(
                    (individual_results_directory / "song.json").read_text()
                )["verdict"],
                "CLEAN",
            )
            self.assertEqual(
                (log_directory / "verdicts.log").read_text(),
                "other.flac -> CLEAN\nsong.flac -> CLEAN\n",
            )


if __name__ == "__main__":
    unittest.main()