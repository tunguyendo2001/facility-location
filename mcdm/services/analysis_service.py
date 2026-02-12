from datetime import datetime
from algorithms import AlgorithmFactory
from services.data_service import DataService
import logging
import time

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service to orchestrate MCDM analysis"""
    
    def __init__(self):
        self.data_service = DataService()
    
    def run_analysis(self, algorithm: str = 'topsis', 
                    config_id: int = None, 
                    user_id: int = None,
                    top_n: int = 10) -> dict:
        """
        Run MCDM analysis and save results to evaluation_result table
        
        Args:
            algorithm: Algorithm name (topsis, ahp, etc.)
            config_id: Expert criteria configuration ID (None = use active config)
            user_id: User performing the analysis (optional)
            top_n: Number of top results to return
        
        Returns:
            Dictionary with analysis results
        """
        
        start_time = datetime.now()
        start_ms = int(time.time() * 1000)
        
        logger.info(f"Starting {algorithm.upper()} analysis...")
        
        try:
            # Step 1: Load configuration
            config = self.data_service.load_config(config_id)
            logger.info(f"Loaded configuration: {config['strategy_name']}")
            
            # Step 2: Load site data
            df = self.data_service.load_sites()
            logger.info(f"Loaded {len(df)} potential sites")
            
            if len(df) == 0:
                return {
                    'success': False,
                    'error': 'No sites found to analyze',
                    'sites_analyzed': 0
                }
            
            # Step 3: Prepare criteria and weights
            cost_criteria = [
                'rent_cost', 'renovation_cost', 
                'competitor_count', 'distance_to_warehouse'
            ]
            benefit_criteria = [
                'floor_area', 'front_width', 
                'traffic_score', 'population_density'
            ]
            
            weights = {
                'rent_cost': config['weight_rent_cost'],
                'renovation_cost': config['weight_renovation_cost'],
                'competitor_count': config['weight_competitor_count'],
                'distance_to_warehouse': config['weight_warehouse_distance'],
                'floor_area': config['weight_floor_area'],
                'front_width': config['weight_front_width'],
                'traffic_score': config['weight_traffic_score'],
                'population_density': config['weight_population_density']
            }
            
            # Step 4: Run algorithm
            algo = AlgorithmFactory.create(algorithm)
            logger.info(f"Running {algo.name} algorithm...")
            
            df_results = algo.analyze(df, weights, cost_criteria, benefit_criteria)
            
            # Calculate execution time
            end_ms = int(time.time() * 1000)
            execution_time_ms = end_ms - start_ms
            
            # Step 5: Save results to evaluation_result table
            batch_id = self.data_service.save_results(
                df_results, 
                config['id'],
                user_id=user_id,
                algorithm=algorithm.upper(),
                execution_time_ms=execution_time_ms
            )
            logger.info(f"Results saved to evaluation_result table with batch_id: {batch_id}")
            
            # Step 6: Prepare response
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Get top N results
            top_sites = df_results.nsmallest(top_n, 'rank_position')
            
            response = {
                'success': True,
                'algorithm': algorithm.upper(),
                'strategy_name': config['strategy_name'],
                'batch_id': batch_id,
                'sites_analyzed': len(df_results),
                'execution_time_seconds': round(duration, 2),
                'execution_time_ms': execution_time_ms,
                'timestamp': end_time.isoformat(),
                'config_id': config['id'],
                'user_id': user_id,
                'score_statistics': {
                    'min': float(df_results['topsis_score'].min()),
                    'max': float(df_results['topsis_score'].max()),
                    'mean': float(df_results['topsis_score'].mean()),
                    'std': float(df_results['topsis_score'].std())
                },
                'top_sites': [
                    {
                        'rank': int(row['rank_position']),
                        'site_id': int(row['id']),
                        'site_code': row['site_code'],
                        'address': row['address'],
                        'score': round(float(row['topsis_score']), 4),
                        'rent_cost': float(row['rent_cost']),
                        'floor_area': float(row['floor_area']),
                        'traffic_score': int(row['traffic_score']),
                        'competitor_count': int(row['competitor_count']),
                        'population_density': float(row['population_density'])
                    }
                    for _, row in top_sites.iterrows()
                ]
            }
            
            logger.info(f"Analysis completed successfully in {duration:.2f}s")
            logger.info(f"Top site: {response['top_sites'][0]['site_code']} with score {response['top_sites'][0]['score']}")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise
    
    def get_batch_results(self, batch_id: str = None, limit: int = 10) -> dict:
        """
        Get results from a specific batch or latest batch
        
        Args:
            batch_id: Batch ID (None = get latest batch)
            limit: Number of results to return
            
        Returns:
            Dictionary with batch results
        """
        try:
            if batch_id is None:
                # Get latest batch results
                df = self.data_service.get_latest_batch_results(limit)
            else:
                # Get specific batch results
                df = self.data_service.get_latest_batch_results(limit)
                # TODO: Implement get_batch_results_by_id if needed
            
            if df.empty:
                return {
                    'success': False,
                    'error': 'No results found'
                }
            
            results = []
            for _, row in df.iterrows():
                results.append({
                    'rank': int(row['rank_position']),
                    'site_code': row['site_code'],
                    'address': row['address'],
                    'district_name': row['district_name'],
                    'score': float(row['topsis_score']),
                    'rent_cost': float(row['rent_cost']),
                    'floor_area': float(row['floor_area']),
                    'traffic_score': int(row['traffic_score']),
                    'competitor_count': int(row['competitor_count']),
                    'strategy_name': row['strategy_name'],
                    'analysis_date': row['analysis_date'].isoformat() if hasattr(row['analysis_date'], 'isoformat') else str(row['analysis_date']),
                    'algorithm_used': row.get('algorithm_used', 'TOPSIS')
                })
            
            return {
                'success': True,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error getting batch results: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_site_evaluation_history(self, site_id: int) -> dict:
        """
        Get evaluation history for a specific site
        
        Args:
            site_id: Site ID
            
        Returns:
            Dictionary with evaluation history
        """
        try:
            df = self.data_service.get_evaluation_history_by_site(site_id)
            
            if df.empty:
                return {
                    'success': False,
                    'error': 'No evaluation history found for this site'
                }
            
            history = []
            for _, row in df.iterrows():
                history.append({
                    'evaluation_id': int(row['id']),
                    'score': float(row['topsis_score']),
                    'rank': int(row['rank_position']),
                    'algorithm': row['algorithm_used'],
                    'strategy_name': row.get('strategy_name', 'N/A'),
                    'evaluated_by': row.get('evaluated_by', 'System'),
                    'evaluation_date': row['created_at'].isoformat() if hasattr(row['created_at'], 'isoformat') else str(row['created_at']),
                    'batch_id': row['batch_id']
                })
            
            return {
                'success': True,
                'site_id': site_id,
                'total_evaluations': len(history),
                'history': history
            }
            
        except Exception as e:
            logger.error(f"Error getting site evaluation history: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
        