# 🔄 Default Branch Change Guide

> **Quick Links**: [Summary](DEFAULT_BRANCH_SUMMARY.md) | [Quick Reference](BRANCH_QUICK_REFERENCE.md)

## Current Status
- **✅ Migration Complete**: Default branch changed from `Main` to `main`
- **Current Default Branch**: `main` (lowercase)

## Why We Changed the Default Branch

The industry standard shifted from `master` to `main` (lowercase) as the default branch name. This repository previously used `Main` (capitalized), which was non-standard. The migration to `main` provides:

- ✅ Follow GitHub's recommended convention
- ✅ Improve consistency with other repositories
- ✅ Align with industry best practices
- ✅ Make it easier for contributors familiar with standard naming

## For New Contributors

## For New Contributors

The default branch is now `main`. When cloning the repository:

```bash
# Clone repository
git clone https://github.com/Barrot-Agent/B-Agent.git
cd B-Agent

# You're automatically on main branch
git branch
```

## For Existing Contributors

If you had the repository cloned before the migration:

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

## Historical Migration Information

### How The Migration Was Completed

The migration from `Main` to `main` was completed in December 2025. The steps taken were:

1. Created new `main` branch from `Main` branch
2. Updated default branch in GitHub settings to `main`
3. Updated all workflows and CI/CD configurations
4. Updated branch protection rules
5. Notified contributors
6. Deleted old `Main` branch after verification

All workflows now reference `main` and the old `Main` branch no longer exists.

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
