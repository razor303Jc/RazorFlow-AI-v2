# RazorFlow AI - Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Node.js 18+ and Python 3.11+

### 1. Frontend Deployment (GitHub Pages)

```bash
# Clone and setup
git clone https://github.com/razor303jc/RazorFlow-AI-v2.git
cd RazorFlow-AI-v2/frontend

# Install dependencies
npm install

# Build and deploy
npm run build
npm run deploy
```

**Live URL**: `https://razor303jc.github.io/RazorFlow-AI-v2/`

### 2. Backend Deployment (Railway)

1. **Create Railway Project**:
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository
   - Select this repository

2. **Configure Environment**:
   ```env
   PORT=8000
   RAILWAY_ENVIRONMENT=production
   ```

3. **Auto-Deploy**:
   - Railway detects `railway.json`
   - Automatic builds on git push
   - Health checks at `/health`

**Live API**: `https://razorflow-ai-production.up.railway.app`

## 📊 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│  GitHub Pages   │────│   Railway API   │
│   (Frontend)    │    │   (Backend)     │
│                 │    │                 │
│ • React/Vite    │    │ • FastAPI       │
│ • Tailwind CSS  │    │ • PostgreSQL    │
│ • Static Assets │    │ • Redis Cache   │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Local Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Opens http://localhost:5173
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

## 🔧 Configuration

### Frontend Environment
- **API_BASE**: Backend URL (auto-configured)
- **BASE_PATH**: `/RazorFlow-AI-v2/` for GitHub Pages

### Backend Environment
- **PORT**: Server port (Railway sets automatically)
- **DATABASE_URL**: PostgreSQL connection (Railway provides)
- **REDIS_URL**: Redis cache (optional)

## 📈 Scaling & Performance

### Frontend Optimization
- Vite build optimization
- GitHub Pages CDN
- Lazy loading components
- Image optimization

### Backend Optimization
- FastAPI async operations
- Database connection pooling
- Redis caching layer
- Railway auto-scaling

## 🔒 Security

### Frontend Security
- HTTPS by default (GitHub Pages)
- CSP headers
- XSS protection
- Secure API communication

### Backend Security
- CORS configuration
- Input validation
- Rate limiting
- Environment variable protection

## 📱 Monitoring

### Health Checks
- Frontend: Deployment status
- Backend: `/health` endpoint
- Database: Connection monitoring

### Analytics
- GitHub Pages built-in analytics
- Railway metrics dashboard
- Custom business metrics

## 💰 Cost Analysis

### GitHub Pages
- **Cost**: Free
- **Bandwidth**: 100GB/month
- **Storage**: 1GB
- **Custom domain**: Supported

### Railway
- **Free Tier**: 
  - $5 credit/month
  - 512MB RAM
  - 1GB storage
- **Pro Plan**: $20/month
  - 8GB RAM
  - 100GB storage
  - Custom domains

### Total Monthly Cost
- **Development**: $0 (free tiers)
- **Production**: $20-50/month
- **Enterprise**: $100+ (custom scaling)

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Update API endpoints in frontend
- [ ] Test all bot functionalities
- [ ] Verify CORS configuration
- [ ] Check responsive design

### Deployment
- [ ] Push to GitHub (triggers frontend deploy)
- [ ] Deploy backend to Railway
- [ ] Verify health checks
- [ ] Test API connectivity

### Post-Deployment
- [ ] Monitor performance
- [ ] Check error logs
- [ ] Test user workflows
- [ ] Update documentation

## 🔄 CI/CD Pipeline

### Automatic Deployment
1. **Git Push** → Triggers workflows
2. **Frontend Build** → Deploy to GitHub Pages
3. **Backend Test** → Deploy to Railway
4. **Health Check** → Verify deployment
5. **Notification** → Success/failure alerts

### Manual Deployment
```bash
# Frontend only
cd frontend && npm run deploy

# Backend only
git push origin main  # Railway auto-deploys
```

---

## 🎯 Next Steps

1. **Custom Domain**: Configure custom domain for branding
2. **Database Setup**: Add PostgreSQL for persistent data
3. **Authentication**: Implement user authentication
4. **Analytics**: Add business metrics tracking
5. **Monitoring**: Set up uptime monitoring

**Ready to launch your AI business platform> .github/workflows/deploy.yml << 'EOF'
name: Deploy RazorFlow AI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Build
      run: |
        cd frontend
        npm run build
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./frontend/dist
        
  test-backend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        
    - name: Test backend
      run: |
        cd backend
        python -m pytest --version || echo "No tests yet"
        python -c "import main; print('Backend imports successfully')"
EOF* 🚀
