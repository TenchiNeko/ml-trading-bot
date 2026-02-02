# Quick Start: Safe GitHub Upload

## Step-by-Step Upload Process

### 1. Initialize Repository

```bash
# Navigate to your project directory
cd /path/to/ml-trading-bot

# Initialize git (if not already done)
git init

# Add .gitignore FIRST (critical!)
git add .gitignore
git commit -m "Add .gitignore to protect sensitive data"
```

### 2. Verify What Will Be Tracked

```bash
# See what git will include
git status

# See what's ignored (should include all .csv files)
git status --ignored

# If you see any .csv or sensitive files in "Untracked files", 
# STOP and add them to .gitignore
```

### 3. Add Safe Files

```bash
# Add only specific safe files
git add README.md
git add requirements.txt
git add ml_panic_cop.py
git add example_config.json
git add SECURITY_CHECKLIST.md

# Review what you're about to commit
git status

# See the actual changes
git diff --cached
```

### 4. Commit Changes

```bash
git commit -m "Initial commit: ML trading bot v2"
```

### 5. Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `ml-trading-bot` (or your choice)
3. **Visibility**: 
   - ✅ **Private** (recommended for trading strategies)
   - ⚠️ Public (only if you're sure no strategy info is exposed)
4. ❌ **Do NOT** initialize with README (you already have one)
5. Click "Create repository"

### 6. Connect and Push

```bash
# Add GitHub remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/ml-trading-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Common Issues & Fixes

### Issue: CSV Files Are Being Tracked

```bash
# Remove from git (keeps local file)
git rm --cached *.csv

# Commit the removal
git commit -m "Remove CSV files from tracking"
```

### Issue: Already Committed Sensitive Data

```bash
# DON'T PUSH YET!
# Remove the last commit (keeps changes)
git reset HEAD~1

# Fix .gitignore
nano .gitignore

# Add .gitignore first
git add .gitignore
git commit -m "Fix .gitignore"

# Now add safe files only
git add ml_panic_cop.py README.md requirements.txt
git commit -m "Initial commit"
```

### Issue: Need to Check What's in a Commit

```bash
# See what's in the last commit
git show

# See what's in staging area
git diff --cached

# See file tree of what would be pushed
git ls-tree -r main --name-only
```

## Safe Workflow

### Every Time You Add Files

```bash
# 1. Check status
git status

# 2. Add specific files only (NEVER use git add .)
git add specific_file.py

# 3. Review changes
git diff --cached

# 4. Commit
git commit -m "Description of changes"

# 5. Push
git push
```

### Before Each Push

```bash
# Verify no sensitive files
git ls-files | grep -E "\.(csv|db|log|key|env)$"

# Should return nothing. If it shows files, STOP!
```

## Quick Commands Reference

```bash
# Status & Info
git status                      # What's changed
git status --ignored            # Show ignored files
git log --oneline              # Commit history
git show                        # Last commit details

# Adding & Committing
git add file.py                # Add specific file
git add -p                     # Add interactively (review each change)
git commit -m "message"        # Commit with message
git commit --amend             # Modify last commit

# Undoing (before push)
git reset HEAD file.py         # Unstage file
git reset HEAD~1               # Undo last commit (keep changes)
git reset --hard HEAD~1        # Undo last commit (DELETE changes)
git checkout -- file.py        # Discard local changes

# Remote Operations
git remote -v                  # Show remotes
git push                       # Push to GitHub
git pull                       # Pull from GitHub
git clone URL                  # Clone repository

# Inspection
git diff                       # Show unstaged changes
git diff --cached              # Show staged changes
git ls-files                   # List tracked files
git ls-tree -r main            # Show file tree
```

## Safety Aliases (Optional)

Add to `~/.gitconfig`:

```ini
[alias]
    # Safe add - shows what you're adding
    sadd = add -p
    
    # Check before push
    ready = !git ls-files | grep -E "\\.(csv|db|log|key|env)$" && echo "WARNING: Sensitive files detected!" || echo "Safe to push"
    
    # Show what would be pushed
    show-push = log origin/main..HEAD --oneline
```

Usage:
```bash
git ready        # Check if safe to push
git show-push    # See what commits would be pushed
```

## Final Checklist Before First Push

- [ ] `.gitignore` exists and is committed
- [ ] No `.csv` files in `git status`
- [ ] No API keys or credentials in code
- [ ] README has strong disclaimer
- [ ] Repository is set to **Private** on GitHub
- [ ] Ran `git status --ignored` to verify protection
- [ ] Reviewed `git diff --cached` for all commits
- [ ] Double-checked with SECURITY_CHECKLIST.md

## Emergency: Pushed Secrets by Accident

```bash
# 1. DO NOT PANIC (but act quickly)

# 2. Delete repository on GitHub immediately
#    Go to Settings > Danger Zone > Delete Repository

# 3. Rotate ALL credentials that were exposed

# 4. Clean local repo
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret" \
  --prune-empty --tag-name-filter cat -- --all

# 5. Create new repository with fixed .gitignore

# 6. Consider the exposed credentials COMPROMISED
```

## Need Help?

- Check `SECURITY_CHECKLIST.md` for detailed verification
- Review `.gitignore` to ensure coverage
- Test with a clean clone in `/tmp` first
- When in doubt, ask before pushing

**Remember: You can always push later. You can't unpush.**
