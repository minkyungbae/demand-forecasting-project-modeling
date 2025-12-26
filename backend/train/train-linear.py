import pandas as pd
from sklearn.model_selection import train_test_split
from features.time_features import add_time_features
from models.linear_models import get_linear_models
from utils.metrics import evaluate

df = pd.read_csv("../../data/blinkit-dataset/blinkit_master_data_eda_mk_251224.csv")

df = add_time_features(df)

X = df.drop(columns=['daily_quantity', 'order_date'])
y = df['daily_quantity']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, shuffle=False, test_size=0.2
)

models = get_linear_models()

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    evaluate(name, y_test, preds)
