# 🚀 Deployment Guide - Solana Trading Bot

This guide will help you get your Solana Trading Bot production-ready and deployed.

## ✅ What's Been Completed

All major features have been implemented and the bot is now **GitHub-ready**:

### 🎯 Core Features Implemented
- ✅ **Multi-wallet group system** - Create and manage up to 100+ wallets per group
- ✅ **Token sniper system** - Automated token sniping with safety filters
- ✅ **Analytics system** - Real-time PnL tracking with CSV/JSON export
- ✅ **Wallet key management** - Auto-save mnemonics to secure files
- ✅ **Jupiter integration** - DEX swaps using Jupiter aggregator
- ✅ **Rate limiting** - API rate limiting (10-100 req/min)
- ✅ **Request logging** - Structured logging with rotation
- ✅ **Error handling** - Global exception handling
- ✅ **Copy trading removed** - As requested

### 📝 Documentation Created
- ✅ `README.md` - Comprehensive project documentation
- ✅ `SECURITY.md` - Security best practices
- ✅ `LICENSE` - MIT License
- ✅ `.env.example` - Environment variable template
- ✅ `.gitignore` - Proper exclusions for sensitive data

### 🔐 Security Implemented
- ✅ AES-256 encryption for private keys
- ✅ Mnemonics auto-saved to `wallet_keys/` (gitignored)
- ✅ Environment-based configuration
- ✅ No hardcoded secrets
- ✅ Secure file structure

## 📦 What's in the Repository

```
sol-trading-bot1/
├── .env.example              # Environment template
├── .gitignore                # Git exclusions
├── LICENSE                   # MIT License
├── README.md                 # Main documentation
├── SECURITY.md               # Security guide
├── DEPLOYMENT_GUIDE.md       # This file
│
├── backend/
│   ├── src/
│   │   ├── core/            # Core functionality
│   │   │   ├── database.py          # SQLite database
│   │   │   ├── wallet.py            # Wallet management
│   │   │   ├── group_manager.py     # Group operations + key export
│   │   │   └── bulk_operations.py   # Bulk trading
│   │   ├── trading/         # Trading logic
│   │   │   ├── jupiter.py           # Jupiter API
│   │   │   ├── executor.py          # Trade execution
│   │   │   └── sniper.py            # Sniper bot
│   │   ├── monitoring/      # Market monitoring
│   │   │   ├── pool_monitor.py      # DEX monitoring
│   │   │   └── token_analyzer.py    # Safety checks
│   │   ├── analytics/       # Analytics + exports
│   │   │   └── tracker.py           # PnL + CSV/JSON export
│   │   ├── api/             # FastAPI server
│   │   │   ├── main.py              # Main server (rate limiting, logging)
│   │   │   └── routes/              # API routes
│   │   └── utils/           # Utilities
│   ├── logs/.gitkeep        # Log directory
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React frontend
│   └── src/
│       ├── pages/           # Dashboard, Wallets, Groups, Trading
│       ├── components/      # UI components
│       └── services/        # API client
│
├── wallet_keys/             # Mnemonic backups (gitignored)
│   └── .gitkeep
│
├── start.sh                 # Linux/Mac launcher
└── start.bat                # Windows launcher
```

## 🚀 Next Steps

### 1. Configure Environment Variables

```bash
# Copy the example file
cp .env.example backend/.env

# Edit with your settings
nano backend/.env
```

**Required settings:**
```bash
# Use a reliable RPC provider (Helius recommended)
RPC_ENDPOINT=https://api.mainnet-beta.solana.com
WS_ENDPOINT=wss://api.mainnet-beta.solana.com

# Generate a strong encryption key (32+ characters)
# Use: openssl rand -hex 32
ENCRYPTION_KEY=your-unique-32-character-minimum-key-here
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Initialize Database

```bash
cd backend
python -c "from src.core.database import init_db; init_db()"
```

### 4. Start the Application

**Option A: Using start scripts**
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

**Option B: Manual start**
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔐 Important Security Steps

### 1. Backup Wallet Keys

When you create wallet groups, mnemonics are automatically saved to:
```
wallet_keys/GroupName_TIMESTAMP.txt
```

**Action Required:**
- Immediately backup these files to a secure location
- Consider printing physical copies for critical wallets
- Store in encrypted USB drives or hardware security modules
- **NEVER** commit these files to Git (already in .gitignore)

### 2. Secure Your Server

If deploying to a server:
```bash
# Enable firewall
sudo ufw enable
sudo ufw allow 8000/tcp  # API port
sudo ufw allow 5173/tcp  # Frontend port (if needed)

