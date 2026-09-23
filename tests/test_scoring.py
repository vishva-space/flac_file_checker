import unittest

from audio.features import Config, SignalResult
from scoring.weighted_score import calculate_confidence, calculate_score, classify_verdict


class ScoringTests(unittest.TestCase):
    def test_weighted_score_sums_contributions(self):
        signals = [SignalResult("one", 80, 25, 20, ""), SignalResult("two", 60, 15, 9, "")]
        self.assertEqual(calculate_score(signals), 29.0)

    def test_high_score_is_transcoded(self):
        self.assertEqual(classify_verdict(70, [], False, Config()), "TRANSCODED")
        self.assertEqual(calculate_confidence(80, []), "MODERATE")

    def test_low_unstable_cutoff_is_unknown(self):
        signals = [SignalResult("cutoff_consistency", 0, 15, 0, "")]
        self.assertEqual(
            classify_verdict(90, [], False, Config(), signals, 11000, 22050),
            "UNKNOWN",
        )

    def test_higher_unstable_cutoff_is_clean(self):
        signals = [SignalResult("cutoff_consistency", 0, 15, 0, "")]
        self.assertEqual(
            classify_verdict(90, [], False, Config(), signals, 12500, 22050),
            "CLEAN",
        )


if __name__ == "__main__":
    unittest.main()