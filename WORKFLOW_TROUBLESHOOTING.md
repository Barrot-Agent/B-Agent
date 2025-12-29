# 🔧 Workflow Troubleshooting Guide

**Last Updated**: 2025-12-29  
**Status**: Active

---

## 📊 Workflow Overview

Barrot-Agent uses several GitHub Actions workflows to automate repository management, build processes, and system monitoring.

### Active Workflows

| Workflow | Purpose | Trigger | Status |
|----------|---------|---------|--------|
| **BBR.yml** | Barrot Build Relay - Updates build manifest and deploys dashboard | Push to main, Manual | ✅ Fixed |
| **Barrot-SHRM-PingPong.yml** | Ping-pong monitoring between Barrot and SHRM systems | Every 15 min, Manual | ✅ Optimized |
| **barrot-bundles.yml** | Creates and saves test bundles | Manual | ✅ Fixed |
| **Barrot.Repo.Cleanup.yml** | Weekly repository cleanup | Sunday midnight, Manual | ✅ Optimized |
| **default-branch-sync.yml** | Syncs Main → main during migration | Manual, Push to Main | ⚠️ Temporary |

---

## 🚨 Common Issues & Solutions

### Issue 1: BBR Workflow Infinite Loop
**Symptom**: BBR workflow triggers itself repeatedly  
**Cause**: Workflow commits trigger new workflow runs  
**Solution**: ✅ Fixed - Added `[skip ci]` to commit messages

```yaml
git commit -m "🔄 Update build manifest [skip ci]"
```

### Issue 2: Workflow Files in Wrong Location
**Symptom**: Workflows don't appear in Actions tab  
**Cause**: File was at `.github/workflows.barrot.bundles.yml` instead of `.github/workflows/`  
**Solution**: ✅ Fixed - Moved to correct location with proper naming

### Issue 3: Empty Commits Causing Failures
**Symptom**: Git push fails with "nothing to commit"  
**Cause**: Using `git commit -m "..." || echo "No changes"` doesn't prevent push  
**Solution**: ✅ Fixed - Added proper conditional logic:

```yaml
if ! git diff --staged --quiet; then
  git commit -m "message"
  git push
else
  echo "✅ No changes to commit"
fi
```

### Issue 4: Outdated Actions Versions
**Symptom**: Security warnings, deprecated features  
**Cause**: Using `actions/checkout@v3`  
**Solution**: ✅ Fixed - Updated all workflows to use `@v4`

### Issue 5: Missing Directories Cause Failures
**Symptom**: Workflow fails when directories don't exist  
**Cause**: Commands like `echo >> file.md` fail if parent dir missing  
**Solution**: ✅ Fixed - Added `mkdir -p` before file operations:

```yaml
mkdir -p memory-bundles SHRM-System
echo "content" >> memory-bundles/file.md
```

---

## 🔍 Debugging Workflows

### Viewing Workflow Logs

1. Go to [Actions tab](https://github.com/Barrot-Agent/Barrot-Agent/actions)
2. Click on the failed workflow run
3. Click on the failed job
4. Review step-by-step logs

### Local Testing

Test workflow logic locally:

```bash
# Test manifest generation
cat <<EOF > build_manifest.yaml
build_signature: BNDL-V2
timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

# Test directory creation
mkdir -p memory-bundles SHRM-System

# Test conditional commits
git add .
if ! git diff --staged --quiet; then
  echo "Would commit"
else
  echo "No changes"
fi
```

### Checking Workflow Syntax

```bash
# Install act (GitHub Actions local runner)
# brew install act  # macOS
# choco install act  # Windows

# Test workflow locally
act -l  # List workflows
act push  # Simulate push event
```

---

## 🛠️ Workflow Best Practices

### 1. Always Use Specific Action Versions

❌ **Bad**: `uses: actions/checkout@v3` (outdated)  
✅ **Good**: `uses: actions/checkout@v4` (latest stable)  
✅ **Better**: Pin to specific SHA for maximum security (e.g., `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11`)

### 2. Prevent Infinite Loops

- Add `[skip ci]` or `[ci skip]` to commit messages
- Use workflow filters: `if: github.event.head_commit.message != 'skip ci'`
- Avoid workflows that trigger themselves

### 3. Handle Edge Cases

```yaml
# Check if file exists before processing
if [ -f "file.txt" ]; then
  process file.txt
fi

# Check if directory has files
if [ "$(ls -A directory/)" ]; then
  process files
fi

# Use || true for non-critical commands
rm -f temp.txt || true
```

### 4. Use Proper Git Configuration

```yaml
# Use bot identity for automated commits
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# Or use service identity
git config user.name "Barrot-Agent"
git config user.email "barrot@systems.local"
```

### 5. Add Meaningful Output

```yaml
- name: Deploy Dashboard
  run: |
    echo "🚀 Deploying dashboard..."
    # deployment commands
    echo "✅ Dashboard deployed successfully!"
```

---

## 🔐 Security Considerations

### Permissions

Always use minimal required permissions:

```yaml
permissions:
  contents: write  # For commits
  pages: write     # For GitHub Pages
  id-token: write  # For OIDC
```

### Secrets

Never hardcode secrets in workflows:

❌ **Bad**: `token: ghp_xxxxxxxxxxxx`  
✅ **Good**: `token: ${{ secrets.GITHUB_TOKEN }}`

---

## 📈 Monitoring & Maintenance

### Regular Checks

- [ ] Review workflow runs weekly
- [ ] Update action versions monthly
- [ ] Check for deprecated features
- [ ] Monitor workflow execution time
- [ ] Review permissions quarterly

### Performance Optimization

```yaml
# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# Limit fetch depth
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Shallow clone for speed
```

---

## 🆘 Getting Help

### Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

### Reporting Issues

1. Check this troubleshooting guide first
2. Review recent workflow runs in Actions tab
3. Check for similar issues in repository issues
4. Create new issue with:
   - Workflow name
   - Error message
   - Link to failed run
   - Steps to reproduce

---

## 📝 Change Log

### 2025-12-29: Major Workflow Refactor

- ✅ Fixed BBR infinite loop issue
- ✅ Moved misplaced `workflows.barrot.bundles.yml` 
- ✅ Updated all workflows to use `actions/checkout@v4`
- ✅ Added proper error handling and conditionals
- ✅ Improved commit messages with emojis
- ✅ Added `[skip ci]` tags where appropriate
- ✅ Created directory existence checks
- ✅ Standardized git user configuration

---

**Maintained by**: Barrot-Agent Development Team  
**Last Review**: 2025-12-29
