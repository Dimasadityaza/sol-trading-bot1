#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Tests all features of Solana Sniper Bot
"""

import asyncio
import httpx
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test results
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(name, passed, message=""):
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if message:
        print(f"         {message}")
    
    test_results.append({
        "name": name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1

async def test_health():
    """Test API health endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            passed = response.status_code == 200
            log_test("Health Check", passed, f"Status: {response.status_code}")
            return passed
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False

async def test_create_wallet():
    """Test wallet creation"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/wallet/create",
                json={
                    "password": "test123456",
                    "label": "Integration Test Wallet"
                }
            )
            passed = response.status_code == 200
            if passed:
                data = response.json()
                wallet_id = data.get("id")
                log_test("Create Wallet", True, f"Created wallet ID: {wallet_id}")
                return wallet_id
            else:
                log_test("Create Wallet", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Create Wallet", False, str(e))
        return None

async def test_list_wallets():
    """Test wallet listing"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/wallet/list")
            passed = response.status_code == 200
            if passed:
                wallets = response.json()
                log_test("List Wallets", True, f"Found {len(wallets)} wallets")
                return wallets
            else:
                log_test("List Wallets", False, f"Status: {response.status_code}")
                return []
    except Exception as e:
        log_test("List Wallets", False, str(e))
        return []

async def test_get_wallet(wallet_id):
    """Test get wallet details"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/wallet/{wallet_id}")
            passed = response.status_code == 200
            if passed:
                wallet = response.json()
                log_test("Get Wallet", True, f"Label: {wallet.get('label')}")
                return wallet
            else:
                log_test("Get Wallet", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Get Wallet", False, str(e))
        return None

async def test_get_balance(wallet_id):
    """Test balance check"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/wallet/{wallet_id}/balance")
            passed = response.status_code == 200
            if passed:
                balance = response.json()
                log_test("Get Balance", True, f"Balance: {balance.get('balance')} SOL")
                return balance
            else:
                log_test("Get Balance", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Get Balance", False, str(e))
        return None

async def test_token_analysis():
    """Test token analysis"""
    try:
        # Use USDC as test token
        token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/trade/analyze",
                json={"token_address": token}
            )
            passed = response.status_code == 200
            if passed:
                analysis = response.json()
                score = analysis.get("safety_score", 0)
                log_test("Token Analysis", True, f"Safety score: {score}/100")
                return analysis
            else:
                log_test("Token Analysis", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Token Analysis", False, str(e))
        return None

async def test_trade_history():
    """Test trade history endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/trade/history?limit=10")
            passed = response.status_code == 200
            if passed:
                trades = response.json()
                log_test("Trade History", True, f"Found {len(trades)} trades")
                return trades
            else:
                log_test("Trade History", False, f"Status: {response.status_code}")
                return []
    except Exception as e:
        log_test("Trade History", False, str(e))
        return []

async def test_trade_stats():
    """Test trading statistics"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/trade/stats")
            passed = response.status_code == 200
            if passed:
                stats = response.json()
                log_test("Trade Stats", True, f"Total trades: {stats.get('total_trades', 0)}")
                return stats
            else:
                log_test("Trade Stats", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Trade Stats", False, str(e))
        return None

async def test_analytics_pnl():
    """Test analytics PnL endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/analytics/pnl")
            passed = response.status_code == 200
            if passed:
                pnl = response.json()
                log_test("Analytics PnL", True, f"Total: {pnl.get('total', 0)} SOL")
                return pnl
            else:
                log_test("Analytics PnL", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Analytics PnL", False, str(e))
        return None

async def test_analytics_portfolio():
    """Test analytics portfolio endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/analytics/portfolio")
            passed = response.status_code == 200
            if passed:
                portfolio = response.json()
                log_test("Analytics Portfolio", True, "Portfolio data retrieved")
                return portfolio
            else:
                log_test("Analytics Portfolio", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Analytics Portfolio", False, str(e))
        return None

async def test_sniper_status():
    """Test sniper status endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/sniper/status")
            passed = response.status_code == 200
            if passed:
                status = response.json()
                log_test("Sniper Status", True, f"Running: {status.get('is_running', False)}")
                return status
            else:
                log_test("Sniper Status", False, f"Status: {response.status_code}")
                return None
    except Exception as e:
        log_test("Sniper Status", False, str(e))
        return None

async def test_delete_wallet(wallet_id):
    """Test wallet deletion"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{BASE_URL}/wallet/{wallet_id}")
            passed = response.status_code == 200
            log_test("Delete Wallet", passed, f"Deleted wallet {wallet_id}")
            return passed
    except Exception as e:
        log_test("Delete Wallet", False, str(e))
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("🧪 SOLANA SNIPER BOT - COMPREHENSIVE INTEGRATION TESTS")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {BASE_URL}")
    print("="*70 + "\n")
    
    # Core API Tests
    print("📡 CORE API TESTS")
    print("-" * 70)
    await test_health()
    
    # Wallet Tests
    print("\n💼 WALLET TESTS")
    print("-" * 70)
    wallet_id = await test_create_wallet()
    await test_list_wallets()
    
    if wallet_id:
        await test_get_wallet(wallet_id)
        await test_get_balance(wallet_id)
    
    # Trading Tests
    print("\n💹 TRADING TESTS")
    print("-" * 70)
    await test_token_analysis()
    await test_trade_history()
    await test_trade_stats()
    
    # Analytics Tests
    print("\n📊 ANALYTICS TESTS")
    print("-" * 70)
    await test_analytics_pnl()
    await test_analytics_portfolio()
    
    # Sniper Tests
    print("\n🎯 SNIPER TESTS")
    print("-" * 70)
    await test_sniper_status()
    
    # Cleanup
    print("\n🧹 CLEANUP")
    print("-" * 70)
    if wallet_id:
        await test_delete_wallet(wallet_id)
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    print("="*70)
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! SYSTEM IS WORKING PERFECTLY! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} TEST(S) FAILED. CHECK LOGS ABOVE.\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
