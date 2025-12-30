from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class BaseAlgorithm(ABC):
    """Abstract base class for MCDM algorithms"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, weights: dict, 
                cost_criteria: list, benefit_criteria: list) -> pd.DataFrame:
        """
        Run the MCDM algorithm
        
        Args:
            data: DataFrame containing decision matrix
            weights: Dictionary of weights for each criterion
            cost_criteria: List of cost criterion names (lower is better)
            benefit_criteria: List of benefit criterion names (higher is better)
        
        Returns:
            DataFrame with added columns: 'score', 'rank_position'
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, data: pd.DataFrame, weights: dict,
                       cost_criteria: list, benefit_criteria: list) -> bool:
        """Validate input data and parameters"""
        pass

