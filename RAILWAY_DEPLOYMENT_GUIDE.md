# 🚀 Railway Deployment Guide for RazorFlow AI

## 📋 **Pre-Deployment Checklist**

### ✅ **Your Project is Railway-Ready!**

- **railway.json**: ✅ Configured with proper build and deploy settings
- **requirements.txt**: ✅ All FastAPI dependencies specified
- **Health Check**: ✅ Endpoint configured at `/health`
- **FastAPI App**: ✅ Production-ready with CORS and proper structure

---

## 🎯 **Deployment Method 1: GitHub Integration (RECOMMENDED)**

### **Step 1: Prepare Your Repository**

```bash
# 1. Ensure your code is committed and pushed to GitHub
cd /home/jc/Documents/RazorFlow-AI-v2
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### **Step 2: Deploy on Railway**

1. **Go to**: https://railway.com/new
2. **Click**: "Deploy from GitHub repo"
3. **Select**: Your `RazorFlow-AI-v2` repository
4. **Click**: "Deploy Now"

### **Step 3: Configure Public Access**

1. **Navigate to**: Your service's Settings tab
2. **Go to**: Networking section
3. **Click**: "Generate Domain"
4. **Result**: Get your public API URL (e.g., `https://your-app.railway.app`)

---

## 🎯 **Deployment Method 2: Railway CLI**

### **Step 1: Install Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or using curl
curl -fsSL https://railway.app/install.sh | sh
```

### **Step 2: Authenticate**

```bash
# Login to Railway
railway login
```

### **Step 3: Deploy**

```bash
# Initialize Railway project
cd /home/jc/Documents/RazorFlow-AI-v2
railway init

# Deploy your app
railway up

# Generate public domain
railway domain
```

---

## 🔧 **Environment Variables Setup**

Once deployed, configure these environment variables in Railway:

### **Required Environment Variables**

```bash
# Database (Railway can provide PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis (Railway can provide Redis)
REDIS_URL=redis://host:port

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for AI assistants)
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS Origins (update with your frontend URL)
ALLOWED_ORIGINS=https://razor303jc.github.io,https://your-custom-domain.com
```

### **Setting Environment Variables**

1. **In Railway Dashboard**: Go to your service → Variables tab
2. **Add each variable**: Click "New Variable" and input key-value pairs
3. **Deploy**: Variables will be available on next deployment

---

## 🗄️ **Database Setup Options**

### **Option A: Use Railway's PostgreSQL**

```bash
# In Railway Dashboard:
# 1. Click "New" → "Database" → "PostgreSQL"
# 2. Railway will provide DATABASE_URL automatically
# 3. Connect your FastAPI service to the database
```

### **Option B: External Database**

```bash
# Use any external PostgreSQL provider
# Set DATABASE_URL in environment variables
```

---

## 📊 **Production Optimizations**

### **1. Update railway.json for Production**

Your current `railway.json` is good, but here are optimizations:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r backend/requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **2. Optimize Backend for Production**

Update your `backend/main.py` to use environment variables:

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Get environment variables
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="RazorFlow AI Backend",
    description="Business Automation Platform with AI Assistants",
    version="2.0.0",
    debug=DEBUG
)

# CORS with environment-based origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    allowed_origins = ["*"]  # Development fallback

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

---

## 🔒 **Security Considerations**

### **1. Environment Variables**

- ✅ **Never commit secrets** to GitHub
- ✅ **Use Railway's environment variables** for sensitive data
- ✅ **Set strong SECRET_KEY** for JWT tokens

### **2. CORS Configuration**

- ✅ **Specific origins** instead of wildcard in production
- ✅ **HTTPS only** for production domains

### **3. Database Security**

- ✅ **Use Railway's private networking** for database connections
- ✅ **Enable SSL** for database connections

---

## 📈 **Monitoring & Scaling**

### **Railway Provides:**

- 📊 **Real-time logs**: Monitor your application
- 📈 **Metrics**: CPU, memory, network usage
- 🔄 **Auto-scaling**: Based on traffic
- 💰 **Usage tracking**: Monitor costs

### **Health Checks**

Your app already has health check configured:

- **Endpoint**: `/health`
- **Timeout**: 100 seconds
- **Auto-restart**: On failure

---

## 🎯 **Quick Start Commands**

### **Deploy Now (GitHub Method)**

```bash
# 1. Push your code
git push origin main

# 2. Go to Railway
open https://railway.com/new

# 3. Select your repo and deploy
```

### **Deploy Now (CLI Method)**

```bash
# 1. Install CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
cd /home/jc/Documents/RazorFlow-AI-v2
railway init
railway up

# 3. Generate domain
railway domain
```

---

## 🆘 **Troubleshooting**

### **Common Issues:**

#### **Build Fails**

```bash
# Check your requirements.txt
# Ensure all dependencies are pinned to specific versions
# Your current setup is already optimized for this
```

#### **App Won't Start**

```bash
# Check PORT environment variable usage
# Ensure startCommand is correct in railway.json
# Your current railway.json looks good
```

#### **Database Connection Issues**

```bash
# Verify DATABASE_URL environment variable
# Check if Railway PostgreSQL service is connected
# Ensure psycopg2-binary is in requirements.txt (✅ already included)
```

---

## 🎉 **Expected Results**

After successful deployment:

1. **API URL**: `https://your-app.railway.app`
2. **Health Check**: `https://your-app.railway.app/health`
3. **Auto-deploy**: On every GitHub push
4. **Monitoring**: Available in Railway dashboard
5. **Logs**: Real-time in Railway console

---

## 🔗 **Next Steps After Deployment**

1. **Update Frontend**: Point your React app to the new Railway URL
2. **Test API**: Verify all endpoints work in production
3. **Setup Monitoring**: Configure alerts and monitoring
4. **Custom Domain**: Add your own domain if needed
5. **SSL**: Railway provides SSL automatically

---

**Your RazorFlow AI backend is ready for Railway deployment! 🚀**
