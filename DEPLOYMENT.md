<<<<<<< HEAD
# 🚀 Barrot-Agent Deployment Guide

This guide covers deployment options for Barrot-Agent across multiple cloud platforms.

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

Barrot-Agent can be deployed to various cloud platforms. The repository includes configuration files for multiple platforms to provide flexibility in deployment choices.

**Current Deployment**: GitHub Pages (via Vercel)
- **URL**: https://barrot-agent.github.io/Barrot-Agent/
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

**URL**: https://barrot-agent.github.io/Barrot-Agent/

---

### Heroku

**Status**: ⚙️ Ready to Deploy

Deploy Barrot-Agent to Heroku with a single click or via CLI.

**Files**:
- `Procfile` - Heroku process configuration
- `app.json` - Heroku app configuration
- `runtime.txt` - Python version specification

**Quick Deploy**:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Barrot-Agent/Barrot-Agent)

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
=======
# Deployment Guide for Barrot

This guide walks you through deploying the Barrot website to various platforms.

## Table of Contents
1. [Vercel Deployment (Recommended)](#vercel-deployment)
2. [GitHub Pages](#github-pages)
3. [Netlify](#netlify)
4. [AWS](#aws)
5. [Docker](#docker)

---

## Vercel Deployment

Vercel is the recommended platform for deploying Barrot due to its seamless integration with Node.js and static sites.

### Prerequisites
- Vercel account (free tier available)
- Git repository

### Steps

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd Barrot-Agent
   vercel --prod
   ```

4. **Configure Environment Variables**
   In your Vercel dashboard:
   - Go to Settings → Environment Variables
   - Add the following variables:
     ```
     NODE_ENV=production
     PORT=3000
     ```

### Automatic Deployments

The repository includes a GitHub Actions workflow that automatically deploys to Vercel on push to the main branch.

To enable this:
1. Go to your GitHub repository → Settings → Secrets
2. Add the following secrets:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `VERCEL_ORG_ID`: Your organization ID from Vercel
   - `VERCEL_PROJECT_ID`: Your project ID from Vercel

---

## GitHub Pages

GitHub Pages is ideal for static sites. Note that the backend API won't work with GitHub Pages alone.

### Prerequisites
- GitHub repository
- GitHub account

### Steps

1. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: Select `main` or `master`
   - Folder: `/website`

2. **Manual Deployment**
   The GitHub Actions workflow will automatically deploy the website folder to GitHub Pages.

3. **Access Your Site**
   Your site will be available at:
   ```
   https://[username].github.io/[repository-name]/
   ```

### Limitations
- Backend API won't work
- Only static files are served
- Need external backend service for full functionality

---

## Netlify

Netlify provides easy deployment with built-in CI/CD.

### Prerequisites
- Netlify account
- Git repository

### Steps

1. **Manual Deployment**
   ```bash
   npm install -g netlify-cli
   netlify login
   netlify deploy --prod
   ```

2. **Automatic Deployment**
   - Connect your GitHub repository to Netlify
   - Build command: `npm install`
   - Publish directory: `website`

3. **Configure Build Settings**
   Create `netlify.toml`:
   ```toml
   [build]
     command = "npm install"
     publish = "website"
   
   [[redirects]]
     from = "/api/*"
     to = "/.netlify/functions/:splat"
     status = 200
   ```

### Serverless Functions

For backend API with Netlify:
1. Create `netlify/functions` directory
2. Convert backend endpoints to serverless functions
3. Deploy with Netlify

---

## AWS

Deploy to AWS using various services.

### Option 1: AWS Elastic Beanstalk

1. **Install AWS CLI and EB CLI**
   ```bash
   pip install awscli awsebcli
   ```

2. **Initialize EB**
   ```bash
   eb init -p node.js-18 barrot-app
   ```

3. **Create Environment and Deploy**
   ```bash
   eb create barrot-production
   eb deploy
   ```

### Option 2: AWS EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t2.micro (free tier)
   - Configure security groups (ports 80, 443, 22)

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install nodejs npm nginx
   ```

4. **Clone and Setup**
   ```bash
   git clone https://github.com/Barrot-Agent/Barrot-Agent.git
   cd Barrot-Agent
   npm install
   ```

5. **Use PM2 for Process Management**
   ```bash
   npm install -g pm2
   pm2 start backend/server.js --name barrot
   pm2 startup
   pm2 save
   ```

6. **Configure Nginx**
   Create `/etc/nginx/sites-available/barrot`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

7. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/barrot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 3: AWS Amplify

1. Connect GitHub repository to AWS Amplify
2. Configure build settings
3. Deploy automatically on push

---

## Docker

Deploy using Docker containers.

### Prerequisites
- Docker installed
- Docker Hub account (optional)

### Steps

1. **Build Image**
   ```bash
   docker build -t barrot-agent .
   ```

2. **Run Container**
   ```bash
   docker run -d -p 3000:3000 --name barrot barrot-agent
   ```

3. **Docker Compose** (recommended)
   Create `docker-compose.yml`:
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "3000:3000"
       environment:
         - NODE_ENV=production
       volumes:
         - ./backend/db:/app/backend/db
       restart: unless-stopped
   ```

   Run:
   ```bash
   docker-compose up -d
   ```

4. **Push to Docker Hub** (optional)
   ```bash
   docker tag barrot-agent your-username/barrot-agent
   docker push your-username/barrot-agent
   ```

---

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Test all features (streaming, recording, 3D rendering, chat)
- [ ] Verify API endpoints are accessible
- [ ] Check database connectivity
- [ ] Test on multiple devices (desktop, tablet, mobile)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Configure SSL/HTTPS
- [ ] Set up monitoring and error tracking
- [ ] Configure backups for database
- [ ] Review security settings
- [ ] Set up custom domain (optional)

---

## Troubleshooting

### Common Issues

**Issue: API requests failing**
- Check CORS settings
- Verify API base URL in frontend
- Check network/firewall rules

**Issue: Database not persisting**
- Ensure database directory is writable
- Check volume mounts in Docker
- Verify database path in configuration

**Issue: WebRTC not working**
- Requires HTTPS in production
- Check browser permissions
- Verify STUN/TURN server configuration

**Issue: 3D rendering not working**
- Ensure Three.js is loaded
- Check browser WebGL support
- Verify canvas element exists
>>>>>>> origin/copilot/add-barrot-website-functionality

---

## Support

For deployment issues:
<<<<<<< HEAD
1. Check platform-specific logs
2. Review configuration files
3. Consult platform documentation
4. Open an issue: https://github.com/Barrot-Agent/Barrot-Agent/issues

---
=======
1. Check the logs
2. Review the documentation
3. Open an issue on GitHub
4. Contact the maintainers
>>>>>>> origin/copilot/add-barrot-website-functionality

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
<<<<<<< HEAD
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: 2025-12-28  
**Status**: All platforms ready for deployment ✅

🦜 **Barrot-Agent** - Deploy anywhere, run everywhere! ✨
=======
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Netlify Documentation](https://docs.netlify.com)
- [AWS Documentation](https://docs.aws.amazon.com)
- [Docker Documentation](https://docs.docker.com)
>>>>>>> origin/copilot/add-barrot-website-functionality
