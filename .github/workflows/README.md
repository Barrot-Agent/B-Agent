# GitHub Workflows

This directory contains GitHub Actions workflows for the Barrot-Agent repository.

## Active Workflows

### 1. `barrot-unified.yml` - Barrot Unified Workflow
**Status:** ✅ Active

This is the primary workflow that consolidates all major automated tasks for the Barrot-Agent system.

**Jobs:**
- `update-manifest` - Updates build manifest with system status
- `publish-dashboard` - Publishes dashboard to GitHub Pages
- `barrot-ping-pong` - Health monitoring ping-pong with SHRM
- `repo-cleanup` - Repository maintenance and cleanup
- `generate-bundle` - Bundle generation

**Triggers:**
- Push to `main` branch
- Schedule: Every 15 minutes (ping-pong), Weekly on Sunday (cleanup)
- Manual dispatch with selective job execution

**Documentation:** See `/UNIFIED_WORKFLOW_DOCS.md` for detailed information.

### 2. `default-branch-sync.yml` - Default Branch Sync
**Status:** ⚠️ Migration-specific (to be removed)

This workflow synchronizes the old 'Main' branch with the new 'main' branch during the migration period.

**Action Required:** This workflow should be removed after the Main→main branch migration is complete.

## Consolidated Workflows

The following workflows have been consolidated into `barrot-unified.yml`:
- ~~`BBR.yml`~~ → `update-manifest` and `publish-dashboard` jobs
- ~~`Barrot-SHRM-PingPong.yml`~~ → `barrot-ping-pong` job
- ~~`Barrot.Repo.Cleanup.yml`~~ → `repo-cleanup` job
- ~~`workflows.barrot.bundles.yml`~~ → `generate-bundle` job

## Workflow Management

### Running Workflows Manually
1. Go to the **Actions** tab
2. Select the workflow you want to run
3. Click **Run workflow**
4. For `barrot-unified.yml`, select which job(s) to run

### Monitoring Workflows
- **Actions Tab:** View all workflow runs and their status
- **Dashboard:** Check https://barrot-agent.github.io/Barrot-Agent/ for build status
- **Logs:** Review automated commit messages in repository history

## Contributing

When modifying workflows:
1. Test changes in a feature branch first
2. Validate YAML syntax before committing
3. Update documentation if changing workflow behavior
4. Consider impact on scheduled jobs
5. Ensure proper permissions are set

## Support

For issues or questions about workflows:
- Check `/UNIFIED_WORKFLOW_DOCS.md` for detailed documentation
- Review workflow run logs in the Actions tab
- Open an issue for workflow-related problems
