# Quick start

Panic Cop analyzes a local CSV and writes a local result file. It does not connect to a broker or download market data.

## 1. Create an environment

```bash
git clone https://github.com/TenchiNeko/ml-trading-bot.git
cd ml-trading-bot

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 2. Prepare data

Use a local CSV with the documented columns:

```text
date,ret_pct,size_final,q_confidence,volume_ratio_x,regime_x
```

`ret_pct` is expressed in percentage points, so `-1.5` means −1.5%. Real trading CSV files are ignored by Git and should remain outside version control.

## 3. Review configuration

```bash
cp example_config.json config.json
```

Start with the defaults. Change one assumption at a time and keep a record of every experiment.

## 4. Run the pipeline

```bash
python ml_panic_cop.py trades.csv \
  --config config.json \
  --output results.csv
```

The terminal prints classification, equity-path, drawdown, and Monte Carlo diagnostics. The output CSV contains the original usable rows plus engineered features and sizing decisions.

## 5. Interpret cautiously

- A better in-sample equity path is not evidence of future profitability.
- The Monte Carlo comparison is a placement diagnostic, not proof of causal edge.
- Validate with true holdout periods, walk-forward evaluation, costs, and paper trading.
- Do not use this script as a live risk control or order-execution system.

## Developer checks

```bash
python -m compileall -q ml_panic_cop.py tests
python -m unittest discover -s tests -v
python ml_panic_cop.py --help
```

See [README.md](README.md) for the full method and [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) before publishing any changes.
