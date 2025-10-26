# 🚀 Deployment Guide - Code Commenter Agent

## Prerequisites
- Leapcell account
- GitHub repository with the code
- Mistral AI API key
- PostgreSQL database (Leapcell provides managed databases)

## Step 1: Prepare Repository
1. Push your code to GitHub repository
2. Ensure all files are committed including:
   - `leapcell.yaml`
   - `requirements.txt`
   - `Dockerfile`
   - All app files

## Step 2: Deploy on Leapcell

### Option A: Deploy from GitHub
1. Login to Leapcell dashboard
2. Click "New Project" → "Import from GitHub"
3. Select your repository
4. Leapcell will auto-detect the `leapcell.yaml` configuration

### Option B: Deploy from Git URL
1. Use the Git URL of your repository
2. Leapcell will clone and build automatically

## Step 3: Configure Environment Variables
In Leapcell dashboard, set these environment variables:

```bash
MISTRAL_API_KEY=Ixvv5x5tjOY9jdO0QuolKeD0OGjSbbui
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname?sslmode=require
API_BASE_URL=https://your-app-name.leapcell.app
TELEX_AGENT_API_KEY=your_telex_key_here  # Optional
TELEX_CHANNEL=your_channel_id            # Optional
APP_ENV=production
```

## Step 4: Database Setup
- Leapcell provides managed PostgreSQL
- Or use your existing PostgreSQL database
- The app will auto-create tables on first startup

## Step 5: Configure Scheduled Jobs
The `leapcell.yaml` includes a daily cron job:
- Runs at 08:00 UTC daily
- Posts tips to Telex (if configured)
- Check Leapcell logs to verify execution

## Step 6: Test Deployment
Once deployed, test these endpoints:
- `GET /` - Health check
- `GET /docs` - API documentation
- `GET /api/daily-tip` - Daily developer tip
- `POST /api/comment` - Code commenting

## API Usage Examples

### Get Daily Tip
```bash
curl https://your-app.leapcell.app/api/daily-tip
```

### Comment Code
```bash
curl -X POST https://your-app.leapcell.app/api/comment \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello world\")"}'
```

## Monitoring
- Check Leapcell logs for application health
- Monitor scheduled job execution
- Set up alerts for failures

## Scaling
- Leapcell auto-scales based on traffic
- Monitor resource usage in dashboard
- Adjust instance size if needed

## Troubleshooting
- Check logs in Leapcell dashboard
- Verify environment variables are set
- Ensure database connectivity
- Test API endpoints individually