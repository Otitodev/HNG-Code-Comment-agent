# Code Commenter Agent (FastAPI + Mistral + Postgres)

## Overview
Small FastAPI service that:
- Comments code snippets via Mistral AI
- Provides a daily "developer tip" cached in Postgres
- Posts the daily tip to Telex using a scheduled job (Leapcell cron)

## Setup (local)
1. Copy `.env.example` -> `.env` and fill values.
2. Create DB and ensure DATABASE_URL points correctly.
3. Install deps:
   pip install -r requirements.txt
4. Run:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

## Endpoints
- POST /api/comment  { "code": "<code snippet>" }
- GET  /api/daily-tip

## Deploy

### Deploy to AWS Lambda (AWS SAM)
- Prerequisites:
  - AWS account and AWS CLI configured with credentials and default region (aws configure).
  - AWS SAM CLI installed.
  - Docker installed and running (required for sam build --use-container to build Linux-compatible wheels for native deps like asyncpg or psycopg2-binary). On Windows, use Docker Desktop with WSL 2.
- Build:
  - sam build --use-container
- First deploy (guided):
  - sam deploy --guided
    - Choose a stack name and region.
    - Save arguments to samconfig.toml when prompted.
    - Provide parameter values when prompted:
      - MistralApiKey
      - TelexAgentApiKey
      - DatabaseUrl
      - ApiBaseUrl
- Subsequent deploys:
  - sam deploy
- Post-deploy testing:
  - Find the ApiEndpoint output in the stack.
  - GET / should return {"message":"Code Commenter Agent (Async) is running"}.
  - POST /api/comment with JSON {"code":"print('hi')"} should return a valid response.
- Notes:
  - If your database is private (e.g., RDS in a VPC), attach the function to that VPC (SubnetIds, SecurityGroupIds) in the SAM template; not configured by default.
  - Cold starts and external calls (DB, AI) may require increasing Timeout above 30s in Globals.Function.Timeout.
  - Only the FastAPI service is deployed here. A future enhancement could add daily_task.py as a scheduled Lambda via an EventBridge rule.
  - The existing Dockerfile remains unchanged for local container runs.

### Deploy to Leapcell (Alternative)
- Push repo to GitHub.
- On Leapcell: import repo, ensure `leapcell.yaml` exists and env vars set.
- Leapcell will run the scheduled `daily_task.py` daily at configured cron.

