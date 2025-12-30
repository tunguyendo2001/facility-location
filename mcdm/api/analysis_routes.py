from flask import Blueprint, jsonify, request
from services.analysis_service import AnalysisService
from models.analysis_request import AnalysisRequest
from models.analysis_response import AnalysisResponse
import logging

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analyze', methods=['POST'])
def run_analysis():
    """
    Run MCDM analysis
    
    Request Body:
    {
        "algorithm": "topsis",  // Optional, default: topsis
        "config_id": 1,         // Optional, use active config if not provided
        "top_n": 10             // Optional, number of top results to return
    }
    """
    try:
        # Parse request
        data = request.get_json() or {}
        
        algorithm = data.get('algorithm', 'topsis')
        config_id = data.get('config_id', None)
        top_n = data.get('top_n', 10)
        
        logger.info(f"Analysis request received: algorithm={algorithm}, config_id={config_id}, top_n={top_n}")
        
        # Validate algorithm
        from config import Config
        if algorithm not in Config.SUPPORTED_ALGORITHMS:
            return jsonify({
                'success': False,
                'error': f'Unsupported algorithm: {algorithm}',
                'supported_algorithms': Config.SUPPORTED_ALGORITHMS
            }), 400
        
        # Run analysis
        service = AnalysisService()
        result = service.run_analysis(
            algorithm=algorithm,
            config_id=config_id,
            top_n=top_n
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@analysis_bp.route('/analyze/<algorithm>', methods=['POST'])
def run_specific_analysis(algorithm):
    """
    Run analysis with specific algorithm
    
    Request Body:
    {
        "config_id": 1,         // Optional
        "top_n": 10             // Optional
    }
    """
    try:
        data = request.get_json() or {}
        data['algorithm'] = algorithm
        
        # Reuse the main analysis endpoint logic
        return run_analysis()
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@analysis_bp.route('/results/<int:analysis_id>', methods=['GET'])
def get_results(analysis_id):
    """Get analysis results by ID (future feature)"""
    return jsonify({
        'message': 'Feature not implemented yet',
        'analysis_id': analysis_id
    }), 501
