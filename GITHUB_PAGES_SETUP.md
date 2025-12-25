# GitHub Pages Setup Guide for Barrot Agent

This guide will help you enable GitHub Pages for the Barrot Agent dashboard.

## Quick Setup

### Step 1: Enable GitHub Pages
1. Navigate to your repository on GitHub
2. Click on **Settings** (top right)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### Step 2: Trigger Deployment
The dashboard will be automatically deployed when:
- Code is pushed to the `main` branch
- You manually trigger the "Deploy to GitHub Pages" workflow

To manually trigger deployment:
1. Go to **Actions** tab
2. Click on "Deploy to GitHub Pages" workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**

### Step 3: Access Your Dashboard
Once deployed, your dashboard will be available at:
```
https://barrot-agent.github.io/Barrot-Agent/
```

## Troubleshooting

### Pages Not Showing Up
- Check that GitHub Pages is enabled in Settings → Pages
- Verify that the workflow ran successfully in the Actions tab
- Wait a few minutes for DNS propagation

### Workflow Failures
- Ensure repository has Pages enabled
- Check that the workflow has proper permissions (should be automatic)
- Review workflow logs for specific errors

### Custom Domain (Optional)
To use a custom domain:
1. Go to Settings → Pages
2. Enter your custom domain under "Custom domain"
3. Follow GitHub's instructions for DNS configuration

## Features

The deployed dashboard includes:
- 🧠 Real-time cognition metrics
- ⚙️ System status indicators
- 📦 Active modules list
- 🔄 Ping-pong protocol monitoring
- ✨ Active spell protocols
- 📚 Connected resources display

## Updates

The dashboard automatically updates when:
- Changes are pushed to `main` branch
- The GitHub Pages workflow is manually triggered
- System metrics are updated by other workflows

---

**Note**: After enabling GitHub Pages, the first deployment may take a few minutes. Subsequent updates are faster.
