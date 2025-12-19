# 수요 예측 모델 개발
---
- 사용하는 모델 : **LDA**
- 사용하는 데이터셋 : [Blinkit Sales Dataset]("https://www.kaggle.com/datasets/akxiit/blinkit-sales-dataset?select=blinkit_order_items.csv")
- Open-Meteo(날씨 데이터)
---
## 데이터셋 개요
- 제품 상세 정보, 주문 수량, 매출액, 타임스탬프 등 Blinkit의 판매 데이터가 포함되어 있습니다.
- 수요 예측, 가격 최적화, 추세 분석 및 비즈니스 통찰력 확보에 유용합니다.
- 온라인 식료품 쇼핑에서 고객 행동 및 계절적 변동을 이해하는 데 도움이 됩니다.

## 잠재적 활용 사례
- 시계열 분석 : 서로 다른 기간에 걸친 판매 추세를 분석
- 수요 예측 : 과거 데이터를 기반으로 미래 제품 수요를 예측
- 가격 최적화 : 가격이 매출 및 수익에 미치는 영향을 파악
- 고객 행동 분석 : 구매 패턴과 선호도를 파악
- 시장 동향 : 다양한 요인의 식료품 판매 실적에 미치는 영향
---
## 날씨 데이터
- 사용 API 👉 Open-Meteo – Archive API
- 선택한 이유
    - API Key 없이 사용 가능하다.
    - 무료이지만 제한이 없다.
        - 과거 데이터 수집에도 제한이 없다.
    - 연구/상업적 사용에도 가능하다.
---
## 폴더 구조
```
demand-forecasting-project-modeling
├─ README.md
├─ backend/
├─ blinkit-dataset/
│  └─ blinkit_master_data.csv
├─ crawling/
├─ frontend/
├─ modeling/
│  ├─ lda-model.py
│  └─ memos
│     └─ basic-LDA-pipeline.txt
└─ requirements.txt

```