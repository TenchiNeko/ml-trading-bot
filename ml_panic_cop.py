"""
ML Trading Bot - Panic Cop v2
A machine learning-based position sizing system that reduces exposure during drawdown conditions.

This system:
1. Identifies panic-eligible trades based on drawdown and loss streaks
2. Uses RandomForest classifier to predict when to reduce position size
3. Validates performance through Monte Carlo simulation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import argparse
import json
from pathlib import Path

# =====================================
# DEFAULT CONFIG (can be overridden)
# =====================================
DEFAULT_CONFIG = {
    "panic_mult": 0.50,          # Position size multiplier when panic is ON
    "prob_threshold": 0.75,      # ML probability threshold for panic
    "dd_gate": -0.15,            # Drawdown level to become panic-eligible
    "loss_gate": 6,              # Loss streak to become panic-eligible
    "teacher_dd": -0.20,         # Deep drawdown for teacher labels
    "teacher_loss": 3,           # Loss streak for teacher labels
    "teacher_bigloss": -0.05,    # Single large loss for teacher labels
    "train_split": 0.70,         # Train/test split ratio
    "n_runs_mc": 2000,           # Monte Carlo simulation runs
    "rf_n_estimators": 300,      # Random Forest trees
    "rf_max_depth": 4,           # Random Forest max depth
    "random_state": 42           # Random seed for reproducibility
}


class PanicCopML:
    """Machine learning-based panic detection and position sizing."""
    
    def __init__(self, config=None):
        """Initialize with configuration."""
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.clf = None
        self.df = None
        self.feature_cols = [
            "dd_4x",
            "loss_streak",
            "roll_loss3",
            "roll_std5",
            "q_confidence",
            "volume_ratio_x",
        ]
    
    def load_data(self, filepath):
        """Load and prepare trading data."""
        print(f"Loading data from: {filepath}")
        df = pd.read_csv(filepath, parse_dates=["date"])
        df = df.sort_values("date").reset_index(drop=True)
        
        # Verify required columns exist
        required_cols = ["ret_pct", "size_final"] + self.feature_cols[3:]
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        df = df.dropna(subset=required_cols).reset_index(drop=True)
        self.df = df
        return df
    
    def engineer_features(self):
        """Create features for ML model."""
        df = self.df
        
        # Sized returns
        rets = df["ret_pct"].values / 100.0
        sizes_4x = df["size_final"].values
        ret_sized = rets * sizes_4x
        
        # Equity curve
        eq = np.ones(len(df))
        for i in range(1, len(df)):
            eq[i] = eq[i-1] * (1.0 + ret_sized[i])
        df["eq_4x"] = eq
        
        # Drawdown from running max
        run_max = np.maximum.accumulate(eq)
        dd = eq / run_max - 1.0
        df["dd_4x"] = dd
        
        # Loss streak
        loss_flag = ret_sized < 0
        loss_streak = np.zeros(len(df), dtype=int)
        streak = 0
        for i, is_loss in enumerate(loss_flag):
            if is_loss:
                streak += 1
            else:
                streak = 0
            loss_streak[i] = streak
        df["loss_streak"] = loss_streak
        
        # Rolling features
        ret_sized_ser = pd.Series(ret_sized)
        df["roll_loss3"] = ret_sized_ser.rolling(3, min_periods=1).mean()
        df["roll_std5"] = ret_sized_ser.rolling(5, min_periods=1).std().fillna(0.0)
        
        print(f"Features engineered for {len(df)} trades")
        return df
    
    def create_labels(self):
        """Create training labels based on conservative teacher rules."""
        df = self.df
        cfg = self.config
        
        # Identify panic-eligible trades
        panic_eligible = (
            ((df["dd_4x"] <= cfg["dd_gate"]) | 
             (df["loss_streak"] >= cfg["loss_gate"])) &
            (df["regime_x"] == "bull_trending")
        )
        df["panic_eligible"] = panic_eligible
        
        # Conservative teacher labels
        rets = df["ret_pct"].values / 100.0
        sizes_4x = df["size_final"].values
        ret_sized = rets * sizes_4x
        
        teacher_panic = (
            (panic_eligible) &
            (df["dd_4x"] <= cfg["teacher_dd"]) &
            ((df["loss_streak"] >= cfg["teacher_loss"]) |
             (ret_sized <= cfg["teacher_bigloss"]))
        )
        df["teacher_panic"] = teacher_panic.astype(int)
        
        print(f"Total trades: {len(df)}")
        print(f"Panic-eligible: {int(panic_eligible.sum())}")
        print(f"Teacher panic=1: {int(df['teacher_panic'].sum())}")
        
        if df["teacher_panic"].sum() == 0:
            raise ValueError("No panic=1 examples. Loosen teacher thresholds.")
        
        return df
    
    def train_model(self):
        """Train RandomForest classifier on panic-eligible trades."""
        df = self.df
        cfg = self.config
        
        # Prepare data
        X_all = df[self.feature_cols].copy()
        y_all = df["teacher_panic"].copy()
        
        # Split on eligible trades only
        eligible_idx = np.where(df["panic_eligible"].values)[0]
        n_eligible = len(eligible_idx)
        split_e = int(n_eligible * cfg["train_split"])
        
        train_idx = eligible_idx[:split_e]
        test_idx = eligible_idx[split_e:]
        
        X_train = X_all.iloc[train_idx]
        y_train = y_all.iloc[train_idx]
        X_test = X_all.iloc[test_idx]
        y_test = y_all.iloc[test_idx]
        
        # Train classifier
        self.clf = RandomForestClassifier(
            n_estimators=cfg["rf_n_estimators"],
            max_depth=cfg["rf_max_depth"],
            random_state=cfg["random_state"],
            class_weight="balanced",
        )
        self.clf.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.clf.predict(X_test)
        print("\n=== Classification Report (Test Set) ===")
        print(classification_report(y_test, y_pred, digits=3))
        
        return self.clf
    
    def apply_panic_sizing(self):
        """Apply ML panic detection to determine position sizes."""
        df = self.df
        cfg = self.config
        
        # Get panic probabilities
        eligible_idx = np.where(df["panic_eligible"].values)[0]
        panic_prob = np.zeros(len(df))
        
        X_all = df[self.feature_cols]
        panic_prob[eligible_idx] = self.clf.predict_proba(X_all.iloc[eligible_idx])[:, 1]
        
        # Apply threshold and gate
        panic_flag_ml = (panic_prob >= cfg["prob_threshold"]) & df["panic_eligible"].values
        df["panic_prob"] = panic_prob
        df["panic_flag_ml"] = panic_flag_ml.astype(int)
        
        # Adjust sizes
        sizes_ml = df["size_final"].values.copy()
        sizes_ml[panic_flag_ml] *= cfg["panic_mult"]
        df["size_ml_panic"] = sizes_ml
        
        print(f"\nML panic trades: {int(panic_flag_ml.sum())}")
        print(f"As % of all trades: {100.0 * panic_flag_ml.mean():.2f}%")
        
        return df
    
    @staticmethod
    def equity_path(returns, sizes):
        """Calculate equity curve from returns and sizes."""
        eq = np.ones(len(returns))
        for i in range(1, len(returns)):
            eq[i] = eq[i-1] * (1.0 + returns[i] * sizes[i])
        return eq
    
    @staticmethod
    def max_drawdown(equity):
        """Calculate maximum drawdown."""
        rm = np.maximum.accumulate(equity)
        dd = equity / rm - 1.0
        return dd.min()
    
    def evaluate_performance(self):
        """Compare 4x gas vs ML panic performance."""
        df = self.df
        
        rets = df["ret_pct"].values / 100.0
        sizes_4x = df["size_final"].values
        sizes_ml = df["size_ml_panic"].values
        
        eq_4x = self.equity_path(rets, sizes_4x)
        eq_ml = self.equity_path(rets, sizes_ml)
        
        dd_4x = self.max_drawdown(eq_4x)
        dd_ml = self.max_drawdown(eq_ml)
        
        print("\n=== Performance Comparison ===")
        print(f"4x gas equity: {eq_4x[-1]:.2f}, max DD: {dd_4x:.2%}")
        print(f"ML panic equity: {eq_ml[-1]:.2f}, max DD: {dd_ml:.2%}")
        
        return {
            "eq_4x": eq_4x[-1],
            "dd_4x": dd_4x,
            "eq_ml": eq_ml[-1],
            "dd_ml": dd_ml
        }
    
    def monte_carlo_validation(self):
        """Validate ML edge through Monte Carlo simulation."""
        df = self.df
        cfg = self.config
        
        rets = df["ret_pct"].values / 100.0
        sizes_4x = df["size_final"].values
        
        eligible_idx = np.where(df["panic_eligible"].values)[0]
        n_panic_real = int(df["panic_flag_ml"].sum())
        
        mc_equities = np.empty(cfg["n_runs_mc"])
        
        for i in range(cfg["n_runs_mc"]):
            sizes_rand = sizes_4x.copy()
            if n_panic_real > 0 and len(eligible_idx) >= n_panic_real:
                chosen = np.random.choice(eligible_idx, size=n_panic_real, replace=False)
                sizes_rand[chosen] *= cfg["panic_mult"]
            eq_rand = self.equity_path(rets, sizes_rand)
            mc_equities[i] = eq_rand[-1]
        
        real_eq = self.equity_path(rets, df["size_ml_panic"].values)[-1]
        mean_eq = mc_equities.mean()
        p_value = (mc_equities >= real_eq).mean()
        z_score = ((real_eq - mean_eq) / mc_equities.std(ddof=1) 
                   if mc_equities.std(ddof=1) > 0 else np.nan)
        
        print("\n=== Monte Carlo Validation ===")
        print(f"Real ML equity: {real_eq:.2f}")
        print(f"Random mean: {mean_eq:.2f}")
        print(f"5th-95th percentile: {np.percentile(mc_equities, 5):.2f} - "
              f"{np.percentile(mc_equities, 95):.2f}")
        print(f"p-value: {p_value:.4f}")
        print(f"z-score: {z_score:.2f}")
        print("Note: p < 0.05 or |z| > 1.96 suggests statistical edge")
        
        return {
            "real_eq": real_eq,
            "mean_eq": mean_eq,
            "p_value": p_value,
            "z_score": z_score
        }
    
    def run_full_pipeline(self, input_file, output_file=None):
        """Execute complete ML panic pipeline."""
        # Load and prepare
        self.load_data(input_file)
        self.engineer_features()
        self.create_labels()
        
        # Train and apply
        self.train_model()
        self.apply_panic_sizing()
        
        # Evaluate
        perf = self.evaluate_performance()
        mc_results = self.monte_carlo_validation()
        
        # Save results
        if output_file:
            self.df.to_csv(output_file, index=False)
            print(f"\n✓ Results saved to: {output_file}")
        
        return {
            "performance": perf,
            "monte_carlo": mc_results
        }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ML Trading Bot - Panic Cop v2")
    parser.add_argument("input_file", help="Input CSV file with trading data")
    parser.add_argument("--output", "-o", help="Output CSV file for results")
    parser.add_argument("--config", "-c", help="JSON config file")
    
    args = parser.parse_args()
    
    # Load config if provided
    config = DEFAULT_CONFIG.copy()
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))
    
    # Run pipeline
    bot = PanicCopML(config)
    output_file = args.output or "ml_panic_results.csv"
    results = bot.run_full_pipeline(args.input_file, output_file)
    
    print("\n✓ Pipeline complete!")
    return results


if __name__ == "__main__":
    main()
