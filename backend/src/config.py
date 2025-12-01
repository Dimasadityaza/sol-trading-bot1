import os
from dotenv import load_dotenv

load_dotenv()

# Network Configuration
NETWORK = os.getenv("NETWORK", "devnet")  # devnet, testnet, or mainnet

# RPC Configuration based on network
RPC_ENDPOINTS = {
    "devnet": "https://api.devnet.solana.com",
    "testnet": "https://api.testnet.solana.com",
    "mainnet": os.getenv("MAINNET_RPC", "https://api.mainnet-beta.solana.com"),
}

WS_ENDPOINTS = {
    "devnet": "wss://api.devnet.solana.com",
    "testnet": "wss://api.testnet.solana.com",
    "mainnet": "wss://api.mainnet-beta.solana.com",
}

RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", RPC_ENDPOINTS.get(NETWORK, RPC_ENDPOINTS["devnet"]))
WS_ENDPOINT = os.getenv("WS_ENDPOINT", WS_ENDPOINTS.get(NETWORK, WS_ENDPOINTS["devnet"]))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sniper.db")

# Security
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key-please-change-in-production-min-32-chars")

# Jupiter API
JUPITER_API_URL = "https://quote-api.jup.ag/v6"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
