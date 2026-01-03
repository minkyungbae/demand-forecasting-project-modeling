from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from app.services.file.file_repository import FileRepository
from app.services.solution.llm_service import LLMService
from app.core.database import get_database

class StatisticsService:
    """통계 분석 서비스"""
    
    def __init__(self):
        self.file_repository = FileRepository()
        self.llm_service = LLMService()
    
    async def generate_statistics(
        self,
        file_id: str,
        user_id: str,
        target_column: str,
        group_by_column: Optional[str] = None
    ) -> Dict:
        """통계 분석 생성 (LLM 설명 포함)"""
        # 데이터 로드
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        if not data:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        # get_csv_data는 이미 data 필드만 반환 (List[Dict])
        df = pd.DataFrame(data)
        
        # 기본 통계 계산
        statistics = self._calculate_statistics(df, target_column, group_by_column)
        
        # LLM으로 설명 생성
        llm_explanation = await self._generate_statistics_explanation(
            file_id, target_column, statistics, group_by_column
        )
        
        return {
            'statistics': statistics,
            'llm_explanation': llm_explanation,
            'group_by_column': group_by_column
        }
    
    def _calculate_statistics(
        self,
        df: pd.DataFrame,
        target_column: str,
        group_by_column: Optional[str] = None
    ) -> Dict:
        """기본 통계 계산"""
        if target_column not in df.columns:
            raise ValueError(f"컬럼 '{target_column}'을 찾을 수 없습니다")
        
        target_series = pd.to_numeric(df[target_column], errors='coerce')
        
        if group_by_column and group_by_column in df.columns:
            # 그룹별 통계
            grouped_stats = {}
            for group_value in df[group_by_column].unique():
                group_data = target_series[df[group_by_column] == group_value].dropna()
                if len(group_data) > 0:
                    grouped_stats[str(group_value)] = {
                        'count': int(len(group_data)),
                        'mean': float(group_data.mean()),
                        'median': float(group_data.median()),
                        'std': float(group_data.std()) if len(group_data) > 1 else 0.0,
                        'min': float(group_data.min()),
                        'max': float(group_data.max()),
                        'sum': float(group_data.sum())
                    }
            
            return {
                'overall': {
                    'count': int(len(target_series.dropna())),
                    'mean': float(target_series.mean()),
                    'median': float(target_series.median()),
                    'std': float(target_series.std()) if len(target_series.dropna()) > 1 else 0.0,
                    'min': float(target_series.min()),
                    'max': float(target_series.max()),
                    'sum': float(target_series.sum())
                },
                'by_group': grouped_stats
            }
        else:
            # 전체 통계
            target_clean = target_series.dropna()
            return {
                'overall': {
                    'count': int(len(target_clean)),
                    'mean': float(target_clean.mean()),
                    'median': float(target_clean.median()),
                    'std': float(target_clean.std()) if len(target_clean) > 1 else 0.0,
                    'min': float(target_clean.min()),
                    'max': float(target_clean.max()),
                    'sum': float(target_clean.sum())
                }
            }
    
    async def _generate_statistics_explanation(
        self,
        file_id: str,
        target_column: str,
        statistics: Dict,
        group_by_column: Optional[str]
    ) -> str:
        """LLM으로 통계 설명 생성"""
        overall = statistics.get('overall', {})
        by_group = statistics.get('by_group', {})
        
        # LLM에게 전달할 프롬프트 구성
        prompt_parts = [f"다음은 '{target_column}' 컬럼에 대한 통계 분석 결과입니다.\n\n"]
        
        prompt_parts.append("## 전체 통계\n")
        prompt_parts.append(f"- 데이터 개수: {overall.get('count', 0):,}개\n")
        prompt_parts.append(f"- 평균: {overall.get('mean', 0):.2f}\n")
        prompt_parts.append(f"- 중앙값: {overall.get('median', 0):.2f}\n")
        prompt_parts.append(f"- 표준편차: {overall.get('std', 0):.2f}\n")
        prompt_parts.append(f"- 최솟값: {overall.get('min', 0):.2f}\n")
        prompt_parts.append(f"- 최댓값: {overall.get('max', 0):.2f}\n")
        prompt_parts.append(f"- 합계: {overall.get('sum', 0):,.2f}\n")
        
        if by_group and group_by_column:
            prompt_parts.append(f"\n## {group_by_column}별 통계 (상위 5개)\n")
            # 그룹별 평균으로 정렬하여 상위 5개만 표시
            sorted_groups = sorted(
                by_group.items(),
                key=lambda x: x[1].get('mean', 0),
                reverse=True
            )[:5]
            
            for group_name, group_stats in sorted_groups:
                prompt_parts.append(f"### {group_name}\n")
                prompt_parts.append(f"- 개수: {group_stats.get('count', 0):,}개\n")
                prompt_parts.append(f"- 평균: {group_stats.get('mean', 0):.2f}\n")
                prompt_parts.append(f"- 중앙값: {group_stats.get('median', 0):.2f}\n")
        
        prompt_parts.append("\n위 통계 결과를 분석하여 다음 내용을 한국어로 설명해주세요:\n")
        prompt_parts.append("1. 전체 데이터의 주요 특징 (평균, 분산 등)\n")
        prompt_parts.append("2. 그룹별 차이점이 있다면 무엇인지\n")
        prompt_parts.append("3. 데이터의 분포 특성 (정규분포인지, 편향되어 있는지 등)\n")
        prompt_parts.append("4. 비즈니스 관점에서의 인사이트\n")
        prompt_parts.append("간결하고 명확하게 작성해주세요. (200자 이내)")
        
        prompt = "".join(prompt_parts)
        
        # LLM 서비스를 통해 설명 생성 (OpenRouter API 키가 있으면)
        try:
            explanation = await self.llm_service._generate_statistics_explanation_with_llm(prompt)
            return explanation
        except Exception as e:
            print(f"⚠️ LLM 설명 생성 실패: {str(e)}, 기본 텍스트 사용")
            # LLM 실패 시 기본 설명
            mean = overall.get('mean', 0)
            std = overall.get('std', 0)
            return (
                f"'{target_column}' 컬럼의 통계 분석 결과:\n"
                f"- 평균값: {mean:.2f}, 표준편차: {std:.2f}\n"
                f"- 전체 데이터 {overall.get('count', 0):,}개 분석 완료"
                + (f"\n- {group_by_column}별로 {len(by_group)}개 그룹 분석" if by_group else "")
            )

