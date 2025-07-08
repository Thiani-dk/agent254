# agent254/aes_utils.py
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hmac
import hashlib

def generate_aes_key() -> bytes:
    """Generates a new, random 256-bit (32-byte) AES key."""
    return get_random_bytes(32)

def encrypt_message(plaintext_bytes: bytes, aes_key: bytes):
    """Encrypts a message and returns Base64 encoded key and ciphertext."""
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # PKCS7 Padding
    pad_len = 16 - (len(plaintext_bytes) % 16)
    padded_message = plaintext_bytes + bytes([pad_len]) * pad_len
    ciphertext_bytes = cipher.encrypt(padded_message)

    # Encode binary data to Base64 strings for storage
    encoded_ciphertext = base64.b64encode(ciphertext_bytes).decode('ascii')
    encoded_aes_key = base64.b64encode(aes_key).decode('ascii')

    return encoded_ciphertext, iv, encoded_aes_key

def decrypt_message(encoded_ciphertext: str, iv: bytes, encoded_aes_key: str):
    """Accepts Base64 encoded values and returns decrypted plaintext."""
    try:
        # Decode Base64 strings back to binary before decryption
        ciphertext_bytes = base64.b64decode(encoded_ciphertext.encode('ascii'))
        aes_key = base64.b64decode(encoded_aes_key.encode('ascii'))

        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext_bytes)

        # Unpad
        pad_len = padded_plaintext[-1]
        plaintext_bytes = padded_plaintext[:-pad_len]

        return plaintext_bytes.decode('utf-8')
    except (ValueError, TypeError, IndexError) as e:
        # Handles errors from bad Base64 padding or other decoding issues
        print(f"Decryption error: {e}")
        return None

def derive_otp(key: bytes, salt: bytes) -> str:
    """Derives a 6-character OTP from the AES key and salt."""
    hm = hmac.new(salt, key, hashlib.sha256).hexdigest()
    return hm[:6].upper()