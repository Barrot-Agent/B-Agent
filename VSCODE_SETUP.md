# 💻 VS Code Setup for Barrot-Agent

**Complete VS Code configuration for optimal Barrot-Agent development**  
**Last Updated**: 2025-12-23T13:06:00Z

---

## 🎯 Quick Start

### 1. Install VS Code
Download from [code.visualstudio.com](https://code.visualstudio.com/)

### 2. Open Barrot-Agent
```bash
cd /path/to/Barrot-Agent
code .
```

### 3. Install Recommended Extensions
VS Code will automatically prompt you to install recommended extensions from `.vscode/extensions.json`

---

## 📦 Recommended Extensions

The following extensions are pre-configured in `.vscode/extensions.json`:

### Essential
- **redhat.vscode-yaml** - YAML language support
- **esbenp.prettier-vscode** - Code formatter
- **github.vscode-pull-request-github** - GitHub integration
- **github.copilot** - AI pair programmer
- **github.copilot-chat** - AI chat assistant

### Git & GitHub
- **eamodio.gitlens** - Supercharged Git capabilities
- **ms-vscode.github-issues-prs** - GitHub issues and PRs

### Documentation
- **davidanson.vscode-markdownlint** - Markdown linting
- **yzhang.markdown-all-in-one** - Markdown tools
- **streetsidesoftware.code-spell-checker** - Spell checker

### Development
- **ms-python.python** - Python support
- **ms-python.vscode-pylance** - Python language server
- **ms-vscode.makefile-tools** - Makefile support

---

## ⚙️ VS Code Settings

Settings are pre-configured in `.vscode/settings.json`:

### Editor
- Format on save: **Enabled**
- Tab size: **2 spaces**
- Trim trailing whitespace: **Enabled**
- Insert final newline: **Enabled**

### YAML
- Schema validation: **Enabled**
- Format on save: **Enabled**
- GitHub workflow schema: **Auto-detected**

### Markdown
- Word wrap: **Enabled**
- Auto-suggestions: **Enabled**

### Git
- Smart commit: **Enabled**
- Sync confirmation: **Disabled** (for faster workflow)

---

## 🚀 Quick Tasks

Pre-configured tasks in `.vscode/tasks.json`:

### View Logs
```
Ctrl/Cmd + Shift + P → Tasks: Run Task → View Logs
```
Shows recent activity from `memory-bundles/activity-log.md`

### View Optimization Log
```
Ctrl/Cmd + Shift + P → Tasks: Run Task → View Optimization Log
```
Shows optimization history

### View Benchmark Results
```
Ctrl/Cmd + Shift + P → Tasks: Run Task → View Benchmark Results
```
Shows benchmark test scores

### View All Logs Summary
```
Ctrl/Cmd + Shift + P → Tasks: Run Task → View All Logs Summary
```
Shows combined summary of recent activities and optimizations

### Open Dashboard
```
Ctrl/Cmd + Shift + P → Tasks: Run Task → Open Dashboard
```
Opens Barrot-Agent dashboard in browser

---

## 🐛 Debug Configurations

Pre-configured in `.vscode/launch.json`:

### View Build Manifest
Launch configuration to view the build manifest with proper formatting

### Run Barrot Dashboard
Opens the dashboard in Chrome for debugging

---

## 📁 Workspace Organization

### File Explorer
Hidden files (configured in settings):
- `.git/` directory
- `node_modules/`
- `.DS_Store`

### Quick Navigation
Use **Ctrl/Cmd + P** to quickly open files:
- Type `build` → Opens build_manifest.yaml
- Type `readme` → Opens README.md
- Type `activity` → Opens activity-log.md

---

## 🔍 Search Features

### Find in Files
**Ctrl/Cmd + Shift + F**
- Search across all documentation
- Filter by file type
- Regex support enabled

### Find in Selection
**Ctrl/Cmd + F** then **Alt + L**
- Search within selected text

---

## 💡 Productivity Tips

### 1. Command Palette
**Ctrl/Cmd + Shift + P**
- Access all VS Code commands
- Run tasks
- Change settings
- Install extensions

### 2. Integrated Terminal
**Ctrl/Cmd + `** (backtick)
- Access bash terminal
- Run git commands
- View log files
- Execute scripts

### 3. Side-by-Side Editing
**Ctrl/Cmd + \\** 
- Split editor
- Compare files
- Review changes

### 4. Zen Mode
**Ctrl/Cmd + K, Z**
- Distraction-free editing
- Focus on single file
- Full screen mode

### 5. Multi-Cursor Editing
**Alt + Click** or **Ctrl/Cmd + Alt + ↑/↓**
- Edit multiple locations simultaneously
- Batch rename variables
- Format multiple lines

---

## 🎨 Customization

### Change Theme
```
Ctrl/Cmd + K, Ctrl/Cmd + T
```
Default: **Dark+ (Default Dark)**

### Modify Settings
```
Ctrl/Cmd + ,
```
Settings UI or edit `.vscode/settings.json` directly

### Add Custom Tasks
Edit `.vscode/tasks.json` to add your own tasks

### Create Snippets
```
File → Preferences → User Snippets
```
Create custom code snippets for faster development

---

## 🔗 GitHub Integration

### Pull Requests
- View PRs directly in VS Code
- Review code changes
- Comment on lines
- Approve or request changes

### Issues
- Browse repository issues
- Create new issues
- Assign and label
- Link to code

### Commits & History
- View commit history with GitLens
- Blame annotations
- File history
- Branch comparisons

---

## 📊 Monitoring Barrot Progress

### View Logs in VS Code
1. Open integrated terminal (**Ctrl/Cmd + `**)
2. Run log viewing commands:

