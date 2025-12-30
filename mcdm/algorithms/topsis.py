import pandas as pd
import numpy as np
from .base_algorithm import BaseAlgorithm

class TopsisAlgorithm(BaseAlgorithm):
    """
    TOPSIS: Technique for Order Preference by Similarity to Ideal Solution
    """
    
    def __init__(self):
        super().__init__('TOPSIS')
    
    def validate_inputs(self, data: pd.DataFrame, weights: dict,
                       cost_criteria: list, benefit_criteria: list) -> bool:
        """Validate TOPSIS inputs"""
        
        # Check if data is not empty
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        # Check if all criteria are present in weights
        all_criteria = cost_criteria + benefit_criteria
        for criterion in all_criteria:
            if criterion not in weights:
                raise ValueError(f"Weight not found for criterion: {criterion}")
            if criterion not in data.columns:
                raise ValueError(f"Criterion not found in data: {criterion}")
        
        # Check if weights sum to 1.0
        total_weight = sum(weights[c] for c in all_criteria)
        if not np.isclose(total_weight, 1.0, atol=0.01):
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        return True
    
    def analyze(self, data: pd.DataFrame, weights: dict,
                cost_criteria: list, benefit_criteria: list) -> pd.DataFrame:
        """
        Run TOPSIS analysis
        """
        
        # Validate inputs
        self.validate_inputs(data, weights, cost_criteria, benefit_criteria)
        
        # Create a copy to avoid modifying original data
        df = data.copy()
        
        # Get all criteria in order
        all_criteria = cost_criteria + benefit_criteria
        
        # Step 1: Extract decision matrix
        decision_matrix = df[all_criteria].values
        
        # Step 2: Normalize the decision matrix (Vector Normalization)
        norm_matrix = self._normalize_matrix(decision_matrix)
        
        # Step 3: Calculate weighted normalized matrix
        weights_array = np.array([weights[c] for c in all_criteria])
        weighted_matrix = norm_matrix * weights_array
        
        # Step 4: Determine ideal and negative-ideal solutions
        ideal_best, ideal_worst = self._get_ideal_solutions(
            weighted_matrix,
            len(cost_criteria),
            len(benefit_criteria)
        )
        
        # Step 5: Calculate separation measures
        dist_to_best = self._calculate_distance(weighted_matrix, ideal_best)
        dist_to_worst = self._calculate_distance(weighted_matrix, ideal_worst)
        
        # Step 6: Calculate relative closeness to ideal solution
        scores = dist_to_worst / (dist_to_best + dist_to_worst)
        
        # Add scores and ranks to dataframe
        df['topsis_score'] = scores
        df['rank_position'] = pd.Series(scores).rank(ascending=False, method='min').astype(int)
        
        return df
    
    def _normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Vector normalization"""
        return matrix / np.sqrt((matrix ** 2).sum(axis=0))
    
    def _get_ideal_solutions(self, weighted_matrix: np.ndarray,
                            n_cost: int, n_benefit: int) -> tuple:
        """
        Get ideal best (A+) and ideal worst (A-) solutions
        """
        ideal_best = np.zeros(weighted_matrix.shape[1])
        ideal_worst = np.zeros(weighted_matrix.shape[1])
        
        # For cost criteria (first n_cost columns): min is best
        if n_cost > 0:
            ideal_best[:n_cost] = weighted_matrix[:, :n_cost].min(axis=0)
            ideal_worst[:n_cost] = weighted_matrix[:, :n_cost].max(axis=0)
        
        # For benefit criteria (remaining columns): max is best
        if n_benefit > 0:
            ideal_best[n_cost:] = weighted_matrix[:, n_cost:].max(axis=0)
            ideal_worst[n_cost:] = weighted_matrix[:, n_cost:].min(axis=0)
        
        return ideal_best, ideal_worst
    
    def _calculate_distance(self, matrix: np.ndarray, ideal: np.ndarray) -> np.ndarray:
        """Calculate Euclidean distance from each alternative to ideal solution"""
        return np.sqrt(((matrix - ideal) ** 2).sum(axis=1))
