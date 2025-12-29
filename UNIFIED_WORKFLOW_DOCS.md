# Barrot Unified Workflow Documentation

## Overview

The Barrot Unified Workflow (`.github/workflows/barrot-unified.yml`) consolidates all major automated tasks for the Barrot-Agent system into a single, cohesive workflow file. This unified approach reduces redundancy, improves maintainability, and provides better control over workflow execution.

## Consolidated Workflows

This unified workflow replaces the following separate workflows:
- `BBR.yml` - Build relay and dashboard publishing
- `Barrot-SHRM-PingPong.yml` - Health monitoring ping-pong
- `Barrot.Repo.Cleanup.yml` - Repository maintenance
- `workflows.barrot.bundles.yml` - Bundle generation

**Note:** The `default-branch-sync.yml` workflow is intentionally excluded from consolidation as it is migration-specific and should be removed after the Main→main branch migration is complete.

## Jobs

### 1. Update Manifest (`update-manifest`)

**Purpose:** Updates the build manifest with current system status and timestamp.

**Triggers:**
- Push to `main` branch
- Manual dispatch (with `build` or `all` option)

**Actions:**
- Generates `build_manifest.yaml` with:
  - Build signature: BNDL-V2
  - Timestamp
  - Reasoning engine: SHRM_v2
  - Rail status (ingestion, deployment, microagent, prediction, dashboard, cognition)
- Commits and pushes changes to repository

### 2. Publish Dashboard (`publish-dashboard`)

**Purpose:** Generates and publishes the Barrot dashboard to GitHub Pages.

**Triggers:**
- Runs after `update-manifest` completes successfully
- Push to `main` branch
- Manual dispatch (with `build` or `all` option)

**Actions:**
- Pulls latest changes including updated manifest
- Generates HTML dashboard from build manifest
- Deploys to GitHub Pages using peaceiris/actions-gh-pages@v4

**Dashboard URL:** `https://barrot-agent.github.io/Barrot-Agent/`

### 3. Barrot-SHRM Ping-Pong (`barrot-ping-pong`)

**Purpose:** Executes health check communication between Barrot and SHRM systems.

**Triggers:**
- Schedule: Every 15 minutes (`*/15 * * * *`)
- Manual dispatch (with `ping-pong` or `all` option)

**Actions:**
- Sends PING signal from Barrot to SHRM
- Receives PONG response from SHRM
- Updates logs:
  - `memory-bundles/outcome-relay.md`
  - `SHRM-System/shrm-response-log.md`
- Updates SHRM configuration with last ping timestamp
- Updates build ledger: `memory-bundles/build-ledger.json`
- Commits and pushes all changes

### 4. Repository Cleanup (`repo-cleanup`)

**Purpose:** Performs automated repository maintenance to keep the repo clean.

**Triggers:**
- Schedule: Weekly on Sunday at midnight UTC (`0 0 * * 0`)
- Manual dispatch (with `cleanup` or `all` option)

**Actions:**
- Removes old bundles from `Barrot-Bundles/` directory (keeps last 10)
- Removes temporary files:
  - `tmp/` directory
  - `*.log` files
  - `*.cache` files
- Commits and pushes cleanup changes

### 5. Generate Bundle (`generate-bundle`)

**Purpose:** Creates test bundles and saves them to the repository.

**Triggers:**
- Manual dispatch only (with `bundle` or `all` option)

**Actions:**
- Generates timestamped test bundle in `Barrot-Bundles/`
- Commits and pushes new bundle to repository

## Manual Execution

The unified workflow supports selective job execution via workflow dispatch:

1. Navigate to **Actions** tab in GitHub repository
2. Select **Barrot Unified Workflow**
3. Click **Run workflow**
4. Select which job(s) to run:
   - `all` - Run all applicable jobs
   - `build` - Run manifest update and dashboard publishing
   - `ping-pong` - Run health check cycle
   - `cleanup` - Run repository maintenance
   - `bundle` - Generate a new bundle

## Permissions

The workflow requires the following permissions:
- `contents: write` - To commit and push changes
- `pages: write` - To deploy to GitHub Pages
- `id-token: write` - For GitHub Pages deployment authentication

## Benefits of Consolidation

### 1. **Reduced Redundancy**
- Single workflow file instead of 4 separate files
- Shared permission declarations
- Consistent checkout and git configuration patterns

### 2. **Improved Maintainability**
- Easier to update and modify workflow logic
- Centralized documentation and comments
- Single source of truth for all automation

### 3. **Better Control**
- Selective job execution via workflow dispatch
- Clear job dependencies (e.g., dashboard depends on manifest)
- Conditional execution based on trigger type

### 4. **Enhanced Visibility**
- All jobs visible in a single workflow run
- Easier to track overall system automation status
- Consolidated workflow run history

## Migration Notes

### Removed Workflows
After the unified workflow is active and tested, the following files should be removed:
- `.github/workflows/BBR.yml`
- `.github/workflows/Barrot-SHRM-PingPong.yml`
- `.github/workflows/Barrot.Repo.Cleanup.yml`
- `.github/workflows.barrot.bundles.yml`

### Separate Workflows
The following workflow remains separate:
- `.github/workflows/default-branch-sync.yml` - Should be removed after Main→main migration is complete

## Monitoring

Monitor workflow execution through:
1. **GitHub Actions Tab** - View all workflow runs
2. **Dashboard** - Check published dashboard for build status
3. **Log Files** - Review ping-pong logs and build ledger
4. **Commits** - Track automated commits from workflow jobs

## Troubleshooting

### Job Not Running
- Check trigger conditions in job `if` statements
- Verify schedule is correct for scheduled jobs
- Ensure proper workflow dispatch input selection

### Git Push Failures
- Check repository permissions
- Verify branch protection rules allow workflow commits
- Ensure `GITHUB_TOKEN` has appropriate permissions

### Dashboard Not Updating
- Verify GitHub Pages is enabled for the repository
- Check that `publish-dashboard` job completed successfully
- Confirm peaceiris/actions-gh-pages action is functioning

## Future Enhancements

Potential improvements to consider:
- Add notification integration (Slack, Discord, email)
- Implement failure recovery mechanisms
- Add more granular job controls
- Include metrics and reporting
- Integrate with external monitoring systems
