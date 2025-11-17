"""Chart Generation Utilities"""
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

class ChartGenerator:
    @staticmethod
    def should_visualize(user_query: str, results: List) -> bool:
        if not results or len(results) == 0:
            return False
        query_lower = user_query.lower()
        viz_keywords = ['trend', 'over time', 'chart', 'graph', 'visualize']
        return any(keyword in query_lower for keyword in viz_keywords)
    
    @staticmethod
    def create_visualization(results: List, user_query: str):
        return None  # Simplified for migration
