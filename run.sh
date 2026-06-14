#!/bin/bash
# vSPACE PWA Launcher using uv run
# Usage: ./run.sh [vote|wallet|nlweb|all]

cd "$(dirname "$0")"

case "${1:-all}" in
    vote)
        echo "Starting F-105 vSpaceVote PWA on port 3000..."
        uv run python apps/vspacevote/app.py
        ;;
    wallet)
        echo "Starting F-106 vSpaceWallet PWA on port 3001..."
        uv run python apps/vspacewallet/app.py
        ;;
    nlweb)
        echo "Starting F-108 NLWeb on port 8501..."
        uv run python infrastructure/foundry-local/app.py
        ;;
    all)
        echo "Starting all PWAs..."
        echo "F-105: http://localhost:3000"
        echo "F-106: http://localhost:3001"
        echo "F-108: http://localhost:8501"
        echo ""
        echo "Starting vSpaceVote..."
        uv run python apps/vspacevote/app.py &
        VOTE_PID=$!
        
        echo "Starting vSpaceWallet..."
        uv run python apps/vspacewallet/app.py &
        WALLET_PID=$!
        
        echo "Starting NLWeb..."
        uv run python infrastructure/foundry-local/app.py &
        NLWEB_PID=$!
        
        echo ""
        echo "All services started!"
        echo "Press Ctrl+C to stop all services"
        
        wait -n $VOTE_PID $WALLET_PID $NLWEB_PID
        ;;
    *)
        echo "Usage: ./run.sh [vote|wallet|nlweb|all]"
        exit 1
        ;;
esac
