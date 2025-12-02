import os
from dotenv import load_dotenv

load_dotenv()

# RPC Configuration - MAINNET by default
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
WS_ENDPOINT = os.getenv("WS_ENDPOINT", "wss://api.mainnet-beta.solana.com")

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
