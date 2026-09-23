import tempfile
import unittest
from pathlib import Path

from audio.loader import load_audio


class LoaderTests(unittest.TestCase):
    def test_rejects_non_flac_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            path.write_bytes(b"not audio")
            with self.assertRaises(Exception):
                load_audio(str(path))


if __name__ == "__main__":
    unittest.main()