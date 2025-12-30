from datetime import datetime
import pandas as pd
from utils.db_connector import get_db_connection
import logging

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
            return df
        finally:
            conn.close()
    
    def save_results(self, df: pd.DataFrame, config_id: int):
        """
        Save analysis results to database
        
        Args:
            df: DataFrame with results (must have topsis_score and rank_position)
            config_id: Configuration ID used for analysis
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            update_query = """
                UPDATE potential_site
                SET topsis_score = %s,
                    rank_position = %s,
                    last_analysis_date = %s,
                    config_used_id = %s
                WHERE id = %s
            """
            
            for _, row in df.iterrows():
                values = (
                    float(row['topsis_score']),
                    int(row['rank_position']),
                    current_time,
                    config_id,
                    int(row['id'])
                )
                cursor.execute(update_query, values)
            
            conn.commit()
            logger.info(f"Updated {len(df)} records in database")
            
        finally:
            cursor.close()
            conn.close()
