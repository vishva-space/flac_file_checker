import unittest

import numpy as np

from audio.features import Config
from detectors.cutoff import detect_cutoff


class CutoffTests(unittest.TestCase):
    def test_detect_cutoff_uses_lower_quartile(self):
        frequencies = np.array([10000.0, 12000.0, 14000.0, 16000.0])
        magnitude = np.full((4, 3), -80.0)
        magnitude[:2, 0] = -10.0
        magnitude[:3, 1] = -10.0
        magnitude[:, 2] = -10.0

        cutoff, cutoffs = detect_cutoff(frequencies, magnitude, Config())

        self.assertEqual(len(cutoffs), 3)
        self.assertEqual(cutoff, 13000.0)


if __name__ == "__main__":
    unittest.main()