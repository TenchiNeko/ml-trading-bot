# ML Trading Bot - Panic Cop v2

A machine learning-based position sizing system that dynamically reduces exposure during drawdown conditions using a RandomForest classifier.

## ⚠️ Disclaimer

**This software is for educational and research purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results. Never risk more than you can afford to lose.**

## Overview

This system implements a "panic cop" mechanism that:

1. **Identifies Risk Conditions**: Detects when the trading system is in a vulnerable state (drawdown, loss streaks)
2. **ML-Based Decision Making**: Uses RandomForest to predict when to reduce position size
3. **Conservative Approach**: Only acts during clearly defined risk scenarios
4. **Statistical Validation**: Validates edge through Monte Carlo simulation

### Key Features

- **Gated Activation**: ML only activates during specific market regimes and risk thresholds
- **Conservative Teacher Labels**: Training labels based on deep drawdowns and extended loss streaks
- **Probability Threshold**: High confidence requirement (default 0.75) before size reduction
- **Monte Carlo Validation**: Statistical proof that the ML is providing edge vs random
- **Configurable Parameters**: All thresholds and settings externalized

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

**Python Version**: 3.8+

### Required Libraries

- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0

## Usage

### Basic Usage

```bash
python ml_panic_cop.py your_trading_data.csv
```

### With Custom Output File

```bash
python ml_panic_cop.py your_trading_data.csv --output results.csv
```

### With Custom Configuration

```bash
python ml_panic_cop.py your_trading_data.csv --config config.json
```

### As a Module

```python
from ml_panic_cop import PanicCopML

# Initialize with custom config
config = {
    "panic_mult": 0.50,
    "prob_threshold": 0.75,
    "dd_gate": -0.15,
}

bot = PanicCopML(config)
results = bot.run_full_pipeline("data.csv", "output.csv")
```

## Data Requirements

Your input CSV must contain these columns:

| Column | Description |
|--------|-------------|
| `date` | Trade date (parseable datetime) |
| `ret_pct` | Return percentage per trade |
| `size_final` | Position size (e.g., 4x leverage) |
| `q_confidence` | Signal confidence metric |
| `volume_ratio_x` | Volume-based feature |
| `regime_x` | Market regime classification |

**Important**: The system only activates during `regime_x == "bull_trending"`

## Configuration

### Default Parameters

```json
{
  "panic_mult": 0.50,         // Reduce size to 50% when panic triggers
  "prob_threshold": 0.75,     // Require 75% ML confidence
  "dd_gate": -0.15,           // -15% drawdown enables panic eligibility
  "loss_gate": 6,             // 6 consecutive losses enables panic eligibility
  "teacher_dd": -0.20,        // -20% DD for training labels
  "teacher_loss": 3,          // 3 losses for training labels
  "teacher_bigloss": -0.05,   // Single -5% loss for training labels
  "train_split": 0.70,        // 70% train, 30% test
  "n_runs_mc": 2000,          // Monte Carlo simulations
  "rf_n_estimators": 300,     // Random Forest trees
  "rf_max_depth": 4,          // Tree depth (prevents overfitting)
  "random_state": 42          // Reproducibility seed
}
```

### Creating a Config File

Create `config.json`:

```json
{
  "panic_mult": 0.60,
  "prob_threshold": 0.80,
  "dd_gate": -0.12
}
```

## How It Works

### 1. Feature Engineering

The system creates these features from your trading data:

- **dd_4x**: Current drawdown from equity peak
- **loss_streak**: Consecutive losing trades count
- **roll_loss3**: 3-trade moving average of sized returns
- **roll_std5**: 5-trade rolling standard deviation
- **q_confidence**: Your signal confidence metric
- **volume_ratio_x**: Your volume feature

### 2. Panic Eligibility Gate

ML can only activate when:
```python
(drawdown <= -15% OR loss_streak >= 6) AND regime == "bull_trending"
```

### 3. Teacher Labels (Conservative)

Training examples labeled as "panic=1" when:
```python
eligible AND drawdown <= -20% AND (loss_streak >= 3 OR single_loss <= -5%)
```

### 4. ML Prediction

- RandomForest trained on eligible trades only
- High probability threshold (75%) required
- Position size reduced to 50% when panic triggers

### 5. Monte Carlo Validation

Shuffles panic decisions randomly among eligible trades 2000 times to prove the ML selections beat random chance.

**Statistical Significance**:
- p-value < 0.05: Strong evidence of edge
- |z-score| > 1.96: Statistically significant at 95% confidence

## Output

The system generates a CSV with these additional columns:

- `eq_4x`: Equity curve without panic
- `dd_4x`: Drawdown without panic
- `loss_streak`: Consecutive losses
- `roll_loss3`, `roll_std5`: Rolling features
- `panic_eligible`: Boolean for eligibility
- `teacher_panic`: Training labels
- `panic_prob`: ML probability of panic
- `panic_flag_ml`: Final panic decision
- `size_ml_panic`: Adjusted position size

## Performance Metrics

The system outputs:

```
=== Performance Comparison ===
4x gas equity: 2.45, max DD: -32.5%
ML panic equity: 2.78, max DD: -28.3%

=== Monte Carlo Validation ===
Real ML equity: 2.78
Random mean: 2.52
p-value: 0.0123
z-score: 2.34
```

## Interpretation Guide

### Good Results
- ML equity > 4x equity
- ML max DD < 4x max DD
- p-value < 0.05
- |z-score| > 1.96

### Warning Signs
- p-value > 0.20 (likely no edge)
- Very few panic triggers (< 1% of trades)
- No improvement in drawdown

### Tuning Advice

**If panic triggers too often**:
- Increase `prob_threshold` (0.75 → 0.85)
- Tighten `dd_gate` (-0.15 → -0.18)
- Increase `loss_gate` (6 → 8)

**If panic never triggers**:
- Decrease `prob_threshold` (0.75 → 0.65)
- Loosen teacher thresholds
- Check that you have "bull_trending" regime periods

**If overfitting**:
- Reduce `rf_max_depth` (4 → 3)
- Increase `rf_n_estimators` (300 → 500)

## Safety Considerations

### What This Code Does NOT Do

❌ Connect to any broker or exchange  
❌ Execute live trades  
❌ Store credentials or API keys  
❌ Access the internet  
❌ Modify your original data files  

### What You Should Never Commit

- Actual trading data (CSV files)
- Broker credentials or API keys
- Trading results or performance data
- Trained models with real data

**The `.gitignore` is configured to protect you**, but always double-check before pushing.

## File Structure

```
ml-trading-bot/
├── .gitignore              # Protects sensitive data
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── ml_panic_cop.py         # Main ML system
├── config.json             # Configuration (optional)
└── example_config.json     # Example configuration
```

## Development

### Running Tests

```bash
# Test with example data
python ml_panic_cop.py example_data.csv --config example_config.json
```

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Never commit real trading data
4. Submit a pull request

## License

[Your chosen license - MIT, GPL, etc.]

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Acknowledgments

Built with:
- scikit-learn for ML
- pandas for data manipulation
- numpy for numerical operations

---

**Remember**: This is a research tool. Always paper trade extensively before considering live use. Never risk capital you can't afford to lose.
