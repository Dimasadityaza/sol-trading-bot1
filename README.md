# 🎯 SOLANA SNIPER BOT V2.0

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Version](https://img.shields.io/badge/Version-2.0-blue)
![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing-success)

**Professional Solana trading bot dengan Multi-Wallet Group System**

---

## 🆕 WHAT'S NEW IN V2.0

### Multi-Wallet Group Features:
- ✅ **Auto-generate 5-1000 wallets** dalam satu group
- ✅ **Distribute SOL** dari 1 wallet ke semua wallet di group
- ✅ **Collect SOL** dari semua wallet ke 1 wallet  
- ✅ **Bulk Buy** - Buy token dari banyak wallet sekaligus
- ✅ **Bulk Sell** - Sell token dari banyak wallet sekaligus
- ✅ **Group Management** - List, view, delete groups
- ✅ **11 New API Endpoints** untuk group operations

---

## 🚀 QUICK START

### One-Click Launch:

**Linux / macOS:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

**Access:**
- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`

---

## ✨ COMPLETE FEATURE LIST

### V1.0 Features (Original):
- ✅ Wallet Management (create, import, multi-wallet)
- ✅ Manual Trading (buy/sell via Jupiter)
- ✅ Token Safety Analysis
- ✅ Auto-Sniping
- ✅ Analytics & PnL Tracking
- ✅ Telegram Notifications
- ✅ Professional UI

### V2.0 Features (NEW!):
- ✅ **Wallet Groups** - Create 5-1000 wallets at once
- ✅ **Auto-Naming** - "Group 1 - Wallet 1", "Group 1 - Wallet 2", etc
- ✅ **Distribute SOL** - Send SOL to all wallets in group
- ✅ **Collect SOL** - Gather SOL from all wallets
- ✅ **Bulk Buy** - All wallets buy token simultaneously
- ✅ **Bulk Sell** - All wallets sell token simultaneously
- ✅ **Group Balances** - See total SOL across all wallets
- ✅ **Group Configuration** - Configure slippage per operation
- ✅ **Private Key Access** - Access keys by group + index

---

## 📚 NEW API ENDPOINTS (V2.0)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/group/create` | POST | Create wallet group (5-1000 wallets) |
| `/group/list` | GET | List all groups |
| `/group/{id}` | GET | Get group details |
| `/group/{id}/wallets` | GET | Get group wallets |
| `/group/{id}/balances` | GET | Get group balances |
| `/group/{id}` | DELETE | Delete group |
| `/group/distribute-sol` | POST | Distribute SOL to all wallets |
| `/group/collect-sol` | POST | Collect SOL from all wallets |
| `/group/bulk-buy` | POST | Bulk buy token |
| `/group/bulk-sell` | POST | Bulk sell token |

**Total Endpoints**: 38 (27 original + 11 new)

---

## 💡 USE CASES

### 1. Volume Trading
```bash
# Create 50 wallets
POST /group/create {"name": "Volume Bots", "count": 50}

# Distribute 0.05 SOL each
POST /group/distribute-sol {...}

# Bulk buy token
POST /group/bulk-buy {"sol_amount": 0.05, ...}
```

### 2. Token Sniping
```bash
# Create 20 sniper wallets
POST /group/create {"name": "Snipers", "count": 20}

# Fund them
POST /group/distribute-sol {...}

# Snipe new token
POST /group/bulk-buy {"token_address": "NEW_TOKEN", ...}
```

### 3. Take Profit
```bash
# Sell from all wallets
POST /group/bulk-sell {"percentage": 100, ...}

# Collect profit
POST /group/collect-sol {...}
```

---

## 📦 WHAT'S INCLUDED

```
solana-sniper-bot/
├── start.sh                    ✅ One-click launcher (Linux/Mac)
├── start.bat                   ✅ One-click launcher (Windows)
├── README.md                   ✅ This file
├── README-MULTI-WALLET.md      ✅ Complete V2.0 guide
│
├── backend/                    ✅ Python FastAPI Backend
│   ├── src/
│   │   ├── core/
│   │   │   ├── database.py              # Database models
│   │   │   ├── wallet.py                # Wallet operations
│   │   │   ├── group_manager.py         # NEW! Group management
│   │   │   └── bulk_operations.py       # NEW! Bulk operations
│   │   ├── trading/
│   │   │   ├── jupiter.py               # Jupiter integration
│   │   │   ├── executor.py              # Trade executor
│   │   │   └── sniper.py                # Auto-sniper
│   │   ├── monitoring/
│   │   │   ├── pool_monitor.py          # Pool monitoring
│   │   │   └── token_analyzer.py        # Safety analyzer
│   │   ├── analytics/
│   │   │   └── tracker.py               # PnL tracker
│   │   ├── utils/
│   │   │   ├── encryption.py            # AES-256 encryption
│   │   │   └── telegram.py              # Telegram bot
│   │   └── api/
│   │       ├── main.py                  # Main API
│   │       └── routes/
│   │           ├── trading.py           # Trading routes
│   │           ├── sniper.py            # Sniper routes
│   │           ├── analytics.py         # Analytics routes
│   │           └── groups.py            # NEW! Group routes
│   └── tests/                  ✅ 19/19 tests passing
│
├── frontend/                   ✅ React TypeScript Frontend
│   └── src/
│       ├── components/         # UI Components
│       ├── pages/              # Pages
│       └── services/           # API client
│
└── desktop/                    ✅ Electron Desktop App
    ├── main.js
    └── package.json
```

---

## 🎯 GETTING STARTED

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- pip & npm

### 2. Start Bot
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### 3. Create First Group
Open `http://127.0.0.1:8000/docs`

Find: **POST /group/create**

Try:
```json
{
  "name": "My First Group",
  "count": 10,
  "password": "secure123"
}
```

### 4. Fund Wallets
Use **POST /group/distribute-sol** to send SOL to all wallets

### 5. Start Trading!
Use **POST /group/bulk-buy** or **POST /group/bulk-sell**

---

## 📖 DOCUMENTATION

- **README-MULTI-WALLET.md** - Complete V2.0 guide
- **API Docs** - http://127.0.0.1:8000/docs
- **QUICKSTART.md** - Quick start guide
- **PROJECT_COMPLETE.md** - Full project summary

---

## 🔧 CONFIGURATION

### backend/.env
```bash
RPC_ENDPOINT=https://api.devnet.solana.com
WS_ENDPOINT=wss://api.devnet.solana.com
DATABASE_URL=sqlite:///./sniper.db
ENCRYPTION_KEY=change-this-32-char-min  # CHANGE THIS!
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📊 PROJECT STATISTICS

| Metric | Value |
|--------|-------|
| Total Files | 79+ |
| Lines of Code | 7,000+ |
| API Endpoints | 38 |
| Database Tables | 4 |
| UI Components | 30+ |
| Tests | 19/19 passing ✅ |

---

## 🧪 TESTING

### All Core Tests Pass:
```bash
cd backend
python tests/test_phase1.py
# Result: 7/7 tests passed ✅

python tests/test_integration.py  
# Result: 12/12 tests passed ✅
```

---

## ⚠️ IMPORTANT NOTES

### First Time Setup:
1. **WAJIB** edit `backend/.env` dan ganti `ENCRYPTION_KEY`
2. Test di **devnet** dulu
3. Save semua **mnemonic phrases**!

### Database Migration:
Jika upgrade dari V1.0, **hapus database lama**:
```bash
cd backend
rm sniper.db
```

### Security:
- Use strong passwords (12+ characters)
- Never share private keys
- Backup mnemonic phrases offline
- Test with small amounts first

---

## 🎓 EXAMPLES

### Create 20 Trading Wallets:
```bash
curl -X POST http://127.0.0.1:8000/group/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Trading Group",
    "count": 20,
    "password": "secure123"
  }'
