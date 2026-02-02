# GitHub Upload Security Checklist

Before pushing your ML trading bot to GitHub, verify these items:

## ✅ Pre-Upload Checklist

### 1. Data Files Protection
- [ ] All `.csv` files are in `.gitignore`
- [ ] No trading data is in the repo
- [ ] No backtest results are included
- [ ] No performance logs exist in repo

### 2. Credentials & Secrets
- [ ] No API keys in any files
- [ ] No broker credentials
- [ ] No `.env` files
- [ ] No `config.ini` or `settings.ini` with secrets
- [ ] No hardcoded passwords or tokens

### 3. Code Safety
- [ ] All hardcoded values moved to config
- [ ] No file paths that reveal your system structure
- [ ] No personally identifiable information
- [ ] No broker-specific identifiers

### 4. Git Configuration
- [ ] `.gitignore` file is present
- [ ] `.gitignore` is committed first
- [ ] Check `git status` before each commit
- [ ] Verify no unintended files are staged

### 5. Documentation
- [ ] README doesn't contain trading results
- [ ] No specific profit/loss figures
- [ ] Disclaimer is prominent
- [ ] Contact info is appropriate for public

## 🔍 Files to Verify

Run these commands in your repo:

```bash
# Check what git will track
git status

# See what's ignored
git status --ignored

# Search for potential secrets (examples)
grep -r "api_key" .
grep -r "password" .
grep -r "secret" .
grep -r "token" .

# Check for CSV files
find . -name "*.csv" -type f

# Check for sensitive extensions
find . -name "*.env" -type f
find . -name "*.key" -type f
find . -name "*.pem" -type f
```

## 🚫 Never Commit

### File Types
- `*.csv` - Trading data
- `*.xlsx` / `*.xls` - Spreadsheets
- `*.db` / `*.sqlite` - Databases
- `*.pkl` / `*.pickle` - Serialized data
- `*.log` - Log files
- `*.env` - Environment variables

### Directories
- `data/` - Trading data
- `results/` - Backtest results
- `logs/` - Log files
- `models/` - Trained models (can be large)
- `__pycache__/` - Python cache

### Sensitive Content
- API keys or tokens
- Broker credentials
- Account numbers
- Real trading results
- Personal financial information

## ✅ Safe to Commit

- Python scripts (`.py`)
- Documentation (`.md`)
- Requirements (`requirements.txt`)
- Configuration templates (example configs with no secrets)
- `.gitignore`
- License file
- Example data (sanitized, small samples only)

## 🔧 If You Accidentally Commit Secrets

**DO NOT just delete the file and recommit!** The secret is still in git history.

### Option 1: Remove from History (Small Repos)
```bash
# Remove file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: rewrites history)
git push origin --force --all
```

### Option 2: BFG Repo-Cleaner (Recommended)
```bash
# Install BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove passwords
bfg --replace-text passwords.txt

# Remove files
bfg --delete-files secrets.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Option 3: Rotate All Secrets
**Most Important**: Immediately rotate any exposed:
- API keys → Generate new ones
- Passwords → Change them
- Tokens → Revoke and create new

## 📋 Final Verification

Before `git push`:

```bash
# 1. Review all changes
git diff --cached

# 2. Check commit contents
git show

# 3. Verify ignored files
git ls-files --others --ignored --exclude-standard

# 4. Test clean clone
cd /tmp
git clone /path/to/your/repo test-clone
cd test-clone
# Verify no sensitive files present
ls -la
```

## 🎯 GitHub Settings

After uploading:

1. **Make repo private** if it contains any strategy logic
2. Enable **branch protection** on main
3. Review **collaborator access**
4. Check **GitHub Actions** permissions if using CI/CD
5. Consider **security scanning** (Dependabot, CodeQL)

## 📞 If Something Goes Wrong

If you accidentally expose secrets:

1. **Immediately** rotate all compromised credentials
2. Delete the repository if necessary
3. Review recent account activity for unauthorized access
4. Consider this a serious security incident

## ✨ Best Practices

- Commit `.gitignore` **before** any other files
- Use `git add -p` to review each change
- Never use `git add .` or `git add *` blindly
- Keep sensitive work in a separate, private repo
- Use environment variables for all secrets
- Consider using git-secrets or similar tools

---

**When in doubt, DON'T push.** You can always push later, but you can't unpush.
