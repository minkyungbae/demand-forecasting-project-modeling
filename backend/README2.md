# ForeCastly Backend

FastAPI + MongoDB를 사용한 수요 예측 및 분석 백엔드 API

## 🚀 빠른 시작 (Docker 사용)

```bash
# 1. MongoDB 시작 (Docker)
docker-compose up -d

# 2. 환경 변수 설정 (선택사항)
# .env 파일이 없으면 기본값 사용 (mongodb://localhost:27017)
# 로컬 MongoDB가 없으면 자동으로 Docker MongoDB 사용
cp .env.example .env

# 3. 의존성 설치 및 서버 실행
pip install -r requirements.txt
python run.py
```

**참고**: 
- 로컬 MongoDB가 설치되어 있으면 로컬 MongoDB 사용
- 로컬 MongoDB가 없으면 Docker MongoDB 자동 사용
- MongoDB Compass가 없어도 mongo-express (`http://localhost:8081`)로 데이터 확인 가능

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Windows CMD
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate

# PowerShell 실행 정책 오류가 발생하면:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값들을 설정하세요.

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정:
- `MONGODB_URL`: MongoDB 연결 URL
- `SECRET_KEY`: JWT 토큰 암호화를 위한 시크릿 키
- `CORS_ORIGINS`: 허용할 CORS 오리진 (쉼표로 구분)

### 3. MongoDB 실행

#### 방법 1: Docker Compose 사용 (권장)

```bash
# Docker Compose로 MongoDB 실행
docker compose up -d

# MongoDB 상태 확인
docker compose ps

# MongoDB 로그 확인
docker compose logs mongodb

# MongoDB 중지
docker compose down

# 데이터까지 삭제하며 중지
docker compose down -v
```

Docker Compose를 사용하면:
- MongoDB가 자동으로 시작됩니다 (인증 없이 사용 가능)
- MongoDB Express (웹 UI)가 `http://localhost:8081`에서 실행됩니다
  - 인증 없이 바로 사용 가능
- 데이터는 영구 저장됩니다 (볼륨 사용)

`.env`에서 `MONGODB_URL=mongodb://localhost:27017`로 설정하세요.

#### 방법 2: 로컬 MongoDB 사용

로컬에 MongoDB가 설치되어 있다면:

```bash
# MongoDB 시작 (로컬)
mongod
```

`.env` 파일에서 `MONGODB_URL=mongodb://localhost:27017`로 설정하세요.

### 4. 서버 실행

```bash
python run.py
```

또는

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 `http://localhost:8000`에서 API를 사용할 수 있습니다.

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🗂️ 프로젝트 구조

```
app/
├── api/                    # API 라우터
│   └── v1/                # API v1
│       ├── auth.py        # 인증
│       ├── users.py       # 유저
│       ├── files.py       # 파일
│       ├── visualizations.py  # 시각화
│       ├── correlations.py    # 상관관계
│       ├── predictions.py     # 예측
│       └── solutions.py       # 솔루션
├── core/                  # 핵심 설정
│   ├── config.py          # 설정
│   ├── database.py        # MongoDB 연결
│   ├── security.py        # 보안 (JWT, 비밀번호)
│   └── exceptions.py      # 커스텀 예외
├── models/                # Pydantic 모델
├── services/              # 비즈니스 로직
│   ├── auth/             # 인증 서비스
│   ├── user/             # 유저 서비스
│   ├── file/             # 파일 서비스
│   ├── visualization/    # 시각화 서비스
│   ├── correlation/      # 상관관계 서비스
│   ├── prediction/       # 예측 서비스
│   └── solution/         # 솔루션 서비스
└── utils/                # 유틸리티
```

## 🔑 주요 기능

### 인증 (Auth)
- 회원가입
- 로그인
- JWT 토큰 기반 인증

### 파일 관리 (Files)
- CSV 파일 업로드
- 파일 목록 조회
- CSV 데이터 조회 (페이지네이션)

### 시각화 (Visualizations)
- 다양한 차트 타입 지원 (line, bar, scatter, heatmap 등)
- 차트 이미지 생성 (Base64)

### 상관관계 분석 (Correlations)
- 피처 간 상관계수 계산
- 가중치 계산
- 상관관계 시각화

### 예측 (Predictions)
- 머신러닝 모델 학습 (Linear, Random Forest 등)
- 시계열 예측
- 모델 성능 지표 제공

### 솔루션 (Solutions)
- LLM 기반 인사이트 생성
- 추천사항 제공

## 🧪 테스트

```bash
pytest
```

## 📝 환경 변수 설명

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `MONGODB_URL` | MongoDB 연결 URL | `mongodb://localhost:27017` |
| `DATABASE_NAME` | 데이터베이스 이름 | `forecastly` |
| `SECRET_KEY` | JWT 토큰 암호화 키 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 (분) | `30` |
| `CORS_ORIGINS` | 허용할 CORS 오리진 | `http://localhost:3000,http://localhost:8000` |
| `OPENROUTER_API_KEY` | OpenRouter API 키 (선택) | - |
| `OPENROUTER_BASE_URL` | OpenRouter API URL | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | 사용할 LLM 모델 | `openai/gpt-4o-mini` |

### Docker Compose MongoDB 설정

`docker-compose.yml`에서 MongoDB 설정:
- **인증**: 없음 (개발 환경용)
- **포트**: `27017`
- **웹 UI (MongoDB Express)**: `http://localhost:8081`
  - 인증 없이 바로 사용 가능

프로덕션 환경에서는 반드시 인증을 설정하세요!

## 🔒 보안

- 비밀번호는 bcrypt로 해싱됩니다
- JWT 토큰을 사용한 인증
- CORS 설정으로 허용된 오리진만 접근 가능

## 📦 의존성

주요 의존성:
- `fastapi`: 웹 프레임워크
- `motor`: MongoDB 비동기 드라이버
- `pydantic`: 데이터 검증
- `pandas`: 데이터 처리
- `scikit-learn`: 머신러닝
- `plotly`: 시각화

전체 의존성 목록은 `requirements.txt`를 참고하세요.

## 🤝 기여

이슈나 풀 리퀘스트를 환영합니다!

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

