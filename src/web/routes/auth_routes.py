from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token
from functools import wraps
from src.security.user_service import UserService
from src.security.two_factor import TwoFactorService
from src.database.models import Role

auth_bp = Blueprint('auth', __name__)
user_service = UserService()
tfa_service = TwoFactorService()

def roles_required(*roles):
    """RBAC decorator — restricts route to given roles."""
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['email', 'password']
    if not all(k in data for k in required):
        return jsonify({"error": "email and password required"}), 400
    if len(data['password']) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    try:
        user = user_service.register(
            email=data['email'],
            password=data['password'],
            name=data.get('name'),
            contact=data.get('contact')
        )
        return jsonify({"message": "Registered successfully", "user_id": user.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = user_service.authenticate(data.get('email', ''), data.get('password', ''))
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Step 1 passed. If 2FA enabled, require second factor before full login.
    if user.is_2fa_enabled:
        session['pending_2fa_user_id'] = user.id
        session.permanent = False
        return jsonify({"message": "2FA code required", "requires_2fa": True}), 200

    return _finalize_login(user)

@auth_bp.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    pending_id = session.get('pending_2fa_user_id')
    if not pending_id:
        return jsonify({"error": "No pending 2FA verification"}), 400

    from src.database.models import User
    user = User.query.get(pending_id)
    code = request.get_json().get('code', '')

    if not tfa_service.verify_code(user, code):
        return jsonify({"error": "Invalid 2FA code"}), 401

    session.pop('pending_2fa_user_id', None)
    return _finalize_login(user)

def _finalize_login(user):
    from datetime import datetime
    from src.database.models import db
    login_user(user, remember=False)  # Flask-Login secure session cookie
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Also issue a JWT for API/mobile-style access
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value}
    )
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": user.role.value
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route('/setup-2fa', methods=['POST'])
@login_required
def setup_2fa():
    profile = user_service.get_decrypted_profile(current_user)
    result = tfa_service.setup_2fa(current_user, profile['email'])
    return jsonify(result), 200

@auth_bp.route('/confirm-2fa', methods=['POST'])
@login_required
def confirm_2fa():
    code = request.get_json().get('code', '')
    if tfa_service.confirm_and_enable(current_user, code):
        return jsonify({"message": "2FA enabled"}), 200
    return jsonify({"error": "Invalid code"}), 400

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(user_service.get_decrypted_profile(current_user)), 200

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    user_service.update_profile(current_user, name=data.get('name'), contact=data.get('contact'))
    return jsonify({"message": "Profile updated"}), 200

# Example admin-only route (RBAC in action)
@auth_bp.route('/admin/users', methods=['GET'])
@roles_required(Role.ADMIN)
def list_all_users():
    from src.database.models import User
    users = User.query.all()
    return jsonify([
        {"id": u.id, "role": u.role.value, "is_banned": u.is_banned} for u in users
    ]), 200

@auth_bp.route('/admin/users/<int:user_id>/ban', methods=['POST'])
@roles_required(Role.ADMIN)
def ban_user(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "Cannot ban yourself"}), 400
    try:
        user = user_service.ban_user(user_id)
        return jsonify({"message": "User banned", "user_id": user.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@auth_bp.route('/admin/users/<int:user_id>/unban', methods=['POST'])
@roles_required(Role.ADMIN)
def unban_user(user_id):
    try:
        user = user_service.unban_user(user_id)
        return jsonify({"message": "User unbanned", "user_id": user.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404