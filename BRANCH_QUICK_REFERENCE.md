# Quick Reference: Default Branch Change

## 🎯 For Contributors

If you have an existing clone of this repository and the default branch has been changed to `main`:

### Update Your Local Repository

```bash
# 1. Fetch latest changes
git fetch origin

# 2. Switch to the new main branch
git checkout main

# 3. Set upstream tracking
git branch -u origin/main

# 4. Pull latest changes
git pull

# 5. Optional: Remove old local branch
git branch -D Main
```

**📱 Mobile Users (Termux/iSH)**: These commands work the same on Termux (Android) and iSH (iOS)!

### For New Clones

New clones will automatically use the `main` branch:

```bash
git clone https://github.com/Barrot-Agent/B-Agent.git
cd Barrot-Agent
# You're now on the main branch
```

## 🔍 Check Your Current Branch

```bash
# See which branch you're on
git branch --show-current

# See the default branch on remote
git remote show origin | grep "HEAD branch"
```

## ⚙️ Common Git Commands (Updated)

```bash
# Pull latest changes from main
git pull origin main

# Create a new branch from main
git checkout main
git pull
git checkout -b my-feature-branch

# Push changes to main (if you have permissions)
git push origin main
```

## 📋 Branch Status

- **Old Default**: `Main` (capitalized)
- **New Default**: `main` (lowercase)
- **Status**: In transition - follow the guide in [DEFAULT_BRANCH_GUIDE.md](DEFAULT_BRANCH_GUIDE.md)

## 🆘 Need Help?

- **Full Migration Guide**: [DEFAULT_BRANCH_GUIDE.md](DEFAULT_BRANCH_GUIDE.md)
- **Issues**: [Open an issue](https://github.com/Barrot-Agent/B-Agent/issues)
- **Workflow Problems**: Check [GitHub Actions](https://github.com/Barrot-Agent/B-Agent/actions)

---

**Last Updated**: 2025-12-26
