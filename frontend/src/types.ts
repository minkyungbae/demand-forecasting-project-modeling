// ======================================================================
// src/types.ts
// 공용 타입 정의 파일 (API 응답, 프론트 상태, 도메인 모델)
// ======================================================================

/* =======================
    CSV / File
======================= */

// 서버에서 CSV 업로드 후 내려주는 응답
export interface CsvUploadResponse {
  file_id: string;
  filename: string;
  file_size: number;
  columns: string[];
  row_count: number;
  uploaded_at: string;
  matched_quantity_column?: string;
  matched_price_column?: string;
}

// 프론트에서 사용하는 파일 정보 (가공된 형태)
export interface FilePayload {
  file_id: string;
  filename: string;
  columns: string[];
  row_count: number;
  matched_quantity_column?: string;
  matched_price_column?: string;
}


/* =======================
    Product / Analytics
======================= */

export interface ProductData {
  product_name: string;
  Price: number;     // 개당 가격
  Quantity: number;  // 판매 수량
  [key: string]: any;
}

export interface AnalyticsSummary {
  totalSales: number;
  totalQuantity: number;
  topProduct: string;
  aiInsights: string;
}


/* =======================
    Auth / User
======================= */

// 회원가입 요청
export interface RegisterPayload {
  username: string; // email
  password: string;
  name: string;
  user_type?: 'admin' | 'premium' | 'basic';
}

// 로그인 응답
export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user: {
    id: number;
    username: string;
    name: string;
    user_type: string;
  };
}

// 사용자 프로필
export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  user_type: 'Basic' | 'Premium' | 'Admin';
  created_at: string;
}
