from typing import List, Dict
import pandas as pd
import numpy as np

class StatisticsCalculator:
    """통계 계산기"""
    
    def calculate_basic_stats(self, data: List[Dict], column: str) -> Dict:
        """기본 통계 계산"""
        df = pd.DataFrame(data)
        if column not in df.columns:
            raise ValueError(f"컬럼 {column}을 찾을 수 없습니다")
        
        series = df[column]
        return {
            'mean': float(series.mean()),
            'median': float(series.median()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'count': int(len(series))
        }
    
    def calculate_correlation(self, data: List[Dict], columns: List[str]) -> Dict:
        """상관계수 계산"""
        df = pd.DataFrame(data)
        subset = df[columns]
        corr_matrix = subset.corr()
        return corr_matrix.to_dict()

