import hashlib
from src.database.models import db, User, Role
from src.security.encryption import EncryptionService

class UserService:
    """
    All reads/writes of PII go through here — nothing else should touch
    email_encrypted / name_encrypted / contact_encrypted directly.
    """
    def __init__(self):
        self.crypto = EncryptionService()

    @staticmethod
    def _hash_email(email: str) -> str:
        # Deterministic hash used only for lookup (not for security, just indexing)
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()

    def register(self, email: str, password: str, name: str = None,
                 contact: str = None, role: Role = Role.USER) -> User:
        email_hash = self._hash_email(email)
        if User.query.filter_by(email_hash=email_hash).first():
            raise ValueError("Email already registered")

        user = User(
            email_hash=email_hash,
            email_encrypted=self.crypto.encrypt(email),
            name_encrypted=self.crypto.encrypt(name) if name else None,
            contact_encrypted=self.crypto.encrypt(contact) if contact else None,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        email_hash = self._hash_email(email)
        user = User.query.filter_by(email_hash=email_hash).first()
        if user and user.check_password(password):
            return user
        return None

    def get_decrypted_profile(self, user: User) -> dict:
        return {
            "id": user.id,
            "email": self.crypto.decrypt(user.email_encrypted),
            "name": self.crypto.decrypt(user.name_encrypted) if user.name_encrypted else None,
            "contact": self.crypto.decrypt(user.contact_encrypted) if user.contact_encrypted else None,
            "role": user.role.value,
            "is_2fa_enabled": user.is_2fa_enabled
        }

    def update_profile(self, user: User, name: str = None, contact: str = None):
        if name is not None:
            user.name_encrypted = self.crypto.encrypt(name)
        if contact is not None:
            user.contact_encrypted = self.crypto.encrypt(contact)
        db.session.commit()
        return user