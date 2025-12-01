# 🎯 SOLANA MULTI-WALLET GROUP BOT

**Standalone bot untuk manage ratusan wallet dan bulk trading operations**

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Version](https://img.shields.io/badge/Version-2.0-blue)

---

## ✨ FITUR UTAMA

### 🔐 Group Management
- ✅ Auto-generate 5-1000 wallet sekaligus
- ✅ Auto-naming: "Group 1 - Wallet 1", "Group 1 - Wallet 2", dst
- ✅ List, view, delete groups
- ✅ Get total balances untuk semua wallet

### 💸 SOL Operations
- ✅ **Distribute SOL**: Sebar SOL dari 1 wallet ke semua wallet dalam group
- ✅ **Collect SOL**: Kumpulkan SOL dari semua wallet ke 1 wallet
- ✅ Auto-calculation dan batch processing

### 📈 Trading Operations
- ✅ **Bulk Buy**: Buy token dari semua wallet sekaligus
- ✅ **Bulk Sell**: Sell token dari semua wallet sekaligus
- ✅ Configurable slippage per operation
- ✅ Success/failure tracking per wallet

### 🎛️ Configuration
- ✅ Password protection per group
- ✅ Access private keys by group + index
- ✅ Slippage settings per operation
- ✅ Custom amounts per wallet

---

## 🚀 QUICK START

### Linux / macOS:
```bash
chmod +x start-multi-wallet.sh
./start-multi-wallet.sh
```

### Windows:
```bash
start-multi-wallet.bat
```

**Bot akan jalan di**: `http://127.0.0.1:8000`

**API Docs**: `http://127.0.0.1:8000/docs`

---

## 📚 API ENDPOINTS

### Group Management

#### 1. Create Group
```bash
POST /group/create

Body:
{
  "name": "Pump.fun Snipers",
  "description": "20 wallets for sniping",
  "count": 20,
  "password": "secure123"
}

Response:
{
  "success": true,
  "group_id": 1,
  "group_name": "Pump.fun Snipers",
  "wallet_count": 20,
  "wallets": [
    {
      "id": 1,
      "index": 1,
      "label": "Pump.fun Snipers - Wallet 1",
      "address": "ABC123...",
      "mnemonic": "word1 word2 ... word24"
    },
    ...
  ]
}
```

⚠️ **PENTING**: Save semua mnemonic phrases!

#### 2. List Groups
```bash
GET /group/list

Response:
{
  "groups": [
    {
      "id": 1,
      "name": "Pump.fun Snipers",
      "wallet_count": 20,
      "created_at": "2025-12-01..."
    }
  ]
}
```

#### 3. Get Group Details
```bash
GET /group/{group_id}

Response:
{
  "id": 1,
  "name": "Pump.fun Snipers",
  "wallet_count": 20,
  "wallets": [...]
}
```

#### 4. Get Group Balances
```bash
GET /group/{group_id}/balances

Response:
{
  "group_id": 1,
  "total_balance": 2.5,
  "wallets": [
    {
      "id": 1,
      "index": 1,
      "address": "ABC...",
      "balance": 0.1
    },
    ...
  ]
}
```

#### 5. Delete Group
```bash
DELETE /group/{group_id}
```

---

### SOL Operations

#### 6. Distribute SOL
```bash
POST /group/distribute-sol

Body:
{
  "from_wallet_id": 1,
  "to_group_id": 1,
  "amount_per_wallet": 0.1,
  "password": "secure123"
}

Response:
{
  "total_wallets": 20,
  "successful": 20,
  "failed": 0,
  "total_sol_sent": 2.0,
  "results": [...]
}
```

#### 7. Collect SOL
```bash
POST /group/collect-sol

Body:
{
  "from_group_id": 1,
  "to_wallet_id": 1,
  "password": "secure123",
  "leave_amount": 0.001
}

Response:
{
  "total_wallets": 20,
  "successful": 20,
  "total_collected": 1.98,
  "results": [...]
}
```

---

### Trading Operations

#### 8. Bulk Buy
```bash
POST /group/bulk-buy

Body:
{
  "group_id": 1,
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "sol_amount": 0.05,
  "slippage": 5.0,
  "password": "secure123"
}

Response:
{
  "total_wallets": 20,
  "successful": 20,
  "failed": 0,
  "token_address": "EPjFWdd5...",
  "results": [
    {
      "wallet_id": 1,
      "wallet_index": 1,
      "success": true,
      "signature": "5xY...",
      "explorer_url": "https://solscan.io/tx/..."
    },
    ...
  ]
}
```

#### 9. Bulk Sell
```bash
POST /group/bulk-sell

Body:
{
  "group_id": 1,
  "token_address": "EPjFWdd5...",
  "percentage": 100,
  "slippage": 5.0,
  "password": "secure123"
}

Response:
{
  "total_wallets": 20,
  "successful": 19,
  "failed": 1,
  "results": [...]
}
```

---

## 💡 USE CASES

### Case 1: Setup 50 Wallets untuk Volume Trading
```bash
# 1. Create group
POST /group/create
{
  "name": "Volume Bots",
  "count": 50,
  "password": "mypass"
}

# 2. Distribute 0.05 SOL ke tiap wallet
POST /group/distribute-sol
{
  "from_wallet_id": 1,
  "to_group_id": 1,
  "amount_per_wallet": 0.05,
  "password": "mypass"
}

# Total cost: 50 x 0.05 = 2.5 SOL
```

### Case 2: Snipe New Token dengan 20 Wallets
```bash
# Buy dari 20 wallets bersamaan
POST /group/bulk-buy
{
  "group_id": 1,
  "token_address": "NEW_TOKEN_HERE",
  "sol_amount": 0.05,
  "slippage": 10.0,
  "password": "mypass"
}

# Total buy: 20 x 0.05 = 1.0 SOL volume
```

### Case 3: Take Profit & Collect
```bash
# 1. Sell semua holdings
POST /group/bulk-sell
{
  "group_id": 1,
  "token_address": "TOKEN_ADDRESS",
  "percentage": 100,
  "slippage": 5.0,
  "password": "mypass"
}

# 2. Collect profit ke main wallet
POST /group/collect-sol
{
  "from_group_id": 1,
  "to_wallet_id": 1,
  "password": "mypass"
}
```

---

## 📋 REQUIREMENTS

- Python 3.9+
- pip
- Internet connection
- SOL for trading (devnet atau mainnet)

---

## ⚙️ CONFIGURATION

### File: `backend/.env`
```bash
# Solana Network
RPC_ENDPOINT=https://api.devnet.solana.com
WS_ENDPOINT=wss://api.devnet.solana.com

# Database
DATABASE_URL=sqlite:///./multi_wallet.db

# Security (GANTI INI!)
ENCRYPTION_KEY=your-super-secret-key-minimum-32-characters

# API
API_HOST=0.0.0.0
API_PORT=8000
```

⚠️ **WAJIB GANTI** `ENCRYPTION_KEY` sebelum production!

---

## 🔒 SECURITY BEST PRACTICES

1. **Ganti Encryption Key**
   - Minimal 32 karakter
   - Random string
   - Simpan dengan aman

2. **Password Management**
   - 1 password per group
   - Minimal 12 karakter
   - Jangan share dengan siapapun

3. **Private Keys**
   - Save semua mnemonic phrases
   - Backup di tempat aman (offline)
   - Jangan screenshot atau kirim via chat

4. **Testing**
   - Test di devnet dulu
   - Gunakan amount kecil
   - Verify semua transactions

---

## 🐛 TROUBLESHOOTING

### Bot tidak start
```bash
# Check Python version
python3 --version  # Harus 3.9+

# Install dependencies manual
cd backend
pip install -r requirements.txt
```

### Database error
```bash
# Hapus database dan restart
cd backend
rm multi_wallet.db
cd ..
./start-multi-wallet.sh
```

### Connection refused
```bash
# Check apakah port 8000 dipakai
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process yang pakai port 8000
```

---

## 📊 PROJECT STRUCTURE

```
multi-wallet-bot/
├── start-multi-wallet.sh       # Linux/Mac launcher
├── start-multi-wallet.bat      # Windows launcher
├── README-MULTI-WALLET.md      # This file
│
└── backend/
    ├── requirements.txt        # Python dependencies
    ├── .env                    # Configuration (auto-created)
    │
    └── src/
        ├── core/
        │   ├── database.py              # Database models
        │   ├── group_manager.py         # Group management
        │   └── bulk_operations.py       # Bulk operations
        │
        └── api/
            ├── main.py                  # Main API
            └── routes/
                └── groups.py            # Group API routes
```

---

## 🎓 TIPS & TRICKS

### 1. Multiple Groups untuk Different Strategies
```bash
# Group 1: Sniping (fast, small amounts)
POST /group/create {"name": "Snipers", "count": 20}

# Group 2: Volume (many wallets)
POST /group/create {"name": "Volume", "count": 100}

# Group 3: Hold (long-term)
POST /group/create {"name": "Holders", "count": 10}
```

### 2. Optimal Slippage Settings
- **Buy**: 5-10% (untuk fast tokens)
- **Sell**: 3-5% (take profit)
- **Low liquidity**: 10-15%

### 3. Leave Amount untuk Rent
- Minimum: 0.001 SOL
- Recommended: 0.002 SOL
- Untuk safety: 0.005 SOL

---

## 📈 PERFORMANCE

- **Create 100 wallets**: ~30 seconds
- **Distribute SOL (100 wallets)**: ~2-3 minutes
- **Bulk buy (100 wallets)**: ~3-5 minutes
- **Collect SOL (100 wallets)**: ~2-3 minutes

*Performance tergantung RPC endpoint dan network congestion*

---

## ⚠️ DISCLAIMER

- Trading cryptocurrencies berisiko tinggi
- Bot ini untuk educational purposes
- Gunakan dengan bijak
- Never invest lebih dari yang mampu Anda lose
- Test di devnet dulu sebelum mainnet

---

## 📞 SUPPORT

### API Documentation
```
http://127.0.0.1:8000/docs
```

### Check Logs
```bash
cat bot.log
```

### Restart Bot
```bash
# Linux/Mac
./start-multi-wallet.sh

# Windows
start-multi-wallet.bat
```

---

## 🎯 ROADMAP

**Completed ✅:**
- [x] Multi-wallet group creation
- [x] Distribute/Collect SOL
- [x] Bulk buy/sell operations
- [x] Group management
- [x] Balance tracking

**Coming Soon:**
- [ ] Frontend UI
- [ ] Token distribution
- [ ] Auto-sniper per group
- [ ] Advanced analytics
- [ ] Export/import groups

---

**VERSION**: 2.0.0  
**STATUS**: Production Ready ✅  
**LICENSE**: MIT  

**Made with ❤️ for Solana traders**
