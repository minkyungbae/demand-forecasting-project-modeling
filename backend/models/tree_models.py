from sklearn.ensemble import RandomForestRegressor

def get_tree_models():
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=200,
            random_state=42
        )
    }