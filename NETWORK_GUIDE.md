# Network Configuration Guide

This guide explains how to switch between Solana networks (Devnet, Testnet, Mainnet).

## 🌐 Available Networks

### 🟡 Devnet (Default - RECOMMENDED for testing)
- **Free SOL**: Get free SOL from faucet
- **No real money**: Perfect for testing
- **Fast**: Quick confirmations
- **Airdrop**: `solana airdrop 2` in devnet

### 🔵 Testnet
- **Testing**: Similar to devnet
- **Stability**: More stable than devnet
- **Free SOL**: Available from faucet

### 🔴 Mainnet (PRODUCTION ONLY)
- **REAL MONEY**: Uses actual SOL
- **⚠️ WARNING**: Only use when ready for production
- **Private RPC**: Use paid RPC for better performance

## 🔧 How to Switch Networks

### Method 1: Edit `.env` file (Recommended)

1. Open `backend/.env`
2. Change the `NETWORK` variable:

```bash
# For Devnet (Testing)
NETWORK=devnet

# For Testnet (Testing)
NETWORK=testnet

# For Mainnet (PRODUCTION - Real Money!)
NETWORK=mainnet
```

3. Restart the backend server
4. The network indicator in the UI will update automatically

### Method 2: Override RPC Endpoint

If you want to use a specific RPC endpoint:

```bash
# In backend/.env
NETWORK=devnet
RPC_ENDPOINT=https://your-custom-rpc-endpoint.com
WS_ENDPOINT=wss://your-custom-ws-endpoint.com
```

## 💰 Getting Test SOL

### Devnet:
```bash
# Using Solana CLI
solana airdrop 2 YOUR_WALLET_ADDRESS --url devnet

# Or use web faucet
# https://faucet.solana.com/
```

### Testnet:
```bash
solana airdrop 2 YOUR_WALLET_ADDRESS --url testnet
```

## 🚨 Important Safety Notes

1. **NEVER use mainnet with test wallets**
2. **ALWAYS test on devnet first**
3. **Use different passwords for test vs production wallets**
4. **Verify network indicator** in UI before trading:
   - 🟡 DEVNET = Safe to test
   - 🔵 TESTNET = Safe to test
   - 🔴 MAINNET = Real money!

## 📊 Network Indicator

The Sniper page shows the current network in the top-right corner:
- 🟡 **DEVNET** - Yellow badge
- 🔵 **TESTNET** - Blue badge
- 🔴 **MAINNET** - Green badge (⚠️ REAL MONEY)

## 🔄 Switching Workflow

### For Development/Testing:
1. Set `NETWORK=devnet` in `.env`
2. Restart backend: `cd backend && python -m src.api.main`
3. Create test wallets
4. Get free SOL from faucet
5. Test all features
6. Verify everything works

### Before Going to Mainnet:
1. ✅ Test thoroughly on devnet
2. ✅ Verify all safety checks work
3. ✅ Understand gas fees and slippage
4. ✅ Get a private RPC endpoint (Helius, QuickNode, etc.)
5. ✅ Use NEW wallets with strong passwords
6. ✅ Start with small amounts
7. ✅ Set `NETWORK=mainnet` in `.env`
8. ✅ Update `MAINNET_RPC` with your private RPC
9. ✅ Restart backend
10. ✅ Double-check network indicator shows 🔴 MAINNET

## 🎯 Recommended Setup

```bash
# backend/.env for TESTING (Current setup)
NETWORK=devnet
RPC_ENDPOINT=https://api.devnet.solana.com
WS_ENDPOINT=wss://api.devnet.solana.com
```

```bash
# backend/.env for PRODUCTION (When ready)
NETWORK=mainnet
MAINNET_RPC=https://your-helius-or-quicknode-rpc.com
RPC_ENDPOINT=https://your-helius-or-quicknode-rpc.com
WS_ENDPOINT=wss://your-helius-or-quicknode-ws.com
```

## 🐛 Troubleshooting

**Network not updating in UI?**
- Hard refresh browser (Ctrl+Shift+R)
- Check backend logs
- Verify `.env` file was saved

**Can't get devnet SOL?**
- Try different faucet: https://faucet.solana.com/
- Use Solana CLI: `solana airdrop 2`
- Check wallet address is correct

**Transactions failing?**
- Verify you're on the right network
- Check you have enough SOL for gas
- Increase slippage if needed

## 📝 Current Status

✅ **You are currently on DEVNET**
- Safe to test
- Free SOL available
- No real money at risk

When ready for mainnet, update `.env` and follow the "Before Going to Mainnet" checklist above! 🚀
