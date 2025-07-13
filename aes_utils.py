# agent254/aes_utils.py
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
# Note: The original aes_utils.py used custom padding.
# For better practice, it's recommended to use Crypto.Util.Padding.pad and unpad
# if you are sure about the padding scheme (e.g., PKCS7).
# If you intend to use the custom padding, ensure it's robust.
# For now, I'll keep the custom padding as it was in your provided file.
import hmac
import hashlib
import secrets  # Import secrets for more secure random string generation
import string   # Import string for character sets


def generate_aes_key() -> bytes:
    """Generates a new, random 256-bit (32-byte) AES key."""
    return get_random_bytes(32)


def encrypt_message(plaintext_bytes: bytes, aes_key: bytes):
    """
    Encrypts a message and returns Base64 encoded key and ciphertext.
    The IV is prepended to the ciphertext before Base64 encoding.
    """
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # PKCS7 Padding (as implemented in your original file)
    # This adds bytes equal to the pad_len at the end of the message
    pad_len = 16 - (len(plaintext_bytes) % 16)
    padded_message = plaintext_bytes + bytes([pad_len]) * pad_len
    ciphertext_bytes = cipher.encrypt(padded_message)

    # Encode binary data to Base64 strings for storage/transmission
    # The IV is returned separately and also stored in the database as bytes.
    encoded_ciphertext = base64.b64encode(ciphertext_bytes).decode('ascii')
    encoded_aes_key = base64.b64encode(aes_key).decode('ascii')

    return encoded_ciphertext, iv, encoded_aes_key


def decrypt_message(encoded_ciphertext: str, iv: bytes, encoded_aes_key: str):
    """
    Accepts Base64 encoded ciphertext, IV (bytes), and Base64 encoded AES key,
    then returns the decrypted plaintext.
    """
    try:
        # Decode Base64 strings back to binary before decryption
        ciphertext_bytes = base64.b64decode(encoded_ciphertext.encode('ascii'))
        aes_key = base64.b64decode(encoded_aes_key.encode('ascii'))

        # Add checks for IV and key lengths before creating cipher
        if len(iv) != 16:
            raise ValueError(f"IV must be 16 bytes long, but got {len(iv)} bytes.")
        # AES key can be 16 (AES-128), 24 (AES-192), or 32 (AES-256) bytes
        if len(aes_key) not in [16, 24, 32]:
            raise ValueError(f"AES key must be 16, 24, or 32 bytes long, but got {len(aes_key)} bytes.")

        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext_bytes)

        # Unpad (as implemented in your original file)
        # This assumes PKCS7 padding where the last byte indicates pad length.
        pad_len = padded_plaintext[-1]
        # Basic check to prevent IndexError if pad_len is invalid or data is too short
        if not (1 <= pad_len <= AES.block_size and len(padded_plaintext) >= pad_len):
            raise ValueError(f"Invalid padding detected or corrupted ciphertext. Pad length: {pad_len}")

        plaintext_bytes = padded_plaintext[:-pad_len]

        return plaintext_bytes.decode('utf-8')
    except (ValueError, TypeError, IndexError) as e:
        # Enhanced error reporting for debugging decryption issues
        print(f"Decryption error (aes_utils.py): {type(e).__name__}: {e}")
        print(f"Debug Info - Encoded Ciphertext Length: {len(encoded_ciphertext) if encoded_ciphertext else 'N/A'}")
        print(f"Debug Info - IV Length: {len(iv) if iv else 'N/A'}")
        print(f"Debug Info - Encoded AES Key Length: {len(encoded_aes_key) if encoded_aes_key else 'N/A'}")
        return None


def derive_otp(salt: bytes) -> tuple[str, str, bytes]:
    """
    Generates a new random 6-character alphanumeric OTP and its HMAC hash.
    Returns the plaintext OTP, its hash, and the salt used.
    """
    # Generate a random 6-character alphanumeric OTP using secrets for security
    characters = string.ascii_uppercase + string.digits
    otp_code = ''.join(secrets.choice(characters) for i in range(6))

    # Calculate HMAC hash of the OTP using the provided salt
    # The OTP needs to be encoded to bytes for hmac.new
    otp_hash = hmac.new(salt, otp_code.encode('utf-8'), hashlib.sha256).hexdigest()

    # Return all three expected values to match routes.py unpacking
    return otp_code, otp_hash, salt
