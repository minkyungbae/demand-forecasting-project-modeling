from typing import Dict

class WeightCalculator:
    """가중치 계산기"""
    
    def calculate(self, correlations: Dict[str, float]) -> Dict[str, float]:
        """상관계수 기반 가중치 계산"""
        if not correlations:
            return {}
        
        # 절댓값 사용
        abs_correlations = {k: abs(v) for k, v in correlations.items()}
        
        # 정규화 (합이 1이 되도록)
        total = sum(abs_correlations.values())
        if total > 0:
            weights = {k: v/total for k, v in abs_correlations.items()}
        else:
            # 모든 상관계수가 0인 경우 균등 분배
            weights = {k: 1/len(abs_correlations) for k in abs_correlations.keys()}
        
        return weights

