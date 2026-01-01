
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
  