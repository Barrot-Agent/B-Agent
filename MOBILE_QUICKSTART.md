# 📱 Barrot-Agent Mobile Quick Reference

## 🚀 Fastest Ways to Access Barrot on Mobile

### 1️⃣ Web Dashboard (No Setup Required)
Just open in your phone browser:
```
https://barrot-agent.github.io/B-Agent/
```

### 2️⃣ GitHub Mobile App
1. Install GitHub app from App Store / Play Store
2. Open app → Search "Barrot-Agent/B-Agent"
3. Access: Code, Actions, Issues, etc.

### 3️⃣ Terminal Access (Advanced)

**Android - Termux:**
```bash
# Install from F-Droid, then run:
pkg update && pkg install git
git clone https://github.com/Barrot-Agent/B-Agent.git
cd Barrot-Agent
```

**iOS - iSH:**
```bash
# Install from App Store, then run:
apk add git
git clone https://github.com/Barrot-Agent/B-Agent.git
cd Barrot-Agent
```

## ⚡ Quick Commands

### Check Build Status
```bash
cat build_manifest.yaml
```

### View Recent Activity
```bash
cat memory-bundles/outcome-relay.md | tail -20
```

### Pull Latest Changes
```bash
git pull
```

### View Spells
```bash
ls spells/
cat spells/omega-ingest.md
```

## 🔐 Authentication

### Create Personal Access Token
1. Go to: github.com → Settings → Developer settings
2. Create new token with `repo` and `workflow` scopes
3. Use token as password when cloning

### Use Token in Git
```bash
git clone https://github.com/Barrot-Agent/B-Agent.git
# Username: your-github-username
# Password: [paste token here]
```

## 📊 Key URLs

| Resource | URL |
|----------|-----|
| Dashboard | https://barrot-agent.github.io/B-Agent/ |
| Repository | https://github.com/Barrot-Agent/B-Agent |
| Actions | https://github.com/Barrot-Agent/B-Agent/actions |
| Full Guide | [MOBILE_SETUP.md](MOBILE_SETUP.md) |

## 🆘 Troubleshooting

**Can't authenticate?**
- Use Personal Access Token, not password
- Check token has `repo` scope

**Termux won't install packages?**
```bash
termux-change-repo  # Switch to working mirror
pkg update
```

**Want more details?**
- See full guide: [MOBILE_SETUP.md](MOBILE_SETUP.md)

---

💡 **Pro Tip**: Bookmark the dashboard and add GitHub app to your home screen for fastest access!
