# Contributing

Thanks for helping improve Panic Cop. Keep changes small, reproducible, and safe for a public research repository.

## Before opening a pull request

1. Create a focused branch from `main`.
2. Keep real trading data, results, credentials, and trained models outside the repository.
3. Install the supported dependencies in a virtual environment.
4. Run the local checks:

   ```bash
   python -m compileall -q ml_panic_cop.py tests
   python -m unittest discover -s tests -v
   python ml_panic_cop.py --help
   ```

5. Explain the behavior change, assumptions, and validation in the pull request.

## Research claims

Do not present in-sample results, Monte Carlo comparisons, or a single backtest as guaranteed performance. Include enough information to reproduce a claim, and distinguish illustrative output from measured results.

## Data and security

Use synthetic or explicitly redistributable fixtures only. Never commit broker credentials, account identifiers, proprietary datasets, private performance histories, serialized trained models, or generated result files. Review [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) before pushing.
