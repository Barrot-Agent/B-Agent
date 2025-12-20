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

---

## Support

For deployment issues:
1. Check the logs
2. Review the documentation
3. Open an issue on GitHub
4. Contact the maintainers

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Netlify Documentation](https://docs.netlify.com)
- [AWS Documentation](https://docs.aws.amazon.com)
- [Docker Documentation](https://docs.docker.com)
