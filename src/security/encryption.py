from cryptography.fernet import Fernet
import os

class EncryptionService:
    """
    Symmetric encryption for user data at rest (profiles, PII).
    Uses Fernet (AES-128-CBC + HMAC under the hood) — simple, no manual
    key rotation infrastructure, key lives in env var.
    """
    def __init__(self, key: str = None):
        key = key or os.environ.get('FERNET_KEY')
        if not key:
            raise ValueError(
                "FERNET_KEY not set. Generate one with EncryptionService.generate_key()"
            )
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)

    @staticmethod
    def generate_key() -> str:
        """Run once, paste result into .env as FERNET_KEY"""
        return Fernet.generate_key().decode()

    def encrypt(self, plaintext: str) -> str:
        if plaintext is None:
            return None
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if ciphertext is None:
            return None
        return self.cipher.decrypt(ciphertext.encode()).decode()

# One-time setup script
if __name__ == "__main__":
    key = EncryptionService.generate_key()
    print(f"Add this to your .env file:\nFERNET_KEY={key}")