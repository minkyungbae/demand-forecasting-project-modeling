
export interface ProductData {
    product_name: string;
    Price: number;    // 개당 가격 (매출 계산용)
    Quantity: number; // 판매 수량
    [key: string]: any; // 기타 동적 컬럼 대응
  }
  
export interface FilePayload {
  data: ProductData[];
  headers: string[];
}

export interface AnalyticsSummary {
  totalSales: number;
  totalQuantity: number;
  topProduct: string;
  aiInsights: string;
}

export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  user_type: 'Basic' | 'Premium' | 'Admin';
  created_at: string;
}

// 회원가입 요청
export interface RegisterPayload {
  username: string; // email
  password: string;
  name: string;
  user_type?: 'admin' | 'premium' | 'basic';
}

// 회원가입 응답
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