```bash
# View activity log
cat memory-bundles/activity-log.md | tail -50

# View optimizations
cat memory-bundles/optimization-log.md | tail -30

# View benchmark results
cat memory-bundles/benchmark-results.md

# View all recent activity
ls -la memory-bundles/
```

### Watch Log Files
Install "Log File Highlighter" extension:
```
Ctrl/Cmd + Shift + X → Search "Log File Highlighter"
```
Then open log files for syntax highlighting

---

## 🚦 Common Workflows

### 1. Check Recent Activity
```bash
# Terminal
cd memory-bundles
tail -30 activity-log.md
```

### 2. Review Optimizations
```
Tasks: Run Task → View Optimization Log
```

### 3. Update Documentation
1. Edit markdown file
2. Save (auto-format enabled)
3. Preview with **Ctrl/Cmd + Shift + V**
4. Commit changes

### 4. View Dashboard
```
Tasks: Run Task → Open Dashboard
```

---

## 🛠️ Troubleshooting

### Extensions Not Installing
```bash
# Reinstall extensions manually
code --install-extension redhat.vscode-yaml
code --install-extension esbenp.prettier-vscode
code --install-extension github.copilot
```

### Settings Not Applying
1. Close and reopen VS Code
2. Reload window: **Ctrl/Cmd + Shift + P** → "Reload Window"
3. Check `.vscode/settings.json` for syntax errors

### Terminal Issues
- Use **Ctrl/Cmd + Shift + `** to create new terminal
- Verify bash is available: `which bash`
- Check terminal profile settings

### File Association Issues
Update file associations in settings:
```json
"files.associations": {
  "*.yaml": "yaml",
  "*.yml": "yaml",
  "*.md": "markdown"
}
```

---

## 📚 Additional Resources

### VS Code Documentation
- [Getting Started](https://code.visualstudio.com/docs)
- [Tips and Tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [Keyboard Shortcuts](https://code.visualstudio.com/docs/getstarted/keybindings)

### Barrot-Agent Specific
- [MOBILE_SETUP.md](MOBILE_SETUP.md) - Mobile development setup
- [OUTPUT_LOGGING.md](OUTPUT_LOGGING.md) - Logging framework
- [AGI_DEVELOPMENT.md](AGI_DEVELOPMENT.md) - AGI development guide

---

## 🎯 Next Steps

1. ✅ Install recommended extensions
2. ✅ Familiarize with keyboard shortcuts
3. ✅ Explore pre-configured tasks
4. ✅ Set up GitHub authentication
5. ✅ Start monitoring Barrot logs
6. ✅ Join the development workflow

---

## 💬 Get Help

- **Issues**: [GitHub Issues](https://github.com/Barrot-Agent/B-Agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Barrot-Agent/B-Agent/discussions)
- **Email**: barrot-agent@example.com

---

**VS Code Setup Version**: 1.0  
**Last Updated**: 2025-12-23T13:06:00Z  
**Status**: Production Ready

---

🦜 **Happy Coding with Barrot-Agent!** ✨
