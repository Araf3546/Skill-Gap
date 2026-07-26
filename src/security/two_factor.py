import pyotp
import qrcode
import io
import base64
from src.database.models import db, User
from src.security.encryption import EncryptionService

class TwoFactorService:
    def __init__(self):
        self.crypto = EncryptionService()

    def setup_2fa(self, user: User, account_email_plain: str) -> dict:
        """
        Generates a new TOTP secret, stores it encrypted, returns a QR code
        (base64 PNG) for the user to scan in Google Authenticator/Authy.
        """
        secret = pyotp.random_base32()
        user.totp_secret_encrypted = self.crypto.encrypt(secret)
        db.session.commit()

        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=account_email_plain, issuer_name="SkillGap"
        )
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode()

        return {"secret": secret, "qr_code_base64": qr_base64}

    def confirm_and_enable(self, user: User, code: str) -> bool:
        """Call after setup_2fa, once user enters a code from their app."""
        if self.verify_code(user, code):
            user.is_2fa_enabled = True
            db.session.commit()
            return True
        return False

    def verify_code(self, user: User, code: str) -> bool:
        if not user.totp_secret_encrypted:
            return False
        secret = self.crypto.decrypt(user.totp_secret_encrypted)
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # allows 30s clock drift

    def disable_2fa(self, user: User):
        user.is_2fa_enabled = False
        user.totp_secret_encrypted = None
        db.session.commit()