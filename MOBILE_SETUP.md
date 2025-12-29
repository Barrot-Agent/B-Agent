# 📱 Barrot-Agent Mobile Setup Guide

Welcome! This guide will help you set up and interact with Barrot-Agent directly from your cellphone.

## 🎯 Overview

Barrot-Agent can be accessed and managed from your mobile device in several ways:
- **Web Dashboard** - Access the Barrot dashboard through your mobile browser
- **GitHub Mobile** - Monitor workflows and repository activity
- **Terminal Emulators** - Run Barrot commands directly on your phone
- **Git Operations** - Clone and manage the repository from mobile

---

## 📱 Quick Start - Web Access (Easiest)

### Access the Barrot Dashboard

The simplest way to interact with Barrot-Agent is through the web dashboard:

1. **Open your mobile browser** (Chrome, Safari, Firefox, etc.)
2. **Navigate to**: `https://barrot-agent.github.io/Barrot-Agent/`
3. **Bookmark the page** for quick access

The dashboard displays:
- Current build status
- Rail status (ingestion, deployment, microagent, prediction, dashboard, cognition)
- Build manifest information
- Timestamp of last update

---

## 📱 Setup via GitHub Mobile App

### Install GitHub Mobile

**Android:**
1. Open Google Play Store
2. Search for "GitHub"
3. Install the official GitHub app
4. Sign in with your GitHub account

**iOS:**
1. Open App Store
2. Search for "GitHub"
3. Install the official GitHub app
4. Sign in with your GitHub account

### Access Barrot-Agent Repository

1. Open GitHub app
2. Navigate to **Repositories**
3. Search for `Barrot-Agent/Barrot-Agent`
4. Tap to open the repository

### Monitor and Trigger Workflows

1. In the repository, go to **Actions** tab
2. View workflow runs and their status
3. Trigger manual workflows (if you have permissions):
   - Tap on a workflow
   - Tap "Run workflow"
   - Select branch and parameters
   - Confirm to trigger

---

## 🔧 Advanced Setup - Terminal Access

For advanced users who want to run Git commands and scripts on their phone:

### Android - Using Termux

**Termux** is a powerful terminal emulator for Android that provides a Linux environment.

#### Step 1: Install Termux

1. **Download from F-Droid** (recommended):
   - Visit: https://f-droid.org/
   - Search for "Termux"
   - Install the app

   OR

2. **Download from GitHub Releases**:
   - Visit: https://github.com/termux/termux-app/releases
   - Download the latest APK
   - Install the APK (enable "Unknown Sources" if needed)

⚠️ **Note**: The Google Play Store version is outdated. Use F-Droid or GitHub releases.

#### Step 2: Set Up Termux Environment

Open Termux and run these commands:

```bash
# Update package lists
pkg update && pkg upgrade -y

# Install essential tools
pkg install -y git curl wget nodejs python

# Install optional tools
pkg install -y vim nano
```

#### Step 3: Configure Git

```bash
# Set your Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Configure GitHub authentication (use personal access token)
git config --global credential.helper store
```

#### Step 4: Clone Barrot-Agent Repository

```bash
# Navigate to home directory
cd ~

# Create projects directory
mkdir -p projects
cd projects

# Clone the repository
git clone https://github.com/Barrot-Agent/Barrot-Agent.git

# Navigate into the repository
cd Barrot-Agent

# Verify the clone
ls -la
```

#### Step 5: Work with Barrot-Agent

```bash
# View build manifest
cat build_manifest.yaml

# Check repository status
git status

# Pull latest changes
git pull

# View spells
cat spells/omega-ingest.md
cat spells/keyseer-insight.md

# View memory bundles
ls -la memory-bundles/
```

#### Step 6: Set Up SSH Keys (Optional)

For easier Git operations:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# View your public key
cat ~/.ssh/id_ed25519.pub

# Copy the output and add it to GitHub:
# Go to GitHub.com → Settings → SSH and GPG keys → New SSH key
```

### iOS - Using iSH Shell

**iSH** is a Linux shell environment for iOS devices.

#### Step 1: Install iSH

1. Open **App Store**
2. Search for "iSH Shell"
3. Install the app
4. Open iSH

#### Step 2: Set Up iSH Environment

```bash
# Update package manager
apk update
apk upgrade

# Install essential tools
apk add git curl wget nodejs python3

# Install text editors
apk add vim nano
```

#### Step 3: Configure Git

```bash
# Set your Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Step 4: Clone Barrot-Agent Repository

```bash
# Navigate to home
cd ~

# Clone the repository
git clone https://github.com/Barrot-Agent/Barrot-Agent.git

# Navigate into the repository
cd Barrot-Agent

# View contents
ls -la
```

#### Step 5: Work with Barrot-Agent

Same commands as Android Termux (see above).

---

## 🌐 Mobile Browser Features

### Viewing the Repository Website

1. Open browser on your phone
2. Navigate to: `https://barrot-agent.github.io/Barrot-Agent/`
3. View live build status and manifests

### Using GitHub.com Mobile Site

