import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from ml_panic_cop import PanicCopML


class PanicCopMLTests(unittest.TestCase):
    @staticmethod
    def documented_frame() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": pd.date_range("2026-01-01", periods=6),
                "ret_pct": [10.0, -5.0, 2.0, -1.0, 3.0, -2.0],
                "size_final": [1.0] * 6,
                "q_confidence": [0.8] * 6,
                "volume_ratio_x": [1.2] * 6,
                "regime_x": ["bull_trending"] * 6,
            }
        )

    def test_documented_input_schema_loads_without_derived_columns(self) -> None:
        frame = self.documented_frame()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trades.csv"
            frame.to_csv(path, index=False)
            loaded = PanicCopML().load_data(path)

        self.assertEqual(len(loaded), len(frame))
        self.assertNotIn("roll_std5", frame.columns)

    def test_missing_input_columns_raise_clear_error(self) -> None:
        frame = self.documented_frame().drop(columns=["regime_x"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trades.csv"
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "regime_x"):
                PanicCopML().load_data(path)

    def test_feature_engineering_includes_the_first_trade(self) -> None:
        bot = PanicCopML()
        bot.df = self.documented_frame()
        result = bot.engineer_features()

        self.assertAlmostEqual(result.loc[0, "eq_4x"], 1.10)
        self.assertIn("dd_4x", result.columns)
        self.assertIn("loss_streak", result.columns)
        self.assertIn("roll_loss3", result.columns)
        self.assertIn("roll_std5", result.columns)

    def test_equity_path_and_drawdown(self) -> None:
        equity = PanicCopML.equity_path(np.array([0.10, -0.05]), np.ones(2))
        np.testing.assert_allclose(equity, np.array([1.10, 1.045]))
        self.assertAlmostEqual(PanicCopML.max_drawdown(equity), -0.05)


if __name__ == "__main__":
    unittest.main()
