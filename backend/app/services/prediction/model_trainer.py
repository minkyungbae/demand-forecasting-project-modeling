from typing import List, Dict, Tuple
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np

class ModelTrainer:
    """모델 학습기"""
    
    async def train_model(
        self,
        data: List[Dict],
        target_column: str,
        features: List[str],
        model_type: str = "linear"
    ) -> Tuple[object, Dict[str, float]]:
        """모델 학습"""
        df = pd.DataFrame(data)
        
        # 피처 전처리: 날짜 및 범주형 컬럼 처리
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
        X = X_processed.fillna(0)
        y = pd.to_numeric(df[target_column], errors='coerce').fillna(0)
        
        # 모델 선택
        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            model = LinearRegression()
        
        # 학습
        model.fit(X, y)
        
        # 예측 및 평가
        y_pred = model.predict(X)
        metrics = {
            'mse': float(mean_squared_error(y, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y, y_pred))),
            'mae': float(mean_absolute_error(y, y_pred)),
            'r2': float(r2_score(y, y_pred))
        }
        
        return model, metrics

