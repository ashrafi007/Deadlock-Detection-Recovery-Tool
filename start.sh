#!/bin/bash
# Start backend and frontend
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting FastAPI backend on http://localhost:8000 ..."
python3 -m uvicorn backend.api:app --port 8000 --reload &
BACKEND_PID=$!

echo "Starting React frontend on http://localhost:5173 ..."
cd "$ROOT/frontend" && npm run dev -- --port 5173 &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" INT TERM
wait
