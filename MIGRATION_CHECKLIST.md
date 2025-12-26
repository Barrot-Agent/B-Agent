# Default Branch Migration Checklist

Use this checklist when executing the default branch migration.

## Pre-Migration

- [ ] Review [DEFAULT_BRANCH_GUIDE.md](DEFAULT_BRANCH_GUIDE.md) thoroughly
- [ ] Ensure you have admin access to the repository
- [ ] Notify team members about upcoming migration
- [ ] Check if there are any open pull requests targeting `Main`
- [ ] Backup any critical data (optional, but recommended)

## Migration Steps

- [ ] **Step 1**: Run the migration script
  ```bash
  bash migrate-default-branch.sh
  ```

- [ ] **Step 2**: Verify `main` branch was created
  ```bash
  git fetch origin
  git branch -r | grep main
  ```

- [ ] **Step 3**: Change default branch in GitHub
  - Go to: Repository Settings → Branches
  - Click the switch icon next to "Main"
  - Select "main" from dropdown
  - Click "Update" and confirm

- [ ] **Step 4**: Update branch protection rules
  - Copy protection rules from `Main` to `main`
  - Configure any required checks for `main`
  - Verify protection rules are active

- [ ] **Step 5**: Update open pull requests
  - Retarget all PRs from `Main` to `main`
  - Verify PRs still pass CI/CD checks

- [ ] **Step 6**: Notify contributors
  - Share [BRANCH_QUICK_REFERENCE.md](BRANCH_QUICK_REFERENCE.md)
  - Post announcement in team channels
  - Update any project documentation

## Post-Migration Verification

- [ ] Verify default branch is now `main`
  ```bash
  git remote show origin | grep "HEAD branch"
  ```

- [ ] Test that workflows run on `main` branch
  - Trigger a workflow manually
  - Verify it completes successfully

- [ ] Ensure all team members have updated their local repos
  - Ask team to run: `git fetch origin && git checkout main`

- [ ] Monitor for any issues for 1-2 weeks

## Cleanup (After Successful Migration)

- [ ] Wait at least 1-2 weeks after migration
- [ ] Verify no one is using `Main` branch anymore
- [ ] Delete old `Main` branch (if desired)
  ```bash
  git push origin --delete Main
  ```

- [ ] Remove branch synchronization workflow
  ```bash
  git rm .github/workflows/default-branch-sync.yml
  git commit -m "Remove default branch sync workflow"
  git push
  ```

- [ ] Archive this checklist for documentation

## Rollback Plan (If Needed)

If issues arise, you can rollback:

1. Change default branch back to `Main` in GitHub settings
2. Notify team to switch back: `git checkout Main`
3. Investigate and resolve issues
4. Re-attempt migration when ready

## Notes

**Date Started**: ______________  
**Date Completed**: ______________  
**Executed By**: ______________  
**Issues Encountered**: ______________

---

For detailed instructions, see [DEFAULT_BRANCH_GUIDE.md](DEFAULT_BRANCH_GUIDE.md)
