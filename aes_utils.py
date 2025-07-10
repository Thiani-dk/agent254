# agent254/aes_utils.py
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hmac
import hashlib
import secrets # NEW: Import secrets for more secure random string generation
import string # NEW: Import string for character sets

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

# UPDATED FUNCTION:
def derive_otp(salt: bytes) -> tuple[str, str, bytes]:
    """
    Generates a new random 6-character OTP and its HMAC hash.
    Returns the plaintext OTP, its hash, and the salt used.
    """
    # Generate a random 6-character alphanumeric OTP
    characters = string.ascii_uppercase + string.digits
    otp_code = ''.join(secrets.choice(characters) for i in range(6)) # Use secrets for better randomness

    # Calculate HMAC hash of the OTP using the provided salt
    # The OTP needs to be encoded to bytes for hmac.new
    otp_hash = hmac.new(salt, otp_code.encode('utf-8'), hashlib.sha256).hexdigest()

    return otp_code, otp_hash, salt # Return all three expected values to match routes.py unpacking