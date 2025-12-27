# 🔄 Default Branch Change Guide

> **Quick Links**: [Summary](DEFAULT_BRANCH_SUMMARY.md) | [Quick Reference](BRANCH_QUICK_REFERENCE.md) | [Migration Script](migrate-default-branch.sh)

## Current Status
- **Current Default Branch**: `Main` (capitalized)
- **Recommended Default Branch**: `main` (lowercase)

## Why Change the Default Branch?

The industry standard has shifted from `master` to `main` (lowercase) as the default branch name. Currently, this repository uses `Main` (capitalized), which is non-standard. Standardizing to `main` will:

- ✅ Follow GitHub's recommended convention
- ✅ Improve consistency with other repositories
- ✅ Align with industry best practices
- ✅ Make it easier for contributors familiar with standard naming

## Prerequisites

To change the default branch, you need:
- Admin access to the repository
- GitHub account with appropriate permissions

## Step-by-Step Guide

### 1. Create the New Branch (If Not Exists)

First, ensure you're on the current default branch and create the new `main` branch:

```bash
# Checkout the current default branch
git checkout Main

# Pull latest changes
git pull origin Main

# Create new main branch from Main
git branch main
git push origin main
```

### 2. Update Default Branch in GitHub

1. Go to repository settings: `https://github.com/Barrot-Agent/Barrot-Agent/settings`
2. Click on "Branches" in the left sidebar
3. In the "Default branch" section, click the switch icon
4. Select `main` from the dropdown
5. Click "Update" and confirm the change

### 3. Update Local Repository

For all contributors to update their local repositories:

```bash
# Fetch the latest changes
git fetch origin

# Switch to the new main branch
git checkout main

# Set upstream to track the new main branch
git branch -u origin/main

# Optional: Delete old local Main branch
git branch -D Main
```

### 4. Update CI/CD and Workflows

After changing the default branch, update any references in:

- GitHub Actions workflows (if they explicitly reference `Main`)
- Documentation files
- CI/CD configuration files
- Branch protection rules

### 5. Delete Old Branch (Optional)

After verifying everything works with the new `main` branch:

```bash
# Delete the old Main branch (requires admin access)
git push origin --delete Main
```

**⚠️ Warning**: Only delete the old branch after:
- Confirming all workflows run successfully on `main`
- Updating all branch protection rules
- Notifying all contributors
- Ensuring all open PRs are retargeted to `main`

## Automated Migration Script

You can use the following script to help with the migration:

```bash
#!/bin/bash

echo "🔄 Starting default branch migration..."

# Fetch latest changes
git fetch origin

# Create main branch from Main
git checkout Main
git pull origin Main
git checkout -b main
git push origin main

echo "✅ New 'main' branch created and pushed"
echo ""
echo "📝 Next steps:"
echo "1. Go to GitHub repository settings"
echo "2. Change default branch to 'main'"
echo "3. Update branch protection rules"
echo "4. Notify contributors"
echo "5. Run: git fetch origin && git checkout main"
```

Save this as `migrate-default-branch.sh` and run with `bash migrate-default-branch.sh`

## For Contributors

If the default branch has been changed to `main`, update your local repository:

```bash
# Fetch the latest from origin
git fetch origin

# Switch to main branch
git checkout main

# Update tracking
git branch -u origin/main

# Pull latest changes
git pull

# Optional: Remove old local Main branch
git branch -D Main
```

## 📱 Using from Mobile (Termux/iSH)

Yes! You can run the migration from mobile terminals like Termux (Android) or iSH (iOS).

### Termux (Android)

The migration script works perfectly in Termux. Make sure you have git installed:

```bash
# Update packages (if needed)
pkg update && pkg upgrade

# Install git (if not already installed)
pkg install git

# Navigate to your repository
cd ~/projects/Barrot-Agent

# Run the migration script
bash migrate-default-branch.sh
```

**Note**: After running the script, you'll still need to change the default branch in GitHub settings. You can:
- Use GitHub Mobile app: Repository → Settings → Branches → Change default
- Use a browser on your phone: Navigate to repository settings
- Use GitHub CLI if installed in Termux: `gh repo edit --default-branch main`

### iSH (iOS)

Similar steps apply for iSH:

```bash
# Ensure git is installed
apk add git

# Navigate to repository
cd ~/Barrot-Agent

# Run migration
bash migrate-default-branch.sh
```

For more mobile setup details, see [MOBILE_SETUP.md](MOBILE_SETUP.md).

## Checking Current Default Branch

To verify which branch is the default:

```bash
# Check remote default branch
git remote show origin | grep "HEAD branch"

# Check local HEAD
cat .git/HEAD
```

## Common Issues

### Issue: "Branch 'main' already exists"
**Solution**: If `main` already exists, just switch to it:
```bash
git checkout main
git pull origin main
```

### Issue: "Cannot delete branch 'Main' - it's the default"
**Solution**: Change the default branch in GitHub settings first, then delete.

### Issue: Workflows failing after branch change
**Solution**: Update all workflow files that explicitly reference `Main`:
```yaml
# Change from:
on:
  push:
    branches: [ Main ]

# To:
on:
  push:
    branches: [ main ]
```

## Resources

- [GitHub: Renaming a branch](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/renaming-a-branch)
- [GitHub: Changing the default branch](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/changing-the-default-branch)

---

**Need Help?** Open an issue in the repository if you encounter any problems during the migration.
