# 수요 예측 모델 개발
---
- 사용한 모델 : RandomForest, ARIMA, RandomForest + ARIMA, LSTM,  RandomForest + ARIMA + LSTM, Boosting(XGboost, LightGBM)
- 최종 선택한 모델 : RandomForest + ARIMA
- 사용하는 데이터셋 : [Blinkit Sales Dataset]("https://www.kaggle.com/datasets/akxiit/blinkit-sales-dataset?select=blinkit_order_items.csv")
- 사용하는 API : Open-Meteo(날씨 정보 데이터)
---
## 데이터셋 개요
- 제품 상세 정보, 주문 수량, 매출액, 타임스탬프 등 Blinkit의 판매 데이터가 포함되어 있습니다.
- 온라인 식료품 쇼핑에서 고객 행동 및 계절적 변동을 이해하는 데 도움이 됩니다.
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
## 폴더 구조
```
demand-forecasting-project-modeling  
├─ README.md
├─ backend/
│  ├─ app/                       # 메인 백엔드 로직
│  ├─ scripts/                   # 관리자 계정 설정
│  ├─ tests/                     # 백엔드 테스트 폴더
├─ documents/                    # React 프로젝트 생성 명령어 기록
├─ frontend/                     # 수요 예측 프로젝트의 프론트엔드 (React + Vite) -> TypeScript 문법(.tsx)
│  ├─ ⭐️ **src**/                # 실제 React 소스 코드 루트 ⭐️
│  │  ├─ App.css                 # App 컴포넌트 전역 스타일
│  │  ├─ ⭐️ **App.tsx**          # 전체 화면 흐름을 제어하는 최상위 컴포넌트 ⭐️
│  │  ├─ ⭐️ **components/**      # 화면 단위 / 재사용 UI 컴포넌트 모음 ⭐️
│  │  │  ├─ DashboardLayout.tsx  # 사이드바 + 메인 영역 공통 레이아웃
│  │  │  ├─ DataDashboard.tsx    # 수요 예측 결과 그래프/차트 화면
│  │  │  ├─ FileUpload.tsx       # CSV 등 데이터 파일 업로드 컴포넌트
│  │  │  ├─ IntroView.tsx        # 첫 진입 화면(서비스 소개)
│  │  │  ├─ LoginView.tsx        # 로그인 화면
│  │  │  ├─ Sidebar.tsx          # 좌측 네비게이션 사이드바
│  │  │  ├─ SignupView.tsx       # 회원가입 화면
│  │  │  └─ SolutionView.tsx     # 모델 분석 결과/솔루션 설명 화면
│  │  ├─ ⭐️ **services/**        # 외부 API 통신 로직 관리 ⭐️
│  │  │  └─ ⭐️ **api.ts**        # 백엔드 서버와 통신하는 API 함수 모음 ⭐️
│  │  └─ ⭐️ **types.ts**         # 공통 TypeScript 타입 정의 ⭐️
└─ requirements.txt

```