from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class LagFeatureGenerator:
    """시계열 Lag 피처 생성기"""
    
    def __init__(self):
        pass
    
    async def generate_lag_features(
        self,
        data: List[Dict],
        date_column: str,
        target_column: str,
        numeric_columns: List[str],
        group_by_columns: List[str],
        lag_periods: List[int] = [7, 30]  # 사용되지 않음 (하위 호환성 유지)
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        시계열 4주 합산 Lag 피처 생성
        
        상품별로 그룹화하여 바로 전 주차, 2주 전, 3주 전, 4주 전의 값을 합산합니다.
        전주 데이터가 없으면 0으로 처리합니다.
        
        Args:
            data: 원본 데이터 (List[Dict])
            date_column: 날짜 컬럼명 (주차 등)
            target_column: 타겟 컬럼명 (예: "수량")
            numeric_columns: Lag 피처를 생성할 숫자형 컬럼 목록
            group_by_columns: 그룹화할 컬럼 목록 (예: ["상품명"])
            lag_periods: 사용되지 않음 (하위 호환성 유지)
        
        Returns:
            (processed_df, new_feature_columns): Lag 피처가 추가된 DataFrame과 새로 생성된 컬럼명 목록
        """
        df = pd.DataFrame(data)
        
        # 날짜 컬럼 확인
        if date_column not in df.columns:
            raise ValueError(f"날짜 컬럼 '{date_column}'을 찾을 수 없습니다")
        
        # 정렬을 위한 순서 컬럼 생성 (주차는 숫자 또는 문자열일 수 있음)
        order_column = f"_{date_column}_order"
        df[order_column] = pd.to_numeric(df[date_column], errors='coerce')
        
        # 숫자 변환이 실패한 경우 원본 값 사용 (문자열 순서)
        if df[order_column].isna().sum() > len(df) * 0.5:
            df[order_column] = df[date_column]
        
        # 그룹화 컬럼이 없으면 빈 리스트로 처리
        if not group_by_columns:
            group_by_columns = []
        
        # 그룹화 컬럼과 날짜 순서 기준으로 정렬
        sort_columns = [*group_by_columns, order_column] if group_by_columns else [order_column]
        df = df.sort_values(sort_columns)
        
        new_feature_columns = []
        
        # 각 숫자형 컬럼에 대해 4주 합산 Lag 피처 생성
        for col in numeric_columns:
            if col not in df.columns:
                continue
            
            # 숫자형으로 변환
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 4주 합산 컬럼명
            rolling_col_name = f"{col}_rolling_4weeks"
            
            if group_by_columns:
                # 그룹별로 4주 합산 계산
                rolling_values = []
                
                for group_key, group in df.groupby(group_by_columns):
                    group = group.copy().sort_values(order_column)
                    group_rolling_values = pd.Series(index=group.index, dtype=float)
                    
                    # 그룹을 리스트로 변환하여 인덱스로 접근
                    group_list = group.reset_index(drop=True)
                    original_indices = group.index.tolist()
                    
                    for i in range(len(group_list)):
                        # 바로 전 주차(1주 전), 2주 전, 3주 전, 4주 전 값 가져오기
                        values = []
                        
                        # 1주 전 (바로 전)
                        if i >= 1:
                            val_1 = group_list.loc[i-1, col]
                            values.append(val_1 if not pd.isna(val_1) else 0.0)
                        else:
                            values.append(0.0)
                        
                        # 2주 전
                        if i >= 2:
                            val_2 = group_list.loc[i-2, col]
                            values.append(val_2 if not pd.isna(val_2) else 0.0)
                        else:
                            values.append(0.0)
                        
                        # 3주 전
                        if i >= 3:
                            val_3 = group_list.loc[i-3, col]
                            values.append(val_3 if not pd.isna(val_3) else 0.0)
                        else:
                            values.append(0.0)
                        
                        # 4주 전
                        if i >= 4:
                            val_4 = group_list.loc[i-4, col]
                            values.append(val_4 if not pd.isna(val_4) else 0.0)
                        else:
                            values.append(0.0)
                        
                        # 4개 값의 합산
                        rolling_sum = sum(values)
                        group_rolling_values.loc[original_indices[i]] = rolling_sum
                    
                    rolling_values.append(group_rolling_values)
                
                # 모든 그룹의 결과를 합침
                df[rolling_col_name] = pd.concat(rolling_values).reindex(df.index)
            else:
                # 그룹화 없이 전체 데이터에서 4주 합산 계산
                df_sorted = df.sort_values(order_column).copy()
                original_indices = df_sorted.index.tolist()
                df_sorted = df_sorted.reset_index(drop=True)
                rolling_values = pd.Series(index=original_indices, dtype=float)
                
                for i in range(len(df_sorted)):
                    # 바로 전 주차(1주 전), 2주 전, 3주 전, 4주 전 값 가져오기
                    values = []
                    
                    # 1주 전 (바로 전)
                    if i >= 1:
                        val_1 = df_sorted.loc[i-1, col]
                        values.append(val_1 if not pd.isna(val_1) else 0.0)
                    else:
                        values.append(0.0)
                    
                    # 2주 전
                    if i >= 2:
                        val_2 = df_sorted.loc[i-2, col]
                        values.append(val_2 if not pd.isna(val_2) else 0.0)
                    else:
                        values.append(0.0)
                    
                    # 3주 전
                    if i >= 3:
                        val_3 = df_sorted.loc[i-3, col]
                        values.append(val_3 if not pd.isna(val_3) else 0.0)
                    else:
                        values.append(0.0)
                    
                    # 4주 전
                    if i >= 4:
                        val_4 = df_sorted.loc[i-4, col]
                        values.append(val_4 if not pd.isna(val_4) else 0.0)
                    else:
                        values.append(0.0)
                    
                    # 4개 값의 합산
                    rolling_sum = sum(values)
                    rolling_values.loc[original_indices[i]] = rolling_sum
                
                # 원래 인덱스로 재정렬
                df[rolling_col_name] = rolling_values.reindex(df.index)
            
            new_feature_columns.append(rolling_col_name)
        
        # 임시 order 컬럼 삭제
        df = df.drop(columns=[order_column])
        
        return df, new_feature_columns
    
    def find_date_column(self, columns: List[str], data_sample: List[Dict]) -> Optional[str]:
        """날짜 컬럼 자동 감지"""
        date_keywords = ['날짜', 'date', '일자', '주문일', '배송일', '생산일', 'time', '시간']
        
        # 키워드 기반 검색
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                # 실제 데이터 샘플로 날짜 형식인지 확인
                if data_sample:
                    sample_values = [row.get(col) for row in data_sample[:5] if col in row]
                    for val in sample_values:
                        if val:
                            try:
                                pd.to_datetime(str(val))
                                return col
                            except:
                                continue
        
        return None

