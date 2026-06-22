#!/bin/bash
echo "============================================================"
echo " Stock Query Server — DSA-CH23-GROUP (Theme C)"
echo "============================================================"

echo "[1/2] Starting Flask backend on http://localhost:5000"
cd backend && python api/server.py &
BACKEND_PID=$!

echo "[2/2] Starting React frontend on http://localhost:3000"
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Servers running."
echo "  Backend  : http://localhost:5000"
echo "  Frontend : http://localhost:3000"
echo "  Health   : http://localhost:5000/api/health"
echo ""
echo "Press Ctrl+C to stop both servers."
wait $BACKEND_PID $FRONTEND_PID
