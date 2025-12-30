from dataclasses import dataclass
from typing import Optional, List, Dict



@dataclass
class SiteResult:
    """Single site result model"""
    rank: int
    site_code: str
    address: str
    score: float
    rent_cost: float
    floor_area: float
    traffic_score: int
    competitor_count: int


@dataclass
class AnalysisResponse:
    """Analysis response model"""
    success: bool
    algorithm: str
    strategy_name: str
    sites_analyzed: int
    execution_time_seconds: float
    timestamp: str
    score_statistics: Dict[str, float]
    top_sites: List[SiteResult]
    error: Optional[str] = None