1. Navigate to: `https://github.com/Barrot-Agent/Barrot-Agent`
2. Tap the menu icon (≡) to access:
   - Code
   - Issues
   - Pull Requests
   - Actions (workflows)
   - Projects
   - Wiki
   - Settings

---

## 🔐 Authentication Setup

### Personal Access Token (PAT)

To authenticate Git operations on mobile:

1. **Generate a token**:
   - Go to GitHub.com on your phone browser
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token
   - Select scopes: `repo`, `workflow`, `read:org`
   - Copy the token

2. **Use the token**:
   ```bash
   # When prompted for password, use the PAT
   git clone https://github.com/Barrot-Agent/Barrot-Agent.git
   # Username: your-github-username
   # Password: [paste your PAT]
   ```

3. **Save credentials** (optional):
   ```bash
   git config --global credential.helper store
   # Next time you authenticate, credentials will be saved
   ```

---

## 📊 Monitoring Barrot Activity

### Check Build Status

**Via Web Dashboard:**
```
https://barrot-agent.github.io/Barrot-Agent/
```

**Via GitHub Actions:**
```
https://github.com/Barrot-Agent/Barrot-Agent/actions
```

**Via Mobile Terminal:**
```bash
cd ~/projects/Barrot-Agent
git pull
cat build_manifest.yaml
```

### View Recent Activity

```bash
# Check commit history
git log --oneline -10

# View recent changes
git diff HEAD~1

# Check branch status
git branch -a
```

---

## 📁 Understanding Barrot-Agent Structure

When you browse the repository on mobile, here's what each directory contains:

```
Barrot-Agent/
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── Barrot-Agent/           # Agent configuration
├── Barrot-Bundles/         # Bundle storage
├── memory-bundles/         # Memory and outcome logs
│   ├── build-ledger.json   # Build history
│   ├── outcome-relay.md    # Activity log
│   └── protocols/          # Protocol definitions
├── site/                   # Website files
│   └── index.html          # Dashboard HTML
├── spells/                 # Agent capabilities
│   ├── omega-ingest.md     # Data ingestion spell
│   └── keyseer-insight.md  # Key analysis spell
├── build_manifest.yaml     # Current build manifest
├── barrot-unified.yml      # Unified workflow (build relay, ping-pong, cleanup, bundles)
├── Dockerfile              # Container configuration
├── package.json            # Node package config
└── README.md               # Main documentation
```

---

## 🚀 Mobile Workflow Tips

### 1. **Use Shortcuts** (iOS)
Create iOS Shortcuts to:
- Open Barrot dashboard
- Open GitHub repository
- Open Termux/iSH with auto-navigation to Barrot directory

### 2. **Home Screen Widgets**
- Add GitHub widget to track repository activity
- Bookmark Barrot dashboard for quick access

### 3. **Notifications**
Enable GitHub notifications for:
- Workflow runs
- Pull requests
- Issues
- Releases

### 4. **Quick Commands**
Create shell aliases in Termux/iSH:

```bash
# Add to ~/.bashrc or ~/.profile
alias barrot='cd ~/projects/Barrot-Agent'
alias bstatus='cat ~/projects/Barrot-Agent/build_manifest.yaml'
alias bpull='cd ~/projects/Barrot-Agent && git pull'
alias blogs='cat ~/projects/Barrot-Agent/memory-bundles/outcome-relay.md | tail -20'
```

Then reload:
```bash
source ~/.bashrc
```

---

## 🐛 Troubleshooting

### Can't Clone Repository

**Issue**: Authentication fails
**Solution**: 
- Use Personal Access Token instead of password
- Check token permissions include `repo` scope

### Termux Not Working

**Issue**: Commands fail or packages won't install
**Solution**:
```bash
termux-change-repo  # Select mirror
pkg update && pkg upgrade
```

### iSH Freezes or Crashes

**Issue**: App becomes unresponsive
**Solution**:
- Force close and reopen
- Ensure iOS is up to date
- Try simpler commands first

### Can't Push Changes

**Issue**: Permission denied
**Solution**:
- Ensure you have write access to the repository
- Check if you're authenticated correctly
- Verify your Git credentials

---

## 📚 Additional Resources

### Documentation
- **Main README**: Check the repository's README.md
- **Spells**: Read the spell documentation in `spells/` directory
- **Build Manifest**: Review `build_manifest.yaml` for current status

### Community
- **GitHub Issues**: Report problems or ask questions
- **Discussions**: Join conversations about Barrot-Agent

### Tools
- **Termux Wiki**: https://wiki.termux.com/
- **iSH Documentation**: https://github.com/ish-app/ish
- **GitHub Mobile Docs**: https://docs.github.com/en/get-started/using-github/github-mobile

---

## 🎉 You're All Set!

You can now access and manage Barrot-Agent from your cellphone. Choose the method that works best for you:

- 🌐 **Casual User**: Use the web dashboard
- 📱 **Regular User**: Install GitHub mobile app
- 💻 **Power User**: Set up Termux/iSH terminal

Happy Barroting! 🦜
