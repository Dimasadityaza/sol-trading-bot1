from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def derive_key(password: str, salt: bytes = None) -> tuple:
    """Derive encryption key from password"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_private_key(private_key: str, password: str) -> str:
    """Encrypt private key with password"""
    key, salt = derive_key(password)
    f = Fernet(key)
    encrypted = f.encrypt(private_key.encode())
    # Combine salt and encrypted data
    combined = salt + encrypted
    return base64.urlsafe_b64encode(combined).decode()

def decrypt_private_key(encrypted_data: str, password: str) -> str:
    """Decrypt private key with password"""
    try:
        combined = base64.urlsafe_b64decode(encrypted_data.encode())
        salt = combined[:16]
        encrypted = combined[16:]
        
        key, _ = derive_key(password, salt)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted)
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
