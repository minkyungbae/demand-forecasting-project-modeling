from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def get_tree_models():
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=200,
            random_state=42
        ),
        "XGBoost": XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            random_state=42
        )
    }
