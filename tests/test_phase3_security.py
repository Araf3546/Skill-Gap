"""
Full security + feature integration test.
Run: python tests/test_phase3_security.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from src.database.models import db, Role
from src.security.user_service import UserService
from src.security.two_factor import TwoFactorService
from src.services.resume_history_service import ResumeHistoryService
from src.services.feedback_services import FeedbackService

def test_full_phase3():
    app = create_app()
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        print("="*60)
        print("PHASE 3 SECURITY INTEGRATION TEST")
        print("="*60)

        user_service = UserService()
        tfa_service = TwoFactorService()
        history_service = ResumeHistoryService()
        feedback_service = FeedbackService()

        # 1. Register (encrypted PII + hashed password)
        print("\n[1/6] Registering user...")
        user = user_service.register(
            email="test.phase3@example.com",
            password="SecurePass123!",
            name="Test User",
            contact="+8801000000000"
        )
        print(f"[OK] User created, id={user.id}, role={user.role.value}")

        # 2. Verify PII is encrypted in DB (not plaintext)
        assert "test.phase3" not in user.email_encrypted
        print("[OK] Email stored encrypted (not plaintext)")

        # 3. Authenticate
        print("\n[2/6] Authenticating...")
        authed = user_service.authenticate("test.phase3@example.com", "SecurePass123!")
        assert authed is not None
        print("[OK] Login successful with bcrypt password check")

        wrong = user_service.authenticate("test.phase3@example.com", "wrongpass")
        assert wrong is None
        print("[OK] Wrong password correctly rejected")

        # 4. 2FA setup + verify
        print("\n[3/6] Setting up 2FA...")
        setup_result = tfa_service.setup_2fa(user, "test.phase3@example.com")
        import pyotp
        code = pyotp.TOTP(setup_result['secret']).now()
        enabled = tfa_service.confirm_and_enable(user, code)
        assert enabled
        print("[OK] 2FA enabled and verified with live TOTP code")

        # 5. Resume history
        print("\n[4/6] Testing resume history...")
        v1 = history_service.save_version(user.id, "resume_v1.pdf", ["Python", "SQL"])
        v2 = history_service.save_version(user.id, "resume_v2.pdf", ["Python", "SQL", "Docker"])
        comparison = history_service.compare_versions(user.id, v1.version_number, v2.version_number)
        assert "Docker" in comparison["gained_skills"]
        print(f"[OK] Version comparison works: gained {comparison['gained_skills']}")

        # 6. Feedback loop
        print("\n[5/6] Testing feedback loop...")
        feedback_service.record_feedback(user.id, v2.id, "Docker", True)
        feedback_service.record_feedback(user.id, v2.id, "Python", False)
        report = feedback_service.get_skill_accuracy_report()
        assert len(report) > 0
        print(f"[OK] Accuracy report generated: {report}")

        # 7. RBAC check
        print("\n[6/6] Testing RBAC...")
        admin = user_service.register(
            email="admin.phase3@example.com", password="AdminPass123!", role=Role.ADMIN
        )
        assert admin.is_admin()
        assert not user.is_admin()
        print("[OK] Role separation confirmed (admin vs regular user)")

        print("\n" + "="*60)
        print("[OK] PHASE 3 COMPLETE - ALL SECURITY & FEATURES VERIFIED")
        print("="*60)

if __name__ == "__main__":
    test_full_phase3()