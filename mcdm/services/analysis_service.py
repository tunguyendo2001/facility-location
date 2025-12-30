from datetime import datetime
from algorithms import AlgorithmFactory
from services.data_service import DataService
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service to orchestrate MCDM analysis"""
    
    def __init__(self):
        self.data_service = DataService()
    
    def run_analysis(self, algorithm: str = 'topsis', 
                    config_id: int = None, top_n: int = 10) -> dict:
        """
        Run MCDM analysis
        
        Args:
            algorithm: Algorithm name (topsis, ahp, etc.)
            config_id: Expert criteria configuration ID (None = use active config)
            top_n: Number of top results to return
        
        Returns:
            Dictionary with analysis results
        """
        
        start_time = datetime.now()
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
            
            # Step 5: Save results to database
            self.data_service.save_results(df_results, config['id'])
            logger.info("Results saved to database")
            
            # Step 6: Prepare response
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Get top N results
            top_sites = df_results.nsmallest(top_n, 'rank_position')
            
            response = {
                'success': True,
                'algorithm': algorithm,
                'strategy_name': config['strategy_name'],
                'sites_analyzed': len(df_results),
                'execution_time_seconds': round(duration, 2),
                'timestamp': end_time.isoformat(),
                'score_statistics': {
                    'min': float(df_results['topsis_score'].min()),
                    'max': float(df_results['topsis_score'].max()),
                    'mean': float(df_results['topsis_score'].mean()),
                    'std': float(df_results['topsis_score'].std())
                },
                'top_sites': [
                    {
                        'rank': int(row['rank_position']),
                        'site_code': row['site_code'],
                        'address': row['address'],
                        'score': float(row['topsis_score']),
                        'rent_cost': float(row['rent_cost']),
                        'floor_area': float(row['floor_area']),
                        'traffic_score': int(row['traffic_score']),
                        'competitor_count': int(row['competitor_count'])
                    }
                    for _, row in top_sites.iterrows()
                ]
            }
            
            logger.info(f"Analysis completed in {duration:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise

