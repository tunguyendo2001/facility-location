from flask import Blueprint, jsonify, request
from services.analysis_service import AnalysisService
from models.analysis_request import AnalysisRequest
from models.analysis_response import AnalysisResponse
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MCDM Analysis Service',
        'version': '1.0.0'
    }), 200


@health_bp.route('/algorithms', methods=['GET'])
def list_algorithms():
    """List all available MCDM algorithms"""
    from config import Config
    return jsonify({
        'supported_algorithms': Config.SUPPORTED_ALGORITHMS,
        'default_algorithm': Config.DEFAULT_ALGORITHM
    }), 200

