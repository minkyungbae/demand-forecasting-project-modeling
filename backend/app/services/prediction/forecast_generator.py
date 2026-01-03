from typing import List, Dict
import pandas as pd
import numpy as np

class ForecastGenerator:
    """예측 생성기"""
    
    def _preprocess_features(self, df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """피처 전처리 (model_trainer와 동일한 로직)"""
        X_processed = df[features].copy()
        
        for col in features:
            if col not in X_processed.columns:
                continue
            
            # 날짜 컬럼 처리
            if pd.api.types.is_datetime64_any_dtype(X_processed[col]) or any(keyword in col.lower() for keyword in ['날짜', 'date']):
                try:
                    # 날짜를 숫자로 변환 (타임스탬프 또는 순서 인덱스)
                    if pd.api.types.is_datetime64_any_dtype(X_processed[col]):
                        X_processed[col] = pd.to_numeric(X_processed[col], errors='coerce')
                    else:
                        # 문자열 날짜를 datetime으로 변환 후 타임스탬프로
                        X_processed[col] = pd.to_datetime(X_processed[col], errors='coerce')
                        X_processed[col] = pd.to_numeric(X_processed[col], errors='coerce')
                except:
                    # 변환 실패 시 라벨 인코딩
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    X_processed[col] = le.fit_transform(X_processed[col].astype(str).fillna(''))
            
            # 범주형/문자열 컬럼 처리
            elif not pd.api.types.is_numeric_dtype(X_processed[col]):
                try:
                    # 숫자로 변환 시도
                    X_processed[col] = pd.to_numeric(X_processed[col], errors='coerce')
                    if X_processed[col].isna().sum() > len(X_processed) * 0.5:  # 50% 이상 NaN이면 라벨 인코딩
                        from sklearn.preprocessing import LabelEncoder
                        le = LabelEncoder()
                        X_processed[col] = le.fit_transform(X_processed[col].astype(str).fillna(''))
                except:
                    # 라벨 인코딩
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    X_processed[col] = le.fit_transform(X_processed[col].astype(str).fillna(''))
        
        # NaN 값 처리
        return X_processed.fillna(0)
    
    async def generate_forecast(
        self,
        model: object,
        data: List[Dict],
        target_column: str,
        features: List[str],
        periods: int
    ) -> List[Dict]:
        """예측 생성"""
        df = pd.DataFrame(data)
        
        # 피처 전처리 (학습 시와 동일한 전처리 적용)
        X_processed = self._preprocess_features(df, features)
        
        # 마지막 데이터 포인트 사용 (DataFrame으로 유지하여 feature names 보존)
        last_features = X_processed.iloc[-1:].copy()  # DataFrame으로 유지 (1행 DataFrame)
        
        # 예측 생성
        forecast_values = []
        for i in range(periods):
            # DataFrame을 그대로 전달하여 feature names 유지
            pred = model.predict(last_features)[0]
            forecast_values.append({
                'period': i + 1,
                'forecast': float(pred),
                'date': None  # 실제로는 날짜 계산 필요
            })
        
        return forecast_values

