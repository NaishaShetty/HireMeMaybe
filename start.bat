@echo off
title HireMeMaybe

echo.
echo  =============================================
echo   HireMeMaybe - AI Resume Intelligence
echo  =============================================
echo.

REM ── Backend ──────────────────────────────────
echo  [1/2] Starting backend (FastAPI on :8000)...
start "HireMeMaybe Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

REM ── Frontend ─────────────────────────────────
echo  [2/2] Starting frontend (Vite on :5173)...
cd /d %~dp0frontend

IF NOT EXIST "node_modules\.bin\vite" (
  echo.
  echo  Installing frontend dependencies (first run only)...
  npm install
  echo.
)

start "HireMeMaybe Frontend" cmd /k "npm run dev"

timeout /t 3 /nobreak >nul
echo.
echo  App is starting at:  http://localhost:5173
echo  API running at:      http://localhost:8000
echo.
start http://localhost:5173
