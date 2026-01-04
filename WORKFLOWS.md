# 🔄 GitHub Actions Workflows Documentation

This document provides an overview of all GitHub Actions workflows in the B-Agent repository, their purposes, schedules, and relationships.

## Active Workflows

### 1. BBR.yml - Barrot Build Relay
**Purpose**: Main build and deployment workflow  
**Trigger**: Push to `main` branch, manual dispatch  
**Schedule**: On every push to main  
**Key Functions**:
- Generates build manifest
- Updates barrot_manifest.json
- Deploys to GitHub Pages
- Enables SHRM_v2 reasoning engine
- Contradiction harvesting
- Temporal plasticity

**Status**: ✅ Core workflow - Essential

---

### 2. Barrot-SHRM-PingPong.yml
**Purpose**: Progressive ping-pong upgrade sessions with HRM variant council  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Every 15 minutes  
**Key Functions**:
- Progressive ping-pong cycles
- SHRM system updates
- Memory bundle logging
- Western AI Giants integration

**Status**: ✅ Active - SHRM system component

---

### 3. Barrot.Repo.Cleanup.yml
**Purpose**: Repository maintenance and cleanup  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Weekly on Sunday at midnight UTC  
**Key Functions**:
- Removes old bundles (keeps last 10)
- Cleans temporary files
- Removes logs and cache files

**Status**: ✅ Active - Maintenance workflow

---

### 4. agi-puzzle-discovery.yml
**Purpose**: AGI puzzle discovery using search skills  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Every 6 hours  
**Key Functions**:
- Practices search skills
- Discovers AGI puzzle pieces
- Tracks progress in memory bundles

**Status**: ✅ Active - Research workflow

---

### 5. ai-benchmark-testing.yml
**Purpose**: Comprehensive AI benchmark testing suite  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Weekly on Sunday at 00:00 UTC  
**Key Functions**:
- Runs complete benchmark suite
- 6-hour timeout for comprehensive testing
- System information display
- Python 3.11 environment

**Status**: ✅ Active - Testing workflow

---

### 6. arc-agi-parallel-test.yml
**Purpose**: Parallel testing for ARC-AGI challenges  
**Trigger**: Pull requests, push to main (for specific paths), manual dispatch  
**Paths Monitored**:
- `glyphs/**`
- `memory-bundles/arc-agi-**`
- Workflow file itself

**Key Functions**:
- Matrix-based parallel testing
- Multiple domain testing
- Fail-fast disabled for comprehensive results
- Concurrency control per ref

**Status**: ✅ Active - Testing workflow

---

### 7. asynchronous-insights.yml
**Purpose**: Continuous asynchronous insight generation  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Every 30 minutes (24/7/365)  
**Key Functions**:
- Problem-focused insights
- Continuous learning cycles
- Optional problem focus input

**Status**: ⚠️ Active - Consider resource optimization

**Note**: This workflow runs very frequently. Consider:
- Conditional execution based on actual need
- Self-hosted runners to avoid GitHub Actions minute consumption
- Event-driven triggers rather than fixed schedule

---

### 8. barrot-bundles.yml
**Purpose**: Manual bundle generation  
**Trigger**: Manual dispatch only  
**Key Functions**:
- Creates test bundles
- Commits to Barrot-Bundles directory
- Timestamped bundle creation

**Status**: ✅ Active - Manual utility workflow

---

### 9. barrot-cognition.yml
**Purpose**: Daily cognition cycle execution  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Daily at midnight UTC  
**Key Functions**:
- Runs matrix cognition nodes
- Configurable node selection
- Trigger source tracking

**Status**: ✅ Active - Core cognition workflow

---

### 10. peer-to-peer-validation.yml
**Purpose**: Continuous peer-to-peer agent validation  
**Trigger**: Manual dispatch, scheduled  
**Schedule**: Hourly  
**Key Functions**:
- P2P validation cycles
- Optional validation query input
- Meta-validation for high-stakes decisions

**Status**: ✅ Active - Validation workflow

---

## Workflow Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Build Pipeline                       │
│                                                                  │
│  Push to main → BBR.yml (Build Relay)                           │
│                     ↓                                            │
│              Updates manifest                                    │
│              Deploys to Pages                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Scheduled Maintenance                        │
│                                                                  │
│  Weekly    → Barrot.Repo.Cleanup.yml                            │
│  Weekly    → ai-benchmark-testing.yml                           │
│  Daily     → barrot-cognition.yml                               │
│  Hourly    → peer-to-peer-validation.yml                        │
│  Every 6h  → agi-puzzle-discovery.yml                           │
│  Every 30m → asynchronous-insights.yml                          │
│  Every 15m → Barrot-SHRM-PingPong.yml                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Testing Workflows                          │
│                                                                  │
│  PR/Push   → arc-agi-parallel-test.yml                          │
│             (on glyphs/** and memory-bundles/arc-agi-**)        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Manual Utilities                            │
│                                                                  │
│  Manual    → barrot-bundles.yml                                 │
│  Manual    → (All workflows support manual dispatch)            │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Permissions

Most workflows have:
- `contents: write` - To commit and push changes
- `pull-requests: write` - To comment on PRs (where applicable)
- `pages: write` - For GitHub Pages deployment (BBR.yml)
- `id-token: write` - For authentication (BBR.yml)

## Resource Considerations

### High-Frequency Workflows
These workflows run very frequently and consume GitHub Actions minutes:
1. **asynchronous-insights.yml** - Every 30 minutes (48 runs/day)
2. **Barrot-SHRM-PingPong.yml** - Every 15 minutes (96 runs/day)
3. **peer-to-peer-validation.yml** - Every hour (24 runs/day)

**Total scheduled runs per day**: 168 runs (48 + 96 + 24)

### Recommendations
For production usage:
- Consider self-hosted runners for high-frequency workflows
- Implement conditional execution based on actual need
- Use event-driven triggers instead of fixed schedules where possible
- Monitor GitHub Actions minutes usage

## Removed Workflows

### default-branch-sync.yml ❌
**Reason for Removal**: Obsolete after Main→main branch migration completed  
**Removal Date**: January 2026  
**Details**: This workflow synchronized the old `Main` branch with the new `main` branch during the migration period. Since the `Main` branch no longer exists, this workflow is no longer needed.

## Workflow Troubleshooting

### Common Issues

1. **Workflow not triggering on schedule**
   - Check if repository is active (GitHub may disable schedules on inactive repos)
   - Verify cron syntax
   - Check workflow permissions

2. **Permission denied errors**
   - Verify workflow has appropriate permissions in YAML
   - Check repository settings for Actions permissions
   - Ensure GITHUB_TOKEN has required scopes

3. **Workflow runs but no commits**
   - Check git configuration in workflow
   - Verify changes are staged before commit
   - Ensure push step has correct permissions

## Best Practices

1. **Use workflow_dispatch** - All workflows should support manual triggering for testing
2. **Proper error handling** - Workflows should handle errors gracefully
3. **Resource optimization** - Be mindful of GitHub Actions minutes consumption
4. **Documentation** - Keep this document updated when adding/modifying workflows
5. **Testing** - Test workflow changes on feature branches before merging to main

## Future Improvements

Potential areas for workflow optimization:
1. Consolidate similar scheduled workflows
2. Implement dynamic scheduling based on repository activity
3. Add workflow result notifications
4. Implement workflow dependencies where appropriate
5. Add more comprehensive error reporting
