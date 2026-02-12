from datetime import datetime
import pandas as pd
from utils.db_connector import get_db_connection
import logging
import uuid

logger = logging.getLogger(__name__)

class DataService:
    """Service for data loading and saving operations"""
    
    def load_config(self, config_id: int = None) -> dict:
        """
        Load expert criteria configuration
        
        Args:
            config_id: Configuration ID (None = load active config)
        
        Returns:
            Dictionary with configuration data
        """
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if config_id:
                query = """
                    SELECT * FROM expert_criteria_config 
                    WHERE id = %s
                """
                cursor.execute(query, (config_id,))
            else:
                query = """
                    SELECT * FROM expert_criteria_config 
                    WHERE is_active = TRUE 
                    LIMIT 1
                """
                cursor.execute(query)
            
            config = cursor.fetchone()
            
            if not config:
                raise ValueError("No configuration found")
            
            return config
            
        finally:
            cursor.close()
            conn.close()
    
    def load_sites(self) -> pd.DataFrame:
        """
        Load potential sites from database
        
        Returns:
            DataFrame with site data
        """
        
        query = """
            SELECT 
                id, site_code, address,
                rent_cost, renovation_cost, competitor_count, distance_to_warehouse,
                floor_area, front_width, traffic_score, population_density
            FROM potential_site
            WHERE status = 'ACTIVE'
        """
        
        conn = get_db_connection()
        
        try:
            df = pd.read_sql(query, conn)
            logger.info(f"Loaded {len(df)} active sites from database")
            return df
        finally:
            conn.close()
    
    def save_results(self, df: pd.DataFrame, config_id: int, 
                    user_id: int = None, algorithm: str = 'TOPSIS',
                    execution_time_ms: int = None):
        """
        Save analysis results to evaluation_result table
        
        Args:
            df: DataFrame with results (must have topsis_score and rank_position)
            config_id: Configuration ID used for analysis
            user_id: User who performed the analysis (optional)
            algorithm: Algorithm used (default: TOPSIS)
            execution_time_ms: Execution time in milliseconds
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Generate unique batch_id for this analysis run
            batch_id = f"{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"Saving {len(df)} evaluation results with batch_id: {batch_id}")
            
            insert_query = """
                INSERT INTO evaluation_result 
                (user_id, config_id, site_id, algorithm_used, 
                 topsis_score, rank_position, created_at, 
                 execution_time_ms, batch_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            insert_count = 0
            for _, row in df.iterrows():
                values = (
                    user_id,  # Can be NULL
                    config_id,
                    int(row['id']),
                    algorithm,
                    float(row['topsis_score']),
                    int(row['rank_position']),
                    current_time,
                    execution_time_ms,
                    batch_id
                )
                cursor.execute(insert_query, values)
                insert_count += 1
            
            conn.commit()
            logger.info(f"Successfully inserted {insert_count} records into evaluation_result table")
            logger.info(f"Batch ID: {batch_id}")
            
            return batch_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving evaluation results: {str(e)}", exc_info=True)
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_latest_batch_results(self, limit: int = 10) -> pd.DataFrame:
        """
        Get top N results from the latest analysis batch
        
        Args:
            limit: Number of top results to return
            
        Returns:
            DataFrame with top results
        """
        
        query = """
            SELECT 
                er.rank_position,
                ps.site_code,
                ps.address,
                d.name as district_name,
                er.topsis_score,
                ps.rent_cost,
                ps.floor_area,
                ps.traffic_score,
                ps.competitor_count,
                ec.strategy_name,
                er.created_at as analysis_date,
                er.algorithm_used
            FROM evaluation_result er
            INNER JOIN (
                SELECT MAX(batch_id) as latest_batch 
                FROM evaluation_result
            ) lb ON er.batch_id = lb.latest_batch
            LEFT JOIN potential_site ps ON er.site_id = ps.id
            LEFT JOIN district d ON ps.district_id = d.id
            LEFT JOIN expert_criteria_config ec ON er.config_id = ec.id
            ORDER BY er.rank_position ASC
            LIMIT %s
        """
        
        conn = get_db_connection()
        
        try:
            df = pd.read_sql(query, conn, params=(limit,))
            return df
        finally:
            conn.close()
    
    def get_evaluation_history_by_site(self, site_id: int) -> pd.DataFrame:
        """
        Get evaluation history for a specific site
        
        Args:
            site_id: Site ID
            
        Returns:
            DataFrame with evaluation history
        """
        
        query = """
            SELECT 
                er.*,
                ec.strategy_name,
                u.full_name as evaluated_by
            FROM evaluation_result er
            LEFT JOIN expert_criteria_config ec ON er.config_id = ec.id
            LEFT JOIN users u ON er.user_id = u.id
            WHERE er.site_id = %s
            ORDER BY er.created_at DESC
        """
        
        conn = get_db_connection()
        
        try:
            df = pd.read_sql(query, conn, params=(site_id,))
            return df
        finally:
            conn.close()
    
    def get_batch_statistics(self, batch_id: str) -> dict:
        """
        Get statistics for a specific batch
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Dictionary with statistics
        """
        
        query = """
            SELECT 
                COUNT(*) as total_sites,
                MIN(topsis_score) as min_score,
                MAX(topsis_score) as max_score,
                AVG(topsis_score) as avg_score,
                STDDEV(topsis_score) as std_score,
                algorithm_used,
                created_at,
                execution_time_ms
            FROM evaluation_result
            WHERE batch_id = %s
            GROUP BY algorithm_used, created_at, execution_time_ms
        """
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(query, (batch_id,))
            result = cursor.fetchone()
            return result if result else {}
        finally:
            cursor.close()
            conn.close()
            