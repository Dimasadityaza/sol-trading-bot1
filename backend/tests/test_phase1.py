#!/usr/bin/env python3
"""
PHASE 1 TESTING: Backend Core
Tests wallet generation, encryption, database, and API
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test 1: Check if all imports work"""
    print("\n" + "="*60)
    print("TEST 1: MODULE IMPORTS")
    print("="*60)
    
    try:
        from core.wallet import generate_wallet, import_wallet, get_balance, keypair_to_base58
        from core.database import init_db, get_db, Wallet
        from utils.encryption import encrypt_private_key, decrypt_private_key
        print("✓ PASSED: All modules import successfully")
        return True
    except Exception as e:
        print(f"✗ FAILED: Import error - {e}")
        return False

def test_database():
    """Test 2: Database initialization"""
    print("\n" + "="*60)
    print("TEST 2: DATABASE INITIALIZATION")
    print("="*60)
    
    try:
        from core.database import init_db
        init_db()
        
        # Check if database file exists
        if os.path.exists("sniper.db"):
            print("✓ PASSED: Database file created")
            return True
        else:
            print("✗ FAILED: Database file not created")
            return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_wallet_generation():
    """Test 3: Wallet generation"""
    print("\n" + "="*60)
    print("TEST 3: WALLET GENERATION")
    print("="*60)
    
    try:
        from core.wallet import generate_wallet, keypair_to_base58
        
        mnemonic, keypair = generate_wallet()
        
        print(f"Mnemonic (first 3 words): {' '.join(mnemonic.split()[:3])}...")
        print(f"Public Key: {keypair.pubkey()}")
        print(f"Private Key (first 20 chars): {keypair_to_base58(keypair)[:20]}...")
        
        # Validate
        assert len(mnemonic.split()) == 12, "Mnemonic should have 12 words"
        assert str(keypair.pubkey()), "Public key should exist"
        
        print("✓ PASSED: Wallet generated successfully")
        return True, keypair
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False, None

def test_encryption():
    """Test 4: Encryption/Decryption"""
    print("\n" + "="*60)
    print("TEST 4: ENCRYPTION/DECRYPTION")
    print("="*60)
    
    try:
        from core.wallet import generate_wallet, keypair_to_base58
        from utils.encryption import encrypt_private_key, decrypt_private_key
        
        # Generate test wallet
        _, keypair = generate_wallet()
        private_key = keypair_to_base58(keypair)
        password = "test123456"
        
        # Encrypt
        encrypted = encrypt_private_key(private_key, password)
        print(f"Encrypted length: {len(encrypted)} characters")
        
        # Decrypt
        decrypted = decrypt_private_key(encrypted, password)
        
        # Validate
        assert decrypted == private_key, "Decrypted key doesn't match original"
        
        print("✓ PASSED: Encryption/Decryption working correctly")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_wallet_import():
    """Test 5: Wallet import"""
    print("\n" + "="*60)
    print("TEST 5: WALLET IMPORT")
    print("="*60)
    
    try:
        from core.wallet import generate_wallet, import_wallet, keypair_to_base58
        
        # Generate a wallet
        _, original_keypair = generate_wallet()
        private_key = keypair_to_base58(original_keypair)
        
        # Import it
        imported_keypair = import_wallet(private_key, "private_key")
        
        # Validate
        assert str(imported_keypair.pubkey()) == str(original_keypair.pubkey()), "Imported wallet doesn't match"
        
        print(f"Original: {original_keypair.pubkey()}")
        print(f"Imported: {imported_keypair.pubkey()}")
        print("✓ PASSED: Wallet import working correctly")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_balance_check():
    """Test 6: Balance check"""
    print("\n" + "="*60)
    print("TEST 6: BALANCE CHECK")
    print("="*60)
    
    try:
        from core.wallet import generate_wallet, get_balance
        
        # Generate wallet
        _, keypair = generate_wallet()
        public_key = str(keypair.pubkey())
        
        # Get balance
        balance = get_balance(public_key)
        
        print(f"Wallet: {public_key}")
        print(f"Balance: {balance} SOL")
        print("✓ PASSED: Balance check working (balance may be 0)")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_database_operations():
    """Test 7: Database CRUD operations"""
    print("\n" + "="*60)
    print("TEST 7: DATABASE OPERATIONS")
    print("="*60)
    
    try:
        from core.database import get_db, Wallet
        from core.wallet import generate_wallet, keypair_to_base58
        from utils.encryption import encrypt_private_key
        
        db = get_db()
        
        # Create test wallet
        _, keypair = generate_wallet()
        private_key = keypair_to_base58(keypair)
        encrypted = encrypt_private_key(private_key, "test123")
        
        # Insert
        wallet = Wallet(
            label="Test Wallet",
            encrypted_private_key=encrypted,
            public_key=str(keypair.pubkey())
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        
        print(f"Inserted wallet ID: {wallet.id}")
        
        # Query
        retrieved = db.query(Wallet).filter(Wallet.id == wallet.id).first()
        assert retrieved is not None, "Wallet not found in database"
        assert retrieved.label == "Test Wallet", "Label doesn't match"
        
        print(f"Retrieved: {retrieved.label} - {retrieved.public_key}")
        
        # Count
        count = db.query(Wallet).count()
        print(f"Total wallets in DB: {count}")
        
        db.close()
        print("✓ PASSED: Database operations working")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("\n" + "#"*60)
    print("# PHASE 1 - BACKEND CORE TESTING")
    print("#"*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Init", test_database()))
    
    wallet_result, keypair = test_wallet_generation()
    results.append(("Wallet Generation", wallet_result))
    
    results.append(("Encryption", test_encryption()))
    results.append(("Wallet Import", test_wallet_import()))
    results.append(("Balance Check", test_balance_check()))
    results.append(("Database Ops", test_database_operations()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL PHASE 1 TESTS PASSED! 🎉")
        print("\nNext: Install dependencies and test API")
        print("Run: pip install -r requirements.txt")
        print("Then: python -m uvicorn src.api.main:app --reload")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Fix errors before proceeding to next phase")
        return 1

if __name__ == "__main__":
    sys.exit(main())
