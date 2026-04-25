#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AgenticCoder Backend (FastAPI)...${NC}"
# Start the backend in the background
source venv/bin/activate
uvicorn api.server:app --reload &
BACKEND_PID=$!

echo -e "${GREEN}Starting AgenticCoder Frontend (React/Vite)...${NC}"
# Start the frontend in the background
cd frontend
npm run dev &
FRONTEND_PID=$!

echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}Both services are starting up!${NC}"
echo -e "${GREEN}Backend is running on http://localhost:8000${NC}"
echo -e "${GREEN}Frontend is running on http://localhost:5173${NC}"
echo -e "${GREEN}Open your browser to http://localhost:5173${NC}"
echo -e "${GREEN}==============================================${NC}\n"
echo -e "${GREEN}Press Ctrl+C to stop both services.${NC}"

# Function to handle cleanup on Ctrl+C
cleanup() {
    echo -e "\n${GREEN}Stopping services...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap Ctrl+C (SIGINT) and call cleanup function
trap cleanup SIGINT

# Wait indefinitely so the script doesn't exit immediately
wait