```

### Distribute 0.1 SOL to Each:
```bash
curl -X POST http://127.0.0.1:8000/group/distribute-sol \
  -H "Content-Type: application/json" \
  -d '{
    "from_wallet_id": 1,
    "to_group_id": 1,
    "amount_per_wallet": 0.1,
    "password": "secure123"
  }'
```

### Bulk Buy Token:
```bash
curl -X POST http://127.0.0.1:8000/group/bulk-buy \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "token_address": "EPjFWdd5...",
    "sol_amount": 0.05,
    "slippage": 5.0,
    "password": "secure123"
  }'
```

---

## 💻 SYSTEM REQUIREMENTS

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Network**: Stable internet connection

---

## 🐛 TROUBLESHOOTING

### Bot won't start
```bash
# Check Python version
python3 --version  # Need 3.9+

# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Frontend error
```bash
cd frontend
npm install tailwindcss-animate
npm run dev
```

### Port 8000 in use
```bash
# Change port in backend/.env
API_PORT=8001
```

---

## 📞 SUPPORT

- **API Docs**: http://127.0.0.1:8000/docs
- **Logs**: Check `backend.log` and `frontend.log`
- **Tests**: Run `python tests/test_phase1.py`

---

## 📜 LICENSE

MIT License

---

## ⚠️ DISCLAIMER

**Educational purposes only. Trade at your own risk.**

- Cryptocurrency trading is highly risky
- Past performance ≠ future results
- Never invest more than you can afford to lose
- Always do your own research

---

**VERSION**: 2.0.0  
**STATUS**: Production Ready ✅  
**LAST UPDATED**: December 2024

**Made with ❤️ for Solana traders**
