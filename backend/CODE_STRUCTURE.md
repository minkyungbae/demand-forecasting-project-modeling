# 코드 구조 및 기능 정리

## 📋 주요 API 엔드포인트

### 1. 인증 (Auth)
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인

### 2. 사용자 (Users)
- `GET /api/v1/users/me` - 현재 사용자 정보 조회
- `GET /api/v1/users/{user_id}` - 특정 사용자 정보 조회

### 3. 파일 관리 (Files)
- `POST /api/v1/files/upload` - CSV 파일 업로드
- `GET /api/v1/files/` - 파일 목록 조회
- `GET /api/v1/files/{file_id}` - 파일 상세 정보 조회
- `POST /api/v1/files/{file_id}/data` - CSV 데이터 조회 (페이지네이션)
- `GET /api/v1/files/{file_id}/columns` - 컬럼 목록 조회
- `DELETE /api/v1/files/{file_id}` - 파일 삭제

### 4. 전체 분석 (Analysis) - 자동화
- `POST /api/v1/analysis/start` - 전체 분석 작업 시작 (예측 피처 선택 후)
- `GET /api/v1/analysis/{task_id}` - 작업 진행 상황 조회
- `GET /api/v1/analysis/{task_id}/result` - 작업 결과 조회 (완료된 경우)
- `GET /api/v1/analysis/{task_id}/statistics` - 통계 분석 결과 조회
- `GET /api/v1/analysis/{task_id}/visualizations` - 시각화 결과 조회
- `GET /api/v1/analysis/{task_id}/correlation` - 상관관계 분석 결과 조회
- `GET /api/v1/analysis/{task_id}/prediction` - 예측 결과 조회
- `GET /api/v1/analysis/{task_id}/solution` - 솔루션 결과 조회
- `GET /api/v1/analysis/file/{file_id}/latest` - 파일의 최신 분석 결과 조회

## 🗄️ MongoDB 컬렉션

1. **users** - 사용자 정보
2. **sales** - 파일 메타데이터
3. **csv** - CSV 데이터 (행별 저장)
4. **file_analysis_config** - 파일 분석 설정 (컬럼 추천 결과, 제품별 개수, 타입별 개수)
5. **analysis_tasks** - 분석 작업 상태 관리 (백그라운드 작업 추적)
6. **statistics** - 통계 분석 결과 (LLM 설명 포함)
7. **correlations** - 상관관계 분석 결과
8. **feature_weights** - 피처 가중치
9. **analysis_results** - 분석 결과
10. **predictions** - 예측 결과
11. **visualizations** - 시각화 결과 (선그래프, 막대그래프)
12. **solutions** - AI 솔루션 결과

## 📊 백그라운드 분석 파이프라인

1. **관련 컬럼 추천** (LLM) → `file_analysis_config` 저장
2. **통계 분석** (기본 통계 + LLM 설명) → `statistics` 저장
3. **시각화 생성** (상품별 선그래프, 막대그래프) → `visualizations` 저장
4. **상관관계 분석** (전체, 상품별) → `correlations` 저장
5. **예측 모델링** (여러 모델 비교) → `predictions` 저장
6. **솔루션 생성** (LLM 인사이트) → `solutions` 저장

각 단계는 `analysis_tasks`에서 상태를 추적하며, 각 단계별로 개별 조회 API 제공

