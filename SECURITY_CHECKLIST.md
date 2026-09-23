# Public repository data-safety checklist

This repository is intentionally public. The program itself does not require credentials, broker access, or network access, but local inputs and generated outputs may contain private financial information.

## Before every push

- [ ] `git status` lists only intended source or documentation changes.
- [ ] No real trading CSV, spreadsheet, Parquet, database, or result export is staged.
- [ ] No `.env` file, credential, API key, account number, or broker identifier is staged.
- [ ] No trained model or serialized object built from private data is staged.
- [ ] Configuration changes contain research parameters only—not secrets or local paths.
- [ ] New test fixtures are synthetic or explicitly redistributable.
- [ ] The staged diff has been reviewed with `git diff --cached`.

## Useful checks

```bash
git status --short
git diff --cached
git ls-files
git ls-files --others --ignored --exclude-standard
```

Check for tracked data-like files:

```bash
git ls-files | grep -E '\.(csv|xlsx?|parquet|feather|pkl|pickle|h5|db|sqlite3?|log|env|key|pem)$'
```

No output is expected unless a small, synthetic fixture was intentionally reviewed and allowed.

## Files that should remain local

- real trade histories and account exports
- backtest and performance reports tied to private strategies
- generated result CSV files
- broker or exchange credentials
- `.env` files and private configuration
- serialized models trained on private inputs
- notebooks containing outputs copied from private data

The checked-in [`.gitignore`](.gitignore) blocks common forms of these artifacts, but ignore rules are a guardrail—not a substitute for reviewing the staged diff.

## If sensitive material is published

1. Revoke or rotate every exposed credential immediately.
2. Assume the exposed value is compromised even if the file is later deleted.
3. Remove the material from Git history with an appropriate history-rewrite tool.
4. Review account and repository activity.
5. Document the incident privately before resuming publication.

Do not paste a live secret or private dataset into a public GitHub issue while requesting help.
