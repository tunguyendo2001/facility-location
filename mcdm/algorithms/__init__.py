from .base_algorithm import BaseAlgorithm
from .topsis import TopsisAlgorithm

class AlgorithmFactory:
    """Factory class to create algorithm instances"""
    
    _algorithms = {
        'topsis': TopsisAlgorithm,
        # Future algorithms can be added here:
        # 'ahp': AHPAlgorithm,
        # 'electre': ElectreAlgorithm,
        # 'promethee': PrometheeAlgorithm,
    }
    
    @classmethod
    def create(cls, algorithm_name: str) -> BaseAlgorithm:
        """Create an algorithm instance by name"""
        algorithm_name = algorithm_name.lower()
        
        if algorithm_name not in cls._algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
        
        algorithm_class = cls._algorithms[algorithm_name]
        return algorithm_class()
    
    @classmethod
    def register(cls, name: str, algorithm_class: type):
        """Register a new algorithm"""
        cls._algorithms[name.lower()] = algorithm_class
    
    @classmethod
    def get_supported_algorithms(cls) -> list:
        """Get list of supported algorithm names"""
        return list(cls._algorithms.keys())
