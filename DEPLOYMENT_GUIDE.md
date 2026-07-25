# Render Deployment Guide for FinTrack

## ✅ Step 1: Code Pushed (DONE)
Your latest changes have been successfully pushed to GitHub:
- 🔧 Fixed login/register internal errors
- 🗑️ Cleaned up unused files
- ✅ All tests passing

## 📋 Step 2: Deploy to Render (Follow Below)

### Option A: Using Render Dashboard (Recommended for First-time Setup)

1. **Go to Render.com**
   - Visit https://dashboard.render.com
   - Sign in with your GitHub account

2. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `personal-finance-db`
   - Plan: Free (or paid if needed)
   - Copy the Database URL (you'll need this)
   - Click "Create Database"

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `jaganath-biradar/FinTrack`
   - Branch: `main`
   - Name: `personal-finance-web`
   - Environment: `Python 3.12`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `alembic upgrade head && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**
   - Click "Environment" tab
   - Add these variables:
     ```
     DATABASE_URL = [paste your PostgreSQL URL here]
     SECRET_KEY = [generate a secure secret key]
     ACCESS_TOKEN_EXPIRE_MINUTES = 60
     ```
   
   To generate SECRET_KEY, run this in terminal:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically start building and deploying
   - Wait for status to show "Live" (usually 3-5 minutes)

### Option B: Using Render CLI (Advanced)

1. Install Render CLI:
   ```bash
   npm install -g @render-oss/render-cli
   ```

2. Authenticate with Render:
   ```bash
   render login
   ```

3. Deploy using render.yaml:
   ```bash
   render deploy --service-region oregon
   ```

## ⚠️ Important Notes

- **Database Migration**: The start command includes `alembic upgrade head` which will automatically run migrations on deploy
- **First Deploy**: Takes 3-10 minutes as dependencies are installed
- **Auto-redeploy**: Every git push to `main` will trigger a new build
- **Free Tier**: May spin down after 15 minutes of inactivity (takes 30 seconds to wake up)

## 🔍 After Deployment

1. Check your deployed app at: `https://your-service-name.onrender.com`
2. Monitor logs: Render Dashboard → Your Service → Logs tab
3. Test endpoints:
   - Login: `https://your-service-name.onrender.com/login`
   - Register: `https://your-service-name.onrender.com/register`

## 🆘 Troubleshooting

If you encounter issues:
1. Check logs in Render Dashboard
2. Verify DATABASE_URL is correct
3. Ensure SECRET_KEY is set
4. Verify python version (should be 3.12+)

---

Need help? Let me know if you have any questions!
