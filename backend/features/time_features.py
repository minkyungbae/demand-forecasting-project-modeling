import pandas as pd

# ---------- 데이터셋 불러오기 ----------
df = pd.read_csv("../../../data/blinkit-dataset/blinkit_master_data_eda_mk_251224.csv")


# ---------- order_date 타입 변경 ----------
df['order_date'] = pd.to_datetime(df['order_date'])


# ---------- 요일 feature ----------
df['day_of_week'] = df['order_date'].dt.day_of_week # 0=월요일, 6=일요일


# ---------- one-hot encoding ----------
df = pd.get_dummies(
    df,
    columns=['day_of_week'],
    drop_first=True
)


# ---------- 월 feature ----------
df['month'] = df['order_date'].dt.month

df = pd.get_dummies(
    df,
    columns=['month'],
    drop_first=True
)


# ---------- 컬럼 정의 함수 ----------
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

df.columns