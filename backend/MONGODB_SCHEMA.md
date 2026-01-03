# MongoDB 컬렉션 설계

## 📊 컬렉션 구조

### 1. User Collection
```javascript
{
  user_id: String,              // 중복없는 고유 식별값
  password: String,              // 해싱된 비밀번호
  email: String,                 // 예: "121212@example.com"
  user_type: String,             // "admin", "premium", "basic"
  file_upload_count: Number,      // 1, 2, 5 ...
  created_at: Date
}
```

### 2. Sales Collection
```javascript
{
  sales_id: Number,              // 1, 2, 8 ... (순차적 증가)
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  file_name: String,              // 파일 이름 (가게이름_날짜.csv)
  file_size: Number,              // 파일 크기
  columns_list: Array,            // ["컬럼1", "컬럼2", "컬럼3", ...]
  columns_type: Object,           // JSON 방식 {"컬럼명": "형태"}
  columns_count: Number,          // 전체 컬럼 총 개수 (ex: 10)
  upload_time: Date,
  upload_status: String           // "processing", "completed", "failed"
}
```

### 3. CSV Collection
```javascript
{
  csv_id: Number,                 // 1, 2, 8 ... (순차적 증가)
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  row_index: Number,               // 고유 값이 아님, 모델링 할 때 컬럼 뽑아오려고 (ex: 0~999)
  data: Object,                   // 해당 CSV 파일의 컬럼명 나열
  csv_upload_time: Date
}
```

### 4. Analysis Results Collection
```javascript
{
  results_id: String,             // 고유 식별값
  analysis_id: String,            // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  analysis_type: String,           // 분석 유형
  metrics: {
    mae: Number,                  // Mean Absolute Error
    rmse: Number,                 // Root Mean Squared Error
    r2: Number,                   // R-squared
    accuracy: Number              // 정확도 (%)
  },
  feature_count: Number,          // 피처 개수
  target_column: String,           // 타겟 컬럼명
  group_by: Array,                // ["상품명", "지역"]
  processing_time_seconds: Number, // 처리 시간 (초)
  result: Object,                  // 분석 결과 데이터
  created_at: Date
}
```

### 5. User Suggestions Collection
```javascript
{
  sug_id: String,                  // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  suggestions: Array,              // 제안 메시지 리스트
  detected_features: {
    has_amount_column: Boolean,
    has_quantity_column: Boolean,
    has_date_column: Boolean,
    categorical_columns: Array
  },
  created_at: Date
}
```

### 6. Feature Weights Collection
```javascript
{
  weight_id: String,               // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  weights: Object,                 // 피처별 가중치들 {"피처명": 가중치}
  model_metrics: Object,           // 모델 성능 지표 (선택적)
  created_at: Date
}
```

### 7. Analysis Tasks Collection
```javascript
{
  task_id: String,               // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  target_column: String,           // 예측 컬럼명
  status: String,                  // "pending", "processing", "completed", "failed"
  current_step: String,            // 현재 진행 중인 단계
  steps: {
    related_columns: { status: String, result: Object },
    statistics: { status: String, result: Object },
    visualizations: { status: String, result: Object },
    correlation: { status: String, result: Object },
    prediction: { status: String, result: Object },
    solution: { status: String, result: Object }
  },
  error_message: String,           // 오류 메시지 (있는 경우)
  created_at: Date,
  updated_at: Date
}
```

### 8. Statistics Collection
```javascript
{
  statistics_id: String,          // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  target_column: String,           // 분석한 컬럼명
  statistics: Object,              // 통계 데이터 {overall: {...}, by_group: {...}}
  llm_explanation: String,         // LLM 생성 설명
  created_at: Date
}
```

### 9. File Analysis Config Collection
```javascript
{
  config_id: String,               // 고유 식별값
  file_id: String,                // 중복없는 고유 식별값
  user_id: String,                // 중복없는 고유 식별값
  target_column: String,           // 예측 컬럼명 (예: "수량")
  related_columns: Array,          // 관련 컬럼 목록 (LLM 추천)
  excluded_columns: Array,         // 제외된 컬럼 목록 (직접 연관)
  final_columns: Array,            // 최종 컬럼 목록 (target_column + related_columns)
  group_by_column: String,         // 제품별 그룹화 컬럼 (예: "상품_ID", null 가능)
  product_counts: Object,          // 제품별 데이터 개수 {"상품A": 100, "상품B": 50}
  column_type_counts: Object,      // 컬럼 타입별 개수 {"int": 3, "varchar": 2, "date": 1, "object": 4}
  created_at: Date,
  updated_at: Date
}
```

## 🔗 컬렉션 간 관계

```
User (1) ──< (N) Sales
User (1) ──< (N) CSV
User (1) ──< (N) Analysis Results
User (1) ──< (N) User Suggestions
User (1) ──< (N) Feature Weights
User (1) ──< (N) File Analysis Config
User (1) ──< (N) Analysis Tasks
User (1) ──< (N) Statistics

Sales (1) ──< (N) CSV
Sales (1) ──< (N) Analysis Results
Sales (1) ──< (1) User Suggestions
Sales (1) ──< (1) Feature Weights
Sales (1) ──< (N) File Analysis Config
Sales (1) ──< (N) Analysis Tasks
Sales (1) ──< (N) Statistics
```

## 📝 인덱스 권장사항

```javascript
// User Collection
db.users.createIndex({ "user_id": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })  

// Sales Collection
db.sales.createIndex({ "file_id": 1 }, { unique: true })
db.sales.createIndex({ "user_id": 1 })
db.sales.createIndex({ "upload_time": -1 })

// CSV Collection
db.csv.createIndex({ "file_id": 1, "row_index": 1 })
db.csv.createIndex({ "user_id": 1 })

// Analysis Results Collection
db.analysis_results.createIndex({ "file_id": 1 })
db.analysis_results.createIndex({ "user_id": 1 })
db.analysis_results.createIndex({ "results_id": 1 }, { unique: true })

// User Suggestions Collection
db.user_suggestions.createIndex({ "file_id": 1 })
db.user_suggestions.createIndex({ "user_id": 1 })

// Feature Weights Collection
db.feature_weights.createIndex({ "file_id": 1 })
db.feature_weights.createIndex({ "user_id": 1 })

// File Analysis Config Collection
db.file_analysis_config.createIndex({ "file_id": 1 })
db.file_analysis_config.createIndex({ "file_id": 1, "target_column": 1 })
db.file_analysis_config.createIndex({ "user_id": 1 })
db.file_analysis_config.createIndex({ "updated_at": -1 })

// Analysis Tasks Collection
db.analysis_tasks.createIndex({ "task_id": 1 }, { unique: true })
db.analysis_tasks.createIndex({ "file_id": 1 })
db.analysis_tasks.createIndex({ "user_id": 1 })
db.analysis_tasks.createIndex({ "status": 1 })
db.analysis_tasks.createIndex({ "created_at": -1 })

// Statistics Collection
db.statistics.createIndex({ "statistics_id": 1 }, { unique: true })
db.statistics.createIndex({ "file_id": 1 })
db.statistics.createIndex({ "user_id": 1 })
db.statistics.createIndex({ "created_at": -1 })
```

