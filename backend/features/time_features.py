import pandas as pd

df = pd.read_csv("../../data/blinkit-dataset/blinkit-master-data-eda-mk-251224.csv")

def add_time_features(df):
    df = df.copy()

    df['order_date'] = pd.to_datetime(df['order_date'])

    df['day_of_week'] = df['order_date'].dt.day_of_week
    df['month'] = df['order_date'].dt.month

    df = pd.get_dummies(
        df,
        columns=['day_of_week', 'month'],
        drop_first=True
    )

    return df
