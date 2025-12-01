#!/bin/bash

# Solana Sniper Bot - Complete Launcher
# Version 2.0 - Now with Multi-Wallet Group Features!

echo "=========================================="
echo "🚀 SOLANA SNIPER BOT V2.0"
echo "   Multi-Wallet Group System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check dependencies
echo -e "${BLUE}📋 Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js found"

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not found. Please install pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip3 found"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} npm found"

echo ""
echo -e "${BLUE}🔧 Setting up backend...${NC}"

cd backend

# Check/create .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} Creating .env file..."
    cat > .env << 'EOF'
RPC_ENDPOINT=https://api.devnet.solana.com
WS_ENDPOINT=wss://api.devnet.solana.com
DATABASE_URL=sqlite:///./sniper.db
ENCRYPTION_KEY=change-this-to-your-own-secret-key-minimum-32-characters-long
API_HOST=0.0.0.0
API_PORT=8000
EOF
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}⚠ IMPORTANT: Edit backend/.env and change ENCRYPTION_KEY!${NC}"
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

pip install -r requirements.txt -q --break-system-packages 2>/dev/null || pip install -r requirements.txt -q

echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Run tests
echo ""
echo -e "${BLUE}🧪 Running tests...${NC}"
python3 tests/test_phase1.py > /tmp/test_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All tests passed!"
else
    echo -e "${YELLOW}⚠${NC} Some tests failed (continuing anyway)"
fi

cd ..

# Setup frontend
echo ""
echo -e "${BLUE}🎨 Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install --silent
fi

# Install missing package
npm install tailwindcss-animate --silent 2>/dev/null

echo -e "${GREEN}✓${NC} Frontend dependencies installed"

cd ..

# Start backend
echo ""
echo -e "${BLUE}🚀 Starting backend server...${NC}"
cd backend
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
echo "   URL: http://127.0.0.1:8000"
echo "   Docs: http://127.0.0.1:8000/docs"
cd ..

# Wait for backend
echo ""
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 3

for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Start frontend
echo ""
echo -e "${BLUE}🎨 Starting frontend...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
echo "   URL: http://localhost:5173"
cd ..

# Wait for frontend
echo ""
echo -e "${BLUE}⏳ Waiting for frontend to be ready...${NC}"
sleep 3

echo ""
echo "=========================================="
echo -e "${GREEN}✅ SOLANA SNIPER BOT V2.0 IS RUNNING!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://127.0.0.1:8000"
echo "   API Docs:  http://127.0.0.1:8000/docs"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:   backend.log"
echo "   Frontend:  frontend.log"
echo ""
echo -e "${BLUE}✨ NEW FEATURES (V2.0):${NC}"
echo "   ✅ Auto-generate wallet groups (5-1000 wallets)"
echo "   ✅ Distribute SOL to all wallets"
echo "   ✅ Collect SOL from all wallets"
echo "   ✅ Bulk buy from multiple wallets"
echo "   ✅ Bulk sell from multiple wallets"
echo "   ✅ Group management (list, view, delete)"
echo ""
echo -e "${BLUE}💡 Quick Start:${NC}"
echo "   1. Open http://localhost:5173 (Frontend UI)"
echo "   2. Or open http://127.0.0.1:8000/docs (API)"
echo "   3. Try 'wallet-groups' endpoints for new features"
echo ""
echo -e "${BLUE}📚 Check these endpoints in API docs:${NC}"
echo "   • POST /group/create - Create wallet group"
echo "   • POST /group/distribute-sol - Send SOL to all"
echo "   • POST /group/collect-sol - Collect SOL from all"
echo "   • POST /group/bulk-buy - Buy from all wallets"
echo "   • POST /group/bulk-sell - Sell from all wallets"
echo ""
echo -e "${YELLOW}🛑 To stop: Press Ctrl+C${NC}"
echo ""

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Cleanup function
trap cleanup INT

cleanup() {
    echo ""
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓${NC} Backend stopped"
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓${NC} Frontend stopped"
        rm .frontend.pid
    fi
    
    pkill -f "uvicorn src.api.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    
    echo ""
    echo -e "${GREEN}✅ All stopped. Goodbye!${NC}"
    echo ""
    exit 0
}

# Keep running
while true; do
    sleep 1
done
