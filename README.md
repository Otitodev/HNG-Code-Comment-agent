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
- Push repo to GitHub.
- On Leapcell: import repo, ensure `leapcell.yaml` exists and env vars set.
- Leapcell will run the scheduled `daily_task.py` daily at configured cron.

