from flask import Blueprint, jsonify

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analyze', methods=['GET'])
def analyze_placeholder():
    return jsonify({"message": "Analysis endpoint is available"}), 200
