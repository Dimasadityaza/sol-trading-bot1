from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class WalletGroup(Base):
    __tablename__ = "wallet_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    wallet_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("wallet_groups.id"), nullable=True)
    wallet_index = Column(Integer, default=0)  # Index within group
    label = Column(String, nullable=False)
    encrypted_private_key = Column(Text, nullable=False)
    public_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_primary = Column(Boolean, default=False)

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, nullable=False)
    token_address = Column(String, nullable=False)
    trade_type = Column(String, nullable=False)  # buy or sell
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float)  # SOL spent
    revenue = Column(Float)  # SOL received
    pnl = Column(Float)  # Profit/Loss
    signature = Column(String, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy = Column(String)  # manual, snipe, copy

class SniperConfig(Base):
    __tablename__ = "sniper_config"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("wallet_groups.id"), nullable=True)
    buy_amount = Column(Float, default=0.1)
    slippage = Column(Float, default=5.0)
    priority_fee = Column(Float, default=0.0001)
    min_liquidity = Column(Float, default=5.0)
    max_buy_tax = Column(Float, default=10.0)
    max_sell_tax = Column(Float, default=10.0)
    require_mint_renounced = Column(Boolean, default=True)
    require_freeze_renounced = Column(Boolean, default=True)
    is_active = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database path
DB_PATH = "sniper.db"

# Create engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized: {DB_PATH}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def close_db(db):
    """Close database session"""
    db.close()
