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
    Run MCDM analysis and save to evaluation_result table
    
    Request Body:
    {
        "algorithm": "topsis",  // Optional, default: topsis
        "config_id": 1,         // Optional, use active config if not provided
        "user_id": 1,           // Optional, user performing analysis
        "top_n": 10             // Optional, number of top results to return
    }
    
    Response:
    {
        "success": true,
        "algorithm": "TOPSIS",
        "strategy_name": "Phủ Sóng Thị Trường",
        "batch_id": "TOPSIS_20260117_143022_a1b2c3d4",
        "sites_analyzed": 80,
        "execution_time_seconds": 0.45,
        "execution_time_ms": 450,
        "timestamp": "2026-01-17T14:30:22.123456",
        "config_id": 1,
        "user_id": 1,
        "score_statistics": {...},
        "top_sites": [...]
    }
    """
    try:
        # Parse request
        data = request.get_json() or {}
        
        algorithm = data.get('algorithm', 'topsis')
        config_id = data.get('config_id', None)
        user_id = data.get('user_id', None)
        top_n = data.get('top_n', 10)
        
        logger.info(f"Analysis request: algorithm={algorithm}, config_id={config_id}, user_id={user_id}, top_n={top_n}")
        
        # Validate algorithm
        from config import Config
        if algorithm.lower() not in [a.lower() for a in Config.SUPPORTED_ALGORITHMS]:
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
            user_id=user_id,
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
        "user_id": 1,           // Optional
        "top_n": 10             // Optional
    }
    """
    try:
        data = request.get_json() or {}
        data['algorithm'] = algorithm
        
        # Forward to main analyze endpoint
        request_data = request.get_json()
        request_data['algorithm'] = algorithm
        
        return run_analysis()
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@analysis_bp.route('/results/latest', methods=['GET'])
def get_latest_batch_results():
    """
    Get results from the latest analysis batch
    
    Query Parameters:
    - limit: Number of top results (default: 10)
    
    Example: GET /api/results/latest?limit=20
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        service = AnalysisService()
        result = service.get_batch_results(batch_id=None, limit=limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting latest results: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.route('/results/batch/<batch_id>', methods=['GET'])
def get_batch_results(batch_id):
    """
    Get results from a specific batch
    
    Query Parameters:
    - limit: Number of results (default: 10)
    
    Example: GET /api/results/batch/TOPSIS_20260117_143022_a1b2c3d4?limit=20
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        service = AnalysisService()
        result = service.get_batch_results(batch_id=batch_id, limit=limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting batch results: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.route('/site/<int:site_id>/history', methods=['GET'])
def get_site_evaluation_history(site_id):
    """
    Get evaluation history for a specific site
    
    Example: GET /api/site/123/history
    
    Response:
    {
        "success": true,
        "site_id": 123,
        "total_evaluations": 5,
        "history": [
            {
                "evaluation_id": 1001,
                "score": 0.8756,
                "rank": 1,
                "algorithm": "TOPSIS",
                "strategy_name": "Phủ Sóng Thị Trường",
                "evaluated_by": "John Doe",
                "evaluation_date": "2026-01-17T14:30:22",
                "batch_id": "TOPSIS_20260117_143022_a1b2c3d4"
            },
            ...
        ]
    }
    """
    try:
        service = AnalysisService()
        result = service.get_site_evaluation_history(site_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting site history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analysis_bp.route('/results/<int:evaluation_id>', methods=['GET'])
def get_evaluation_result(evaluation_id):
    """
    Get a specific evaluation result by ID
    
    Example: GET /api/results/1001
    """
    # TODO: Implement this endpoint if needed
    return jsonify({
        'message': 'Feature not implemented yet',
        'evaluation_id': evaluation_id
    }), 501