# Use HTTPS (recommended: Let's Encrypt)
sudo certbot --nginx
```

### 3. Use Premium RPC Provider

For production, use a reliable RPC provider:

- **Helius** (recommended): https://helius.xyz/
  - 100K free requests/month
  - Best for Solana

- **QuickNode**: https://quicknode.com/
  - Reliable and fast

- **Alchemy**: https://alchemy.com/
  - Enterprise-grade

Update your `.env`:
```bash
RPC_ENDPOINT=https://YOUR-HELIUS-ENDPOINT.solana-mainnet.quiknode.pro/YOUR-API-KEY/
```

## 📊 Using the Bot

### Create a Wallet Group

1. Go to **Groups** page
2. Click **"Create New Group"**
3. Enter:
   - Group name (e.g., "Trading Bots")
   - Number of wallets (1-100)
   - Strong password for encryption
4. Click **"Create"**

**Result:**
- Wallets created in database (encrypted)
- Mnemonics saved to `wallet_keys/GroupName_TIMESTAMP.txt`
- **Backup this file immediately!**

### Fund Wallets

1. Check group details to get wallet addresses
2. Send SOL to each wallet
3. Or use the bulk distribute feature

### Configure Sniper

1. Go to **Trading** page
2. Select wallet group
3. Configure:
   - Buy amount (SOL per token)
   - Min liquidity (e.g., 5 SOL)
   - Safety score (0-100)
   - Tax limits
4. Enable safety checks
5. Start sniper

### View Analytics

1. Go to **Analytics** page
2. View:
   - Real-time PnL
   - Win rate
   - Top tokens
   - Group performance
3. Export:
   - **CSV**: For spreadsheets
   - **JSON**: For custom analysis

## 🧪 Testing

### Test on Devnet First

Update `.env`:
```bash
RPC_ENDPOINT=https://api.devnet.solana.com
WS_ENDPOINT=wss://api.devnet.solana.com
```

### Run Tests

```bash
cd backend
pytest
```

## 🐛 Troubleshooting

### Issue: Module not found errors

```bash
cd backend
pip install -r requirements.txt
```

### Issue: Database locked

Close other applications using the database, or delete and reinitialize:
```bash
rm backend/sniper.db
python -c "from src.core.database import init_db; init_db()"
```

### Issue: RPC connection failed

- Check RPC endpoint in `.env`
- Verify RPC provider is online
- Check firewall/network settings

### Issue: Port already in use

Change port in `backend/.env`:
```bash
API_PORT=8001
```

## 📈 Production Deployment

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9

WORKDIR /app
COPY backend/ /app/

RUN pip install -r requirements.txt

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t solana-trading-bot .
docker run -p 8000:8000 -v $(pwd)/wallet_keys:/app/wallet_keys solana-trading-bot
```

### Using Systemd (Linux)

Create `/etc/systemd/system/solana-bot.service`:
```ini
[Unit]
Description=Solana Trading Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/sol-trading-bot1/backend
Environment="PATH=/path/to/sol-trading-bot1/backend/venv/bin"
ExecStart=/path/to/sol-trading-bot1/backend/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable solana-bot
sudo systemctl start solana-bot
sudo systemctl status solana-bot
```

## 📞 Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check README.md and SECURITY.md
- **API Docs**: http://localhost:8000/docs

## ⚠️ Final Reminders

1. ✅ **NEVER** commit `.env` file
2. ✅ **ALWAYS** backup `wallet_keys/` directory
3. ✅ **START SMALL** - test with small amounts first
4. ✅ **USE DEVNET** - test thoroughly before mainnet
5. ✅ **SECURE YOUR SERVER** - firewall, HTTPS, strong passwords
6. ✅ **MONITOR LOGS** - check `backend/logs/` regularly

## 🎉 You're Ready!

Your Solana Trading Bot is now:
- ✅ Production-ready
- ✅ GitHub-ready
- ✅ Secure
- ✅ Well-documented
- ✅ Fully functional

**Happy trading! 🚀**

---

**Version**: 2.0
**Last Updated**: December 2024
**License**: MIT
