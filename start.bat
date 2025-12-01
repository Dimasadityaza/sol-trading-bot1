@echo off
REM Solana Sniper Bot - Complete Launcher for Windows
REM Version 2.0 - Now with Multi-Wallet Group Features!

echo ==========================================
echo SOLANA SNIPER BOT V2.0
echo Multi-Wallet Group System
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo Setting up backend...
cd backend

REM Create .env if not exists
if not exist .env (
    echo Creating .env file...
    (
        echo RPC_ENDPOINT=https://api.devnet.solana.com
        echo WS_ENDPOINT=wss://api.devnet.solana.com
        echo DATABASE_URL=sqlite:///./sniper.db
        echo ENCRYPTION_KEY=change-this-to-your-own-secret-key-minimum-32-characters-long
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
    ) > .env
    echo [OK] .env file created
    echo [WARNING] IMPORTANT: Edit backend\.env and change ENCRYPTION_KEY!
)

REM Install backend dependencies
echo Installing Python dependencies...
pip install -r requirements.txt -q

echo [OK] Backend dependencies installed

REM Run tests
echo.
echo Running tests...
python tests\test_phase1.py > ..\test_output.txt 2>&1
if %errorlevel% equ 0 (
    echo [OK] All tests passed!
) else (
    echo [WARNING] Some tests failed ^(continuing anyway^)
)

cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

REM Install missing package
call npm install tailwindcss-animate

echo [OK] Frontend dependencies installed

cd ..

REM Start backend
echo.
echo Starting backend server...
cd backend
start /B python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 > ..\backend.log 2>&1
cd ..

REM Wait for backend
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo.
echo Starting frontend...
cd frontend
start /B npm run dev > ..\frontend.log 2>&1
cd ..

REM Wait for frontend
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo SOLANA SNIPER BOT V2.0 IS RUNNING!
echo ==========================================
echo.
echo URLs:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://127.0.0.1:8000
echo   API Docs:  http://127.0.0.1:8000/docs
echo.
echo Logs:
echo   Backend:   backend.log
echo   Frontend:  frontend.log
echo.
echo NEW FEATURES ^(V2.0^):
echo   * Auto-generate wallet groups ^(5-1000 wallets^)
echo   * Distribute SOL to all wallets
echo   * Collect SOL from all wallets
echo   * Bulk buy from multiple wallets
echo   * Bulk sell from multiple wallets
echo   * Group management ^(list, view, delete^)
echo.
echo Quick Start:
echo   1. Open http://localhost:5173 ^(Frontend UI^)
echo   2. Or open http://127.0.0.1:8000/docs ^(API^)
echo   3. Try 'wallet-groups' endpoints for new features
echo.
echo Check these new endpoints in API docs:
echo   - POST /group/create - Create wallet group
echo   - POST /group/distribute-sol - Send SOL to all
echo   - POST /group/collect-sol - Collect SOL from all
echo   - POST /group/bulk-buy - Buy from all wallets
echo   - POST /group/bulk-sell - Sell from all wallets
echo.
echo Press any key to stop all servers...
pause >nul

REM Cleanup
echo.
echo Stopping servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" >nul 2>&1

echo All stopped. Goodbye!
timeout /t 2 /nobreak >nul
