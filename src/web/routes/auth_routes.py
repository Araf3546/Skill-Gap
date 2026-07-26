from flask import Blueprint, jsonify

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    return jsonify({"message": "Auth login endpoint is available"}), 200


@auth_bp.route('/register', methods=['GET'])
def register():
    return jsonify({"message": "Auth register endpoint is available"}), 200
