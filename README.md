# 수요 예측 모델 개발
---
- 사용한 모델 : Baseline, Linear Regression, Tree models 
- 사용하는 데이터셋 : [Blinkit Sales Dataset]("https://www.kaggle.com/datasets/akxiit/blinkit-sales-dataset?select=blinkit_order_items.csv")
- 사용하는 API : Open-Meteo(날씨 정보 데이터)
---
## 데이터셋 개요
- 제품 상세 정보, 주문 수량, 매출액, 타임스탬프 등 Blinkit의 판매 데이터가 포함되어 있습니다.
- 수요 예측, 가격 최적화, 추세 분석 및 비즈니스 통찰력 확보에 유용합니다.
- 온라인 식료품 쇼핑에서 고객 행동 및 계절적 변동을 이해하는 데 도움이 됩니다.

## 잠재적 활용 사례
- 수요 예측 : 과거 데이터를 기반으로 미래 제품 수요를 예측
---
## 날씨 데이터
> 본 프로젝트에서는 Open-Meteo Archive API를 활용하여 인도 주요 도시의 2023–2024 기상 데이터를 수집하고, 일 단위 시계열 데이터를 월별로 리샘플링하여 수요 예측 모델의 외생 변수로 활용.
- 사용 API 👉 Open-Meteo – Archive API
- 선택한 이유
    - API Key 없이 사용 가능하다.
    - 무료이지만 제한이 없다.
        - 과거 데이터 수집에도 제한이 없다.
    - 연구/상업적 사용에도 가능하다.
---
## [React Component from]("https://github.com/codedthemes/mantis-free-react-admin-template")
---
## 폴더 구조
```
demand-forecasting-project-modeling
├─ README.md
├─ backend
│  ├─ API
│  │  └─ weather_api.ipynb
│  ├─ features
│  │  ├─ time_features.ipynb
│  │  └─ time_features.py
│  ├─ main.py
│  ├─ models
│  │  ├─ check
│  │  │  ├─ baseline_model_code.ipynb
│  │  │  └─ demand_code.ipynb
│  │  ├─ linear_models.py
│  │  └─ tree_models.py
│  └─ train
│     └─ train-linear.py
├─ data
├─ documents
│  └─ command.txt
├─ frontend
│  ├─ ...
│  ├─ src
│  │  ├─ ...
│  │  ├─ App.jsx
│  │  └─ ...
│  └─ ...
├─ function
│  └─ eda
│     ├─ eda_blinkit_master_data.ipynb
│     └─ eda_weather.ipynb
└─ requirements.txt

```