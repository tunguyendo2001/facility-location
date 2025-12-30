from dataclasses import dataclass
from typing import Optional, List, Dict
from utils.validators import validate_algorithm, validate_top_n
from config import Config

@dataclass
class AnalysisRequest:
    """Analysis request model"""
    algorithm: str = 'topsis'
    config_id: Optional[int] = None
    top_n: int = 10
    
    def validate(self):
        """Validate request parameters"""
        if not validate_algorithm(self.algorithm):
            raise ValueError(f"Invalid algorithm: {self.algorithm}")
        
        if not validate_top_n(self.top_n):
            raise ValueError(f"Invalid top_n: {self.top_n}. Must be between 1 and {Config.TOP_RESULTS_LIMIT}")
        
        return True
