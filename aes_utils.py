# aes_utils.py

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hmac, hashlib

def generate_aes_key() -> bytes:
    return get_random_bytes(32)  # 256-bit key

def encrypt_aes(plaintext: bytes, key: bytes):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # PKCS7 padding
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len]) * pad_len
    ciphertext = cipher.encrypt(padded)
    return iv, ciphertext

def decrypt_aes(iv: bytes, ciphertext: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ciphertext)
    pad_len = padded[-1]
    return padded[:-pad_len]

def derive_otp(key: bytes, salt: bytes) -> str:
    """
    Derive a 6-digit OTP from the AES‐key + salt using HMAC-SHA256,
    then take the first 6 digits of its hex digest.
    """
    hm = hmac.new(salt, key, hashlib.sha256).hexdigest()
    
    # --- BUG FIX: Case Sensitivity ---
    # Return first 6 hex characters in UPPERCASE for consistency.
    return hm[:6].upper()