# OneDrive ↔ GitHub Sync Setup

This document describes the setup for automatic synchronization between OneDrive and GitHub to enable Barrot cognition triggers from external sources.

## Architecture

```
OneDrive (run_matrix.txt) → Power Automate → GitHub Actions → Matrix Execution
```

## Setup Instructions

### 1. OneDrive Setup

1. Create a dedicated folder in OneDrive: `Barrot-Triggers/`
2. This folder will be monitored for trigger files

### 2. Power Automate Flow

Create a new automated cloud flow in Power Automate with the following configuration:

#### Trigger
- **Name:** When a file is created or modified
- **Location:** OneDrive for Business or OneDrive Personal
- **Folder:** `/Barrot-Triggers/`
- **Include sub-folders:** No
- **How often:** Every 1 minute

#### Condition
- **Condition:** File name equals `run_matrix.txt`

#### Action: Trigger GitHub Workflow
- **HTTP Method:** POST
- **URL:** `https://api.github.com/repos/Barrot-Agent/B-Agent/actions/workflows/barrot-cognition.yml/dispatches`
- **Headers:**
  ```json
  {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "Bearer YOUR_GITHUB_TOKEN",
    "Content-Type": "application/json"
  }
  ```
- **Body:**
  ```json
  {
    "ref": "main",
    "inputs": {
      "trigger_source": "onedrive",
      "trigger_time": "@{utcNow()}"
    }
  }
  ```

#### Action: Log to GitHub
- **HTTP Method:** POST
- **URL:** `https://api.github.com/repos/Barrot-Agent/B-Agent/dispatches`
- **Body:** Log the sync event to memory-bundles/

### 3. GitHub Actions Workflow

Create `.github/workflows/barrot-cognition.yml`:

```yaml
name: Barrot Cognition Cycle
on:
  workflow_dispatch:
    inputs:
      trigger_source:
        description: 'Source of the trigger'
        required: false
        default: 'manual'
      trigger_time:
        description: 'Time of trigger'
        required: false

jobs:
  run-cognition:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run Barrot Bootstrap
        run: python barrot_bootstrap.py
      
      - name: Log Sync Event
        run: |
          echo "## Sync Event: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> memory-bundles/onedrive-sync-log.md
          echo "**Trigger Source:** ${{ github.event.inputs.trigger_source }}" >> memory-bundles/onedrive-sync-log.md
          echo "**Trigger Time:** ${{ github.event.inputs.trigger_time }}" >> memory-bundles/onedrive-sync-log.md
          echo "---" >> memory-bundles/onedrive-sync-log.md
      
      - name: Commit Results
        run: |
          git config user.name "Barrot Agent"
          git config user.email "barrot@agent.local"
          git add .
          git commit -m "Cognition cycle completed via OneDrive sync" || echo "No changes"
          git push || echo "No changes to push"
```

### 4. Sync Event Logging

All sync events are logged to `memory-bundles/onedrive-sync-log.md` with:
- Timestamp (UTC)
- Trigger source (OneDrive/manual/scheduled)
- Cognition nodes executed
- Glyphs emitted
- Any errors or warnings

## Trigger File Format

The `run_matrix.txt` file in OneDrive can contain optional parameters:

```
nodes=node_self_reflect,node_diff_detector
priority=high
reason=Manual cognition check requested by Sean
```

If empty, all matrix nodes will be executed.

## Security Considerations

1. **GitHub Token:** Use a Personal Access Token (PAT) with `repo` and `workflow` scopes
2. **Token Storage:** Store the PAT securely in Power Automate (use encrypted connections)
3. **Rate Limiting:** Power Automate checks OneDrive every minute but only triggers on file changes
4. **Access Control:** Ensure only authorized users can write to the OneDrive trigger folder

## Testing

1. Create `run_matrix.txt` in OneDrive `Barrot-Triggers/` folder
2. Wait up to 1 minute for Power Automate to detect the change
3. Verify GitHub Actions workflow is triggered
4. Check `memory-bundles/onedrive-sync-log.md` for the logged event

## Troubleshooting

### Flow not triggering
- Verify OneDrive folder path is correct
- Check Power Automate run history for errors
- Ensure file name is exactly `run_matrix.txt`

### GitHub workflow fails
- Verify GitHub token has correct permissions
- Check GitHub Actions logs for error details
- Ensure repository workflows are enabled

### No sync log created
- Verify git push permissions in GitHub Actions
- Check for commit conflicts
- Review workflow step logs

## Future Enhancements

- Two-way sync: GitHub → OneDrive for results
- Email notifications on cognition completion
- Slack/Teams integration for glyph emissions
- Mobile app trigger support
