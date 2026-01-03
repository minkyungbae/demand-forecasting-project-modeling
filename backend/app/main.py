from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, files, analysis, predictions, correlations, solutions, visualizations, features, statistics
from app.core.config import settings
from app.core.database import init_db, close_db

app = FastAPI(
    title="ForeCastly Analytics API",
    version="1.0.0",
    description="수요 예측 및 분석 API"
)


# CORS 설정
# 개발 환경: 모든 주소 허용 (다른 PC에서 접근 가능)
# 프로덕션에서는 .env의 CORS_ORIGINS에 특정 주소만 설정하세요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경: 모든 주소 허용
    allow_credentials=False,  # allow_origins=["*"]일 때는 False여야 함
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["인증"])
app.include_router(users.router, prefix="/users", tags=["사용자"])
app.include_router(files.router, prefix="/files", tags=["파일 관리"])
app.include_router(features.router, prefix="/features", tags=["컬럼 추천"])
app.include_router(statistics.router, prefix="/statistics", tags=["통계 분석"])
app.include_router(analysis.router, prefix="/analysis", tags=["전체 분석 (자동)"])
app.include_router(predictions.router, prefix="/predictions", tags=["예측"])
app.include_router(correlations.router, prefix="/correlations", tags=["상관관계"])
app.include_router(solutions.router, prefix="/solutions", tags=["솔루션"])
app.include_router(visualizations.router, prefix="/visualizations", tags=["시각화"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "ForeCastly Analytics API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

