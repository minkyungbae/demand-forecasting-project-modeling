from typing import List
import pandas as pd

def validate_csv_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """CSV 컬럼 검증"""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"필수 컬럼이 없습니다: {', '.join(missing_columns)}")
    return True

def validate_numeric_column(df: pd.DataFrame, column: str) -> bool:
    """숫자형 컬럼 검증"""
    if column not in df.columns:
        raise ValueError(f"컬럼 {column}을 찾을 수 없습니다")
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"컬럼 {column}은 숫자형이어야 합니다")
    return True

