# aes_utils.py

import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256

def generate_aes_key() -> bytes:
    return get_random_bytes(32)  # 256 bits

def encrypt_aes(plain_text: bytes, key: bytes) -> tuple[bytes, bytes]:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pad_len = 16 - (len(plain_text) % 16)
    padded = plain_text + bytes([pad_len]) * pad_len
    ct_bytes = cipher.encrypt(padded)
    return iv, ct_bytes

def decrypt_aes(iv: bytes, ciphertext: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ciphertext)
    pad_len = padded[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding.")
    return padded[:-pad_len]

def derive_otp(key: bytes, salt: bytes, digits: int = 6) -> str:
    h = HMAC.new(salt, digestmod=SHA256)
    h.update(key)
    full = h.digest()
    code_int = int.from_bytes(full, "big") % (10 ** digits)
    return str(code_int).zfill(digits)
