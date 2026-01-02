# 🚀 B-Agent Deployment Guide

This guide covers deployment options for B-Agent across multiple cloud platforms.

## 📋 Table of Contents

- [Overview](#overview)
- [Deployment Platforms](#deployment-platforms)
  - [Vercel (Current - GitHub Pages)](#vercel-current---github-pages)
  - [Heroku](#heroku)
  - [Render](#render)
  - [Railway](#railway)
  - [Fly.io](#flyio)
  - [Docker (Self-hosted)](#docker-self-hosted)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)

---

## Overview

B-Agent can be deployed to various cloud platforms. The repository includes configuration files for multiple platforms to provide flexibility in deployment choices.

**Current Deployment**: GitHub Pages (via Vercel)
- **URL**: https://barrot-agent.github.io/B-Agent/
- **Status**: ✅ Active

---

## Deployment Platforms

### Vercel (Current - GitHub Pages)

**Status**: ✅ Currently Deployed

The dashboard is currently deployed via GitHub Pages and can also be deployed directly to Vercel.

**Files**:
- `vercel.json` - Vercel configuration
- `site/index.html` - Static dashboard

**Deployment**:
1. The GitHub Actions workflow automatically deploys to GitHub Pages
2. Alternatively, connect your GitHub repo to Vercel
3. Vercel will auto-detect the configuration

**URL**: https://barrot-agent.github.io/B-Agent/

---

### Heroku

**Status**: ⚙️ Ready to Deploy

Deploy Barrot-Agent to Heroku with a single click or via CLI.

**Files**:
- `Procfile` - Heroku process configuration
- `app.json` - Heroku app configuration
- `runtime.txt` - Python version specification

**Quick Deploy**:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Barrot-Agent/B-Agent)

**Manual Deployment**:
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create a new Heroku app
heroku create barrot-agent-app

# Deploy
git push heroku main

# Open the app
heroku open
```

**Configuration**:
- Buildpack: Python
- Process: `web` serving static files on port $PORT
- Pricing: Basic tier ($5-7/month) - Note: Heroku discontinued free tier in November 2022

---

### Render

**Status**: ⚙️ Ready to Deploy

Deploy as a static site on Render with automatic builds.

**Files**:
- `render.yaml` - Render Blueprint configuration

**Deployment**:
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply" to deploy

**Features**:
- Automatic HTTPS
- Custom headers for security
- Static site optimization
- Free tier available

**Manual Deployment**:
```bash
# Via Render Dashboard
1. New → Static Site
2. Connect repository
3. Set:
   - Build Command: (leave empty)
   - Publish Directory: ./site
4. Create Static Site
```

---

### Railway

**Status**: ⚙️ Ready to Deploy

Deploy using Docker on Railway with automatic deployments.

**Files**:
- `railway.toml` - Railway configuration
- `Dockerfile` - Container definition

**Deployment**:
1. Go to [Railway](https://railway.app/)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select Barrot-Agent repository
5. Railway will auto-detect configuration
6. Deploy

**Features**:
- Docker-based deployment
- Auto-scaling
- Custom domains
- Free $5 monthly credit

**Manual Deployment**:
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

---

### Fly.io

**Status**: ⚙️ Ready to Deploy

Deploy as a lightweight container on Fly.io's global network.

**Files**:
- `fly.toml` - Fly.io configuration
- `Dockerfile` - Container definition

**Deployment**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Authenticate
fly auth login

# Launch app (first time)
fly launch

# Deploy
fly deploy

# Open app
fly open
```

**Features**:
- Global edge network
- Automatic HTTPS
- Auto-scaling
- Free tier: 3 shared-cpu VMs with 256MB RAM

**Configuration**:
- Region: `iad` (Washington D.C.) - change in `fly.toml`
- Memory: 256MB
- Auto-stop when idle
- Health checks enabled

---

### Docker (Self-hosted)

**Status**: ✅ Available

Run Barrot-Agent in a Docker container on any platform.

**Files**:
- `Dockerfile` - Container definition

**Build and Run**:
```bash
# Build the image
docker build -t barrot-agent .

# Run the container
docker run -d \
  --name barrot-agent \
  -p 8080:8080 \
  -e BARROT_ENV=docker \
  barrot-agent

# Access at http://localhost:8080
```

**Docker Compose** (optional):
```yaml
version: '3.8'
services:
  barrot-agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - BARROT_ENV=docker
    restart: unless-stopped
```

**Deployment Options**:
- Local development
- VPS (DigitalOcean, Linode, etc.)
- Kubernetes clusters
- Any Docker-compatible platform

---

## Configuration Files

| File | Platform | Purpose |
|------|----------|---------|
| `vercel.json` | Vercel | Static site configuration |
| `Procfile` | Heroku | Process type definition |
| `app.json` | Heroku | App metadata and configuration |
| `runtime.txt` | Heroku | Python version specification |
| `render.yaml` | Render | Blueprint configuration |
| `railway.toml` | Railway | Project configuration |
| `fly.toml` | Fly.io | App and deployment settings |
| `Dockerfile` | Docker/Railway/Fly.io | Container definition |

---

## Environment Variables

### Common Variables

- `BARROT_ENV`: Deployment environment identifier
  - Values: `heroku`, `render`, `railway`, `flyio`, `docker`, `vercel`
  - Used for environment-specific configuration

### Platform-Specific

**Heroku**:
- `PORT`: Automatically set by Heroku (required for web process)

**Fly.io**:
- Internal port: `8080` (configured in `fly.toml`)

**Railway**:
- Automatically handles port assignment

**Render**:
- Static site - no dynamic env vars needed

---

## Choosing a Platform

### Use Vercel/GitHub Pages when:
- ✅ Serving static content only
- ✅ Need GitHub integration
- ✅ Want automatic deployments from GitHub
- ✅ Free tier is sufficient

### Use Heroku when:
- ✅ Need simple, straightforward deployment
- ✅ Want one-click deployment
- ✅ Familiar with Heroku ecosystem
- ⚠️ Note: No longer offers free tier - paid plans start at $5-7/month (Basic tier)

### Use Render when:
- ✅ Want modern alternative to Heroku
- ✅ Need static site with custom headers
- ✅ Want automatic HTTPS and CDN
- ✅ Free tier available

### Use Railway when:
- ✅ Need Docker-based deployment
- ✅ Want modern developer experience
- ✅ Need easy database integration
- ✅ Free $5 monthly credit

### Use Fly.io when:
- ✅ Need global edge deployment
- ✅ Want low-latency worldwide
- ✅ Need auto-scaling capabilities
- ✅ Free tier available (3 VMs)

### Use Docker when:
- ✅ Self-hosting on VPS/cloud
- ✅ Need full control
- ✅ Running in Kubernetes
- ✅ Custom infrastructure

---

## Support

For deployment issues:
1. Check platform-specific logs
2. Review configuration files
3. Consult platform documentation
4. Open an issue: https://github.com/Barrot-Agent/B-Agent/issues

---

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: 2025-12-28  
**Status**: All platforms ready for deployment ✅

🦜 **Barrot-Agent** - Deploy anywhere, run everywhere! ✨
