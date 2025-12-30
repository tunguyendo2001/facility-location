from config import Config

def validate_algorithm(algorithm: str) -> bool:
    """Validate algorithm name"""
    return algorithm.lower() in Config.SUPPORTED_ALGORITHMS


def validate_top_n(top_n: int) -> bool:
    """Validate top_n parameter"""
    return isinstance(top_n, int) and 1 <= top_n <= Config.TOP_RESULTS_LIMIT
