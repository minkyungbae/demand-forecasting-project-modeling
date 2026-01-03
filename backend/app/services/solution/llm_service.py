from typing import Optional, List, Dict, Tuple
import httpx
import json
import re
from app.core.config import settings

class LLMService:
    """LLM 서비스 (OpenRouter 사용)"""
    
    async def generate_insights(
        self,
        file_id: str,
        correlation_data: Optional[Dict],
        prediction_data: Optional[Dict],
        question: Optional[str]
    ) -> Dict[str, any]:
        """인사이트 및 추천사항 생성"""
        # OpenRouter API 키가 있으면 LLM 사용, 없으면 기본 템플릿 반환
        if settings.OPENROUTER_API_KEY:
            try:
                return await self._generate_with_openrouter(
                    file_id, correlation_data, prediction_data, question
                )
            except Exception as e:
                print(f"⚠️ OpenRouter API 오류: {str(e)}, 기본 템플릿 사용")
        
        # 기본 템플릿 반환
        return self._generate_default_insights(correlation_data, prediction_data)
    
    def _generate_default_insights(
        self,
        correlation_data: Optional[Dict],
        prediction_data: Optional[Dict]
    ) -> Dict[str, any]:
        """기본 인사이트 생성 (API 키 없을 때)"""
        insights = []
        recommendations = []
        
        if correlation_data:
            insights.append("상관관계 분석이 완료되었습니다.")
            if isinstance(correlation_data, dict):
                top_features = list(correlation_data.get('weights', {}).keys())[:3]
                if top_features:
                    recommendations.append(f"다음 피처들에 집중하세요: {', '.join(top_features)}")
        
        if prediction_data:
            insights.append("예측 모델이 생성되었습니다.")
            # PredictionResponse 객체인 경우 dict로 변환
            if hasattr(prediction_data, 'model_metrics'):
                model_metrics = prediction_data.model_metrics
            elif isinstance(prediction_data, dict):
                model_metrics = prediction_data.get('model_metrics', {})
            else:
                model_metrics = {}
            
            r2 = model_metrics.get('r2', 0) if isinstance(model_metrics, dict) else (getattr(model_metrics, 'r2', 0) if hasattr(model_metrics, 'r2') else 0)
            if r2 > 0.7:
                recommendations.append("모델의 예측 정확도가 높습니다. 신뢰할 수 있는 예측입니다.")
            else:
                recommendations.append("모델의 예측 정확도를 개선하기 위해 더 많은 데이터를 수집하세요.")
        
        if not insights:
            insights.append("데이터 분석을 시작하세요.")
            recommendations.append("CSV 파일을 업로드하고 분석을 진행하세요.")
        
        generated_text = "\n".join(insights) + "\n\n" + "\n".join(recommendations)
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'generated_text': generated_text
        }
    
    async def _generate_with_openrouter(
        self,
        file_id: str,
        correlation_data: Optional[Dict],
        prediction_data: Optional[Dict],
        question: Optional[str]
    ) -> Dict[str, any]:
        """OpenRouter API를 사용한 인사이트 생성"""
        # 프롬프트 구성
        prompt = self._build_prompt(correlation_data, prediction_data, question)
        
        # OpenRouter API 호출
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",  # 선택적
                    "X-Title": "ForeCastly Analytics",  # 선택적
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 데이터 분석 전문가입니다. 사용자의 데이터 분석 결과를 바탕으로 인사이트와 추천사항을 제공합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 응답 파싱
            generated_text = result["choices"][0]["message"]["content"]
            
            # 인사이트와 추천사항 분리 (간단한 파싱)
            insights, recommendations = self._parse_llm_response(generated_text)
            
            return {
                'insights': insights,
                'recommendations': recommendations,
                'generated_text': generated_text
            }
    
    def _build_prompt(
        self,
        correlation_data: Optional[Dict],
        prediction_data: Optional[Dict],
        question: Optional[str]
    ) -> str:
        """LLM 프롬프트 구성"""
        prompt_parts = ["다음 데이터 분석 결과를 바탕으로 인사이트와 추천사항을 제공해주세요.\n\n"]
        
        if correlation_data:
            prompt_parts.append("## 상관관계 분석 결과\n")
            if isinstance(correlation_data, dict):
                weights = correlation_data.get('weights', {})
            else:
                weights = getattr(correlation_data, 'weights', {}) if hasattr(correlation_data, 'weights') else {}
            
            if weights:
                if isinstance(weights, dict):
                    top_features = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:5]
                else:
                    top_features = []
                prompt_parts.append("주요 피처 가중치:\n")
                for feature, weight in top_features:
                    prompt_parts.append(f"- {feature}: {weight:.3f}\n")
            prompt_parts.append("\n")
        
        if prediction_data:
            prompt_parts.append("## 예측 모델 결과\n")
            # PredictionResponse 객체 처리
            if hasattr(prediction_data, 'model_metrics'):
                metrics = prediction_data.model_metrics
            elif isinstance(prediction_data, dict):
                metrics = prediction_data.get('model_metrics', {})
            else:
                metrics = {}
            
            if metrics:
                prompt_parts.append(f"모델 성능 지표:\n")
                if isinstance(metrics, dict):
                    for key, value in metrics.items():
                        prompt_parts.append(f"- {key}: {value}\n")
                else:
                    # Pydantic 모델인 경우
                    for key in ['mse', 'rmse', 'mae', 'r2']:
                        if hasattr(metrics, key):
                            prompt_parts.append(f"- {key}: {getattr(metrics, key)}\n")
            prompt_parts.append("\n")
        
        if question:
            prompt_parts.append(f"## 추가 질문\n{question}\n\n")
        
        prompt_parts.append("위 분석 결과를 바탕으로:\n")
        prompt_parts.append("1. 주요 인사이트 3-5개를 나열해주세요.\n")
        prompt_parts.append("2. 실용적인 추천사항 3-5개를 제시해주세요.\n")
        prompt_parts.append("각 항목은 간결하고 명확하게 작성해주세요.")
        
        return "".join(prompt_parts)
    
    def _parse_llm_response(self, text: str) -> tuple[List[str], List[str]]:
        """LLM 응답을 인사이트와 추천사항으로 파싱"""
        insights = []
        recommendations = []
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 섹션 구분
            if '인사이트' in line or 'insight' in line.lower():
                current_section = 'insights'
                continue
            elif '추천' in line or 'recommendation' in line.lower():
                current_section = 'recommendations'
                continue
            
            # 번호나 불릿 제거
            line = line.lstrip('0123456789.-*• ')
            
            if current_section == 'insights' and line:
                insights.append(line)
            elif current_section == 'recommendations' and line:
                recommendations.append(line)
            elif not current_section and line:
                # 섹션이 명확하지 않으면 첫 부분은 인사이트로
                if not insights:
                    insights.append(line)
                else:
                    recommendations.append(line)
        
        # 파싱 실패 시 기본 처리
        if not insights and not recommendations:
            # 전체 텍스트를 문장 단위로 분리
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            mid = len(sentences) // 2
            insights = sentences[:mid] if mid > 0 else [text[:200]]
            recommendations = sentences[mid:] if mid < len(sentences) else []
        
        return insights[:5], recommendations[:5]  # 최대 5개씩
    
    async def analyze_columns(self, columns: List[str]) -> Dict[str, str]:
        """컬럼명을 분석하여 각 컬럼의 타입을 식별 (가격, 수량, 날짜 등)"""
        # OpenRouter API 키가 없으면 기본 규칙 기반 분석
        if not settings.OPENROUTER_API_KEY:
            return self._analyze_columns_default(columns)
        
        try:
            return await self._analyze_columns_with_llm(columns)
        except Exception as e:
            print(f"⚠️ OpenRouter API 오류: {str(e)}, 기본 규칙 기반 분석 사용")
            return self._analyze_columns_default(columns)
    
    async def _analyze_columns_with_llm(self, columns: List[str]) -> Dict[str, str]:
        """LLM을 사용한 컬럼 타입 분석"""
        prompt = f"""다음 CSV 파일의 컬럼명 목록을 보고, 각 컬럼이 무엇을 나타내는지 정확히 분석해주세요.

컬럼명 목록: {', '.join(columns)}

각 컬럼의 타입을 다음 중 하나로 분류해주세요:

1. "price": **실제 금액, 가격, 매출, 비용 등 숫자로 표현되는 금전적 가치**
   - 예시: "금액", "가격", "매출", "판매가", "비용", "수입", "지출"
   - ⚠️ 주의: "회원타입", "상품타입"처럼 "타입"이라는 단어가 있어도 금액이 아니면 "category"로 분류
   - ⚠️ 주의: "평점", "점수"처럼 숫자여도 금액이 아니면 "other"로 분류

2. "quantity": **수량, 개수, 판매량 등 물리적 수치**
   - 예시: "수량", "개수", "판매량", "재고", "인원수", "건수"
   - ⚠️ 주의: 금액과 혼동하지 않도록 주의 (금액은 price, 수량은 quantity)

3. "date": **날짜, 시간, 일자, 기간 등 시간 관련 정보**
   - 예시: "주문날짜", "생산일", "배송일", "시간", "년월일", "기간"
   - 예시: "배송_지연시간", "배송소요시간"도 시간 단위를 나타내면 "date"

4. "category": **카테고리, 분류, 종류, 타입 등 범주형 데이터**
   - 예시: "카테고리", "분류", "종류", "회원타입", "상품타입", "브랜드", "지역"
   - ⚠️ 중요: "회원타입", "상품타입" 등은 "category"로 분류 (price가 아님)

5. "other": **기타 데이터 (이름, ID, 설명, 평점, 기타 숫자 값 등)**
   - 예시: "상품명", "상품_ID", "이름", "설명", "평점", "상품별_평균평점", "ID"
   - 숫자형이어도 금액, 수량, 날짜가 아니면 "other"

**분류 원칙:**
- 컬럼명만 보고 판단하되, 의미를 정확히 파악하세요
- "타입"이라는 단어가 있어도 금액이 아니면 반드시 "category"
- 금액 관련 키워드("금액", "가격", "매출" 등)가 명확히 들어가야만 "price"
- 수량 관련 키워드("수량", "개수", "판매량" 등)가 명확히 들어가야만 "quantity"

반환 형식은 반드시 JSON 형식이어야 합니다:
{{
  "컬럼명1": "price",
  "컬럼명2": "quantity",
  "컬럼명3": "date",
  "컬럼명4": "category",
  ...
}}

모든 컬럼을 빠짐없이 분류하고, 반드시 JSON 형식으로만 응답하세요."""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",
                    "X-Title": "ForeCastly Analytics",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": """당신은 데이터 분석 전문가입니다. CSV 파일의 컬럼명을 분석하여 각 컬럼의 의미를 정확히 식별합니다.

중요한 분류 규칙:
1. "price": 반드시 금액, 가격, 매출 등 금전적 가치를 나타내는 컬럼만 분류
2. "회원타입", "상품타입"처럼 "타입"이 포함되어도 금액이 아니면 반드시 "category"
3. 컬럼명의 실제 의미를 분석하여 정확히 분류하세요
4. 애매한 경우는 "other"로 분류

반드시 JSON 형식으로만 응답합니다."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            
            generated_text = result["choices"][0]["message"]["content"]
            
            # JSON 파싱
            try:
                column_types = json.loads(generated_text)
                # 모든 컬럼이 분석되었는지 확인
                for col in columns:
                    if col not in column_types:
                        column_types[col] = "other"
                return column_types
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 분석 사용
                return self._analyze_columns_default(columns)
    
    def _analyze_columns_default(self, columns: List[str]) -> Dict[str, str]:
        """기본 규칙 기반 컬럼 타입 분석 (LLM 없을 때)"""
        column_types = {}
        # 가격 관련 키워드 (금액 관련 명확한 키워드만)
        price_keywords = ['가격', '금액', '매출', '판매가', 'price', 'amount', 'revenue', 'sales', 'cost', '원', '원화', '달러', 'dollar', 'won', '비용', '수입', '지출']
        # 수량 관련 키워드
        quantity_keywords = ['수량', '개수', '판매량', 'quantity', 'count', 'number', '개', '건', '재고', '인원']
        # 날짜 관련 키워드
        date_keywords = ['날짜', '시간', '일자', '기간', 'date', 'time', '날', '시', '월', '년', '일시']
        # 카테고리 관련 키워드 (type은 포함하되, 단독으로만 사용하는 경우만)
        category_keywords = ['카테고리', '분류', '종류', 'category', 'kind', '구분']
        
        for col in columns:
            col_lower = col.lower()
            
            # 특수 케이스: "타입"이 포함된 경우 (회원타입, 상품타입 등)
            # "타입" 단어가 있고 금액 키워드가 없으면 category로 분류
            if '타입' in col or 'type' in col_lower:
                # 금액 관련 키워드가 명확히 없으면 category
                if not any(keyword in col_lower for keyword in price_keywords):
                    column_types[col] = "category"
                    continue
            
            # 우선순위: price > quantity > date > category > other
            if any(keyword in col_lower for keyword in price_keywords):
                column_types[col] = "price"
            elif any(keyword in col_lower for keyword in quantity_keywords):
                column_types[col] = "quantity"
            elif any(keyword in col_lower for keyword in date_keywords):
                column_types[col] = "date"
            elif any(keyword in col_lower for keyword in category_keywords):
                column_types[col] = "category"
            else:
                column_types[col] = "other"
        
        return column_types
    
    async def suggest_related_columns_simple(
        self,
        target_column: str,
        all_columns: List[str],
        data_sample: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """컬럼 분류 (그룹화 컬럼, 직접 연관 컬럼, 유효 컬럼 분리)"""
        # OpenRouter API 키가 없으면 기본 규칙 기반 추천
        if not settings.OPENROUTER_API_KEY:
            return self._suggest_related_columns_simple_default(target_column, all_columns)
        
        try:
            return await self._suggest_related_columns_simple_with_llm(target_column, all_columns, data_sample)
        except Exception as e:
            import traceback
            print(f"⚠️ OpenRouter API 오류: {str(e)}")
            print(f"상세 오류: {traceback.format_exc()}")
            print("기본 규칙 기반 추천 사용")
            return self._suggest_related_columns_simple_default(target_column, all_columns)
    
    async def _suggest_related_columns_simple_with_llm(
        self,
        target_column: str,
        all_columns: List[str],
        data_sample: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """LLM을 사용한 컬럼 분류 (그룹화 컬럼, 직접 연관 컬럼, 유효 컬럼 분리)"""
        # 대상 컬럼 제외한 나머지 컬럼들
        other_columns = [col for col in all_columns if col != target_column]
        
        # 데이터 샘플 정보 추가
        sample_info = ""
        if data_sample and len(data_sample) > 0:
            sample_info = "\n\n**데이터 샘플 (처음 5행):**\n"
            for i, row in enumerate(data_sample[:5]):
                sample_info += f"행 {i+1}: {dict(list(row.items())[:5])}\n"  # 처음 5개 컬럼만
        
        prompt = f"""다음 CSV 파일의 데이터를 분석하고 있습니다. 데이터는 시계열 데이터이며 날짜 컬럼을 기준으로 정렬되어 있습니다.
       
       예측 대상 컬럼: "{target_column}"
       전체 컬럼 목록: {', '.join(all_columns)}
       {sample_info}
       
       컬럼들을 다음 3가지 카테고리로 분류해주세요:
       
       1. **grouping_columns (그룹화 컬럼)**: 그룹화/집계에만 사용되는 명목형 컬럼
          - 예시: "브랜드", "카테고리", "상품_ID", "상품명", "지역", "회원타입" 등
          - 특징: 범주형 데이터, 고유값이 적당한 개수 (전체의 5%~50%)
          - 용도: 그룹화하여 상관계수나 시각화를 그룹별로 분석할 때 사용
          - ⚠️ 이 컬럼들은 상관관계 분석이나 예측 모델의 직접적인 피처로 사용되지 않음
       
       2. **directly_related_columns (직접 연관 컬럼)**: 타겟 컬럼과 직접적인 계산 관계가 있는 컬럼
          - 예시: 
            - 타겟이 "수량"인 경우 → "금액", "판매금액", "단가" 등 (수량 × 단가 = 금액)
            - 타겟이 "금액"인 경우 → "수량", "단가" 등
            - 같은 의미의 컬럼: "판매량"과 "판매개수", "금액"과 "매출" 등
          - 특징: 타겟 컬럼과 수학적으로 직접 연관됨 (예: 곱셈, 나눗셈 관계)
          - ⚠️ 상관관계 분석에 불필요하고 예측에도 의미 없음 (이미 타겟과 직접 연관됨)
       
       3. **valid_columns (유효 컬럼)**: 예측 및 상관관계 분석에 사용할 수 있는 컬럼
          - 숫자형 컬럼: "평점", "배송_지연시간", "배송소요시간", "유통기한_일수" 등
          - 특징: 타겟과 직접 계산 관계가 아니며, 시계열 Lag 피처로 변환 가능한 컬럼
          - 용도: 시계열 기반으로 Lag 피처 생성 (예: 지난주 평점, 지난주 배송지연시간)
          - ⚠️ 현재 주의 값이 아닌 지난 주/달의 값이 유효함
       
       **날짜 컬럼 처리**:
       - 날짜 컬럼 (예: "주문날짜", "날짜")은 grouping_columns, directly_related_columns, valid_columns 모두에 포함하지 않음
       - 날짜 컬럼은 시계열 정렬 및 Lag 피처 생성에만 사용됨
       
       **중요 규칙**:
       - 각 컬럼은 반드시 3개 카테고리 중 하나에만 속해야 함 (중복 없음)
       - 타겟 컬럼은 분류하지 않음 (제외)
       - 날짜 컬럼은 3개 카테고리 모두에 포함하지 않음
       
       반환 형식은 반드시 JSON 형식이어야 합니다:
       {{
         "grouping_columns": ["브랜드", "카테고리", "상품_ID", ...],
         "directly_related_columns": ["금액", "단가", ...],
         "valid_columns": ["평점", "배송_지연시간", "배송소요시간", ...],
         "date_column": "주문날짜",  // 날짜 컬럼명 (자동 감지)
         "reason": "분류 이유를 간단히 설명"
       }}
       
       한국어로 된 컬럼명도 정확히 분석해주세요. 반드시 JSON 형식으로만 응답하세요."""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",
                    "X-Title": "ForeCastly Analytics",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 데이터 분석 전문가입니다. 예측 대상 컬럼과 직접적으로 연관된 컬럼만 제외하고, 나머지는 모두 추천합니다. 반드시 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 반환하세요."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            )
            
            # 응답 상태 확인 전에 에러 응답 체크
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = str(error_json.get('error', error_detail))
                except:
                    pass
                print(f"⚠️ OpenRouter API 응답: {error_detail}")
                raise Exception(f"OpenRouter API 오류 ({response.status_code}): {error_detail}")
            
            response.raise_for_status()
            result = response.json()
            
            # 에러 응답 확인
            if "error" in result:
                raise Exception(f"OpenRouter API 오류: {result['error']}")
            
            generated_text = result["choices"][0]["message"]["content"]
            
            # JSON 파싱 (응답에서 JSON 코드 블록 제거)
            try:
                # ```json ... ``` 형식 제거
                if "```json" in generated_text:
                    generated_text = generated_text.split("```json")[1].split("```")[0].strip()
                elif "```" in generated_text:
                    generated_text = generated_text.split("```")[1].split("```")[0].strip()
                
                suggestion = json.loads(generated_text)
                
                # 새로운 형식 검증
                grouping_columns = [
                    col for col in suggestion.get("grouping_columns", [])
                    if col in other_columns
                ]
                directly_related_columns = [
                    col for col in suggestion.get("directly_related_columns", [])
                    if col in other_columns
                ]
                valid_columns = [
                    col for col in suggestion.get("valid_columns", [])
                    if col in other_columns
                ]
                date_column = suggestion.get("date_column")
                # date_column이 실제 컬럼 목록에 있는지 확인
                if date_column and date_column not in all_columns:
                    date_column = None
                
                # 하위 호환성을 위해 related_columns와 excluded_columns도 제공
                # related_columns = grouping_columns + valid_columns (예측에 사용 가능한 컬럼)
                # excluded_columns = directly_related_columns (제외된 컬럼)
                related_columns = grouping_columns + valid_columns
                excluded_columns = directly_related_columns
                
                return {
                    "grouping_columns": grouping_columns,
                    "directly_related_columns": directly_related_columns,
                    "valid_columns": valid_columns,
                    "date_column": date_column,
                    "related_columns": related_columns,  # 하위 호환성
                    "excluded_columns": excluded_columns,  # 하위 호환성
                    "reason": suggestion.get("reason", "LLM 분석 결과")
                }
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 추천 사용
                return self._suggest_related_columns_simple_default(target_column, all_columns)
    
    def _suggest_related_columns_simple_default(
        self,
        target_column: str,
        all_columns: List[str]
    ) -> Dict[str, any]:
        """기본 규칙 기반 관련 컬럼 추천 (LLM 없을 때) - 직접 연관 컬럼만 제외"""
        other_columns = [col for col in all_columns if col != target_column]
        
        target_lower = target_column.lower()
        related = []
        excluded = []
        
        # 금액/수량 관련 키워드
        price_keywords = ['가격', '금액', '매출', '판매가', 'price', 'amount', 'revenue', 'sales', 'cost', '원', '원화', '달러', 'dollar', 'won', '비용', '수입', '지출']
        quantity_keywords = ['수량', '개수', '판매량', 'quantity', 'count', 'number', '개', '건', '재고', '인원']
        date_keywords = ['날짜', '시간', '일자', '기간', 'date', 'time', '날', '시', '월', '년', '일시']
        
        # 타겟 컬럼이 금액인지 수량인지 판단
        is_target_price = any(keyword in target_lower for keyword in price_keywords)
        is_target_quantity = any(keyword in target_lower for keyword in quantity_keywords)
        
        for col in other_columns:
            col_lower = col.lower()
            is_col_price = any(keyword in col_lower for keyword in price_keywords)
            is_col_quantity = any(keyword in col_lower for keyword in quantity_keywords)
            
            # 날짜/시간 컬럼 제외 (예측 모델에서 직접 사용 불가)
            if any(keyword in col_lower for keyword in date_keywords):
                excluded.append(col)
                continue
            
            # 직접적인 관계 제외: 금액-수량 관계
            if (is_target_price and is_col_quantity) or (is_target_quantity and is_col_price):
                excluded.append(col)
                continue
            
            # 같은 의미의 컬럼 제외 (이름이 비슷한 경우)
            target_words = set(target_lower.replace('_', ' ').replace('-', ' ').split())
            col_words = set(col_lower.replace('_', ' ').replace('-', ' ').split())
            # 공통 단어가 많으면 같은 의미로 판단
            common_words = target_words & col_words
            if len(common_words) >= 2 or (len(common_words) == 1 and len(target_words) <= 2):
                excluded.append(col)
                continue
            
            # 나머지는 모두 포함
            related.append(col)
        
        reason = f"규칙 기반 분석: '{target_column}'과 직접적인 관계를 제외한 {len(related)}개 컬럼 추천"
        
        return {
            "related_columns": related,
            "excluded_columns": excluded,
            "reason": reason
        }
    
    async def match_quantity_and_price_columns(
        self,
        columns: List[str]
    ) -> Dict[str, Optional[str]]:
        """CSV 컬럼 목록에서 수량/금액 컬럼을 자동 매칭 (각각 1개씩만)
        
        Returns:
            {
                "quantity_column": "매칭된_수량_컬럼명" or None,
                "price_column": "매칭된_금액_컬럼명" or None
            }
        """
        if not settings.OPENROUTER_API_KEY:
            return self._match_columns_default(columns)
        
        try:
            return await self._match_columns_with_llm(columns)
        except Exception as e:
            print(f"⚠️ LLM 컬럼 매칭 오류: {str(e)}, 기본 규칙 기반 매칭 사용")
            import traceback
            print(f"상세 오류:\n{traceback.format_exc()}")
            return self._match_columns_default(columns)
    
    async def _match_columns_with_llm(
        self,
        columns: List[str]
    ) -> Dict[str, Optional[str]]:
        """LLM을 사용한 수량/금액 컬럼 매칭"""
        prompt = f"""다음 CSV 파일의 컬럼 목록에서 "수량"과 "금액"에 해당하는 컬럼을 각각 정확히 1개씩만 찾아주세요.

컬럼 목록: {', '.join(columns)}

**수량 컬럼**: 판매량, 개수, 재고수량, 주문수량 등 수량을 나타내는 컬럼
**금액 컬럼**: 가격, 판매금액, 매출액, 총액 등 금액을 나타내는 컬럼

반드시 JSON 형식으로만 응답하세요:
{{
  "quantity_column": "정확한_수량_컬럼명" 또는 null,
  "price_column": "정확한_금액_컬럼명" 또는 null
}}

매칭되는 컬럼이 없으면 null로 반환하세요. 각각 최대 1개씩만 반환하세요."""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",
                    "X-Title": "ForeCastly Analytics",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 데이터 분석 전문가입니다. CSV 컬럼 목록에서 수량과 금액 컬럼을 정확히 1개씩만 찾습니다. 반드시 JSON 형식으로만 응답하세요."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # 낮은 온도로 정확도 향상
                    "max_tokens": 200
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = str(error_json.get('error', error_detail))
                except:
                    pass
                print(f"⚠️ OpenRouter API 응답 오류: {error_detail}")
                response.raise_for_status()
            
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            
            # JSON 파싱 (```json 블록 제거)
            json_match = re.search(r"```json\n(.*)\n```", generated_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = generated_text
            
            try:
                matched = json.loads(json_string)
                # 컬럼명 검증 (실제 컬럼 목록에 있는지 확인)
                quantity_column = matched.get("quantity_column")
                price_column = matched.get("price_column")
                
                if quantity_column and quantity_column not in columns:
                    print(f"⚠️ 매칭된 수량 컬럼 '{quantity_column}'이 실제 컬럼 목록에 없습니다.")
                    quantity_column = None
                
                if price_column and price_column not in columns:
                    print(f"⚠️ 매칭된 금액 컬럼 '{price_column}'이 실제 컬럼 목록에 없습니다.")
                    price_column = None
                
                return {
                    "quantity_column": quantity_column,
                    "price_column": price_column
                }
            except json.JSONDecodeError as e:
                print(f"❌ LLM 응답 JSON 파싱 실패: {e}")
                print(f"원본 LLM 응답:\n{generated_text}")
                return self._match_columns_default(columns)
    
    def _match_columns_default(
        self,
        columns: List[str]
    ) -> Dict[str, Optional[str]]:
        """기본 규칙 기반 수량/금액 컬럼 매칭"""
        quantity_column = None
        price_column = None
        
        # 수량 키워드 (우선순위 순)
        quantity_keywords = [
            ['수량', 'quantity'],
            ['개수', 'count', 'number'],
            ['판매량', 'sales_quantity'],
            ['재고', 'stock'],
            ['인원', 'person']
        ]
        
        # 금액 키워드 (우선순위 순)
        price_keywords = [
            ['금액', 'amount'],
            ['가격', 'price', 'cost'],
            ['매출', 'revenue', 'sales'],
            ['판매가', 'selling_price'],
            ['총액', 'total']
        ]
        
        # 수량 컬럼 찾기 (우선순위 순으로 매칭)
        for keywords in quantity_keywords:
            for col in columns:
                col_lower = col.lower()
                if any(keyword.lower() in col_lower for keyword in keywords):
                    quantity_column = col
                    break
            if quantity_column:
                break
        
        # 금액 컬럼 찾기 (우선순위 순으로 매칭)
        for keywords in price_keywords:
            for col in columns:
                col_lower = col.lower()
                if any(keyword.lower() in col_lower for keyword in keywords):
                    price_column = col
                    break
            if price_column:
                break
        
        return {
            "quantity_column": quantity_column,
            "price_column": price_column
        }
    
    async def suggest_group_by_columns(
        self,
        columns: List[str],
        target_column: str,
        data_sample: Optional[List[Dict]] = None,
        column_stats: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, List[str]]:
        """상관계수 분석 시 그룹화할 컬럼들을 LLM으로 추천 (데이터 샘플 기반)
        
        Args:
            columns: 전체 컬럼 목록
            target_column: 예측 대상 컬럼
            data_sample: 실제 데이터 샘플 (최대 20행)
            column_stats: 각 컬럼의 통계 정보 (고유값 개수, 데이터 타입 등)
        
        Returns:
            {
                "group_by_columns": ["상품_ID", "브랜드", "카테고리"]  # 그룹화할 컬럼 목록
            }
        """
        if not settings.OPENROUTER_API_KEY:
            return self._suggest_group_by_columns_default(columns, target_column, column_stats)
        
        try:
            return await self._suggest_group_by_columns_with_llm(columns, target_column, data_sample, column_stats)
        except Exception as e:
            print(f"⚠️ LLM 그룹화 컬럼 추천 오류: {str(e)}, 기본 규칙 기반 추천 사용")
            import traceback
            print(f"상세 오류:\n{traceback.format_exc()}")
            return self._suggest_group_by_columns_default(columns, target_column, column_stats)
    
    async def _suggest_group_by_columns_with_llm(
        self,
        columns: List[str],
        target_column: str,
        data_sample: Optional[List[Dict]] = None,
        column_stats: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, List[str]]:
        """LLM을 사용한 그룹화 컬럼 추천 (데이터 샘플 기반)"""
        
        # 데이터 샘플 문자열 생성
        sample_str = ""
        if data_sample and len(data_sample) > 0:
            sample_rows = data_sample[:20]  # 최대 20행만
            sample_str = "\n\n**실제 데이터 샘플 (처음 몇 행):**\n"
            for i, row in enumerate(sample_rows[:5], 1):  # 처음 5행만 표시
                sample_str += f"\n행 {i}:\n"
                for col in columns[:10]:  # 처음 10개 컬럼만 표시 (너무 길어지지 않도록)
                    if col in row:
                        value = str(row[col])[:50]  # 값이 너무 길면 잘라냄
                        sample_str += f"  - {col}: {value}\n"
        
        # 컬럼 통계 정보 문자열 생성
        stats_str = ""
        if column_stats:
            stats_str = "\n\n**각 컬럼의 통계 정보:**\n"
            for col in columns:
                if col in column_stats:
                    stats = column_stats[col]
                    unique_count = stats.get('unique_count', 'N/A')
                    data_type = stats.get('data_type', 'N/A')
                    stats_str += f"- {col}: 타입={data_type}, 고유값 개수={unique_count}\n"
        
        prompt = f"""다음 CSV 데이터에서 "{target_column}" 컬럼의 상관관계를 분석하려고 합니다.

**전체 컬럼 목록**: {', '.join(columns)}
{sample_str}
{stats_str}

**과제**: 상관관계 분석 시 **그룹별로 나누어서 분석**해야 하는 컬럼들을 찾아주세요.

**그룹화할 컬럼의 판단 기준**:
1. **범주형/카테고리형 데이터**: 고유값이 적당한 범주형 컬럼 (예: 상품명, 브랜드, 카테고리, 지역, 부서 등)
2. **그룹별 독립성**: 각 그룹별로 독립적인 상관관계 패턴이 있을 것으로 예상되는 컬럼
3. **적절한 그룹 수**: 고유값이 너무 적지도(2개 미만) 않고 너무 많지도 않은(전체 행의 80% 이상) 컬럼
   - 이상적: 고유값이 전체 행의 5%~50% 범위
4. **데이터 특성**: 실제 데이터 샘플을 보고, 그룹화했을 때 의미있는 분석이 가능한 컬럼

**주의사항**:
- 숫자형 ID 컬럼도 그룹화 대상이 될 수 있음 (예: 상품_ID, 주문_ID 등)
- 날짜/시간 컬럼은 그룹화 대상이 아님
- 타겟 컬럼({target_column})은 그룹화 대상이 아님
- 연속형 숫자 데이터는 그룹화 대상이 아님

**반환 형식** (반드시 JSON만):
{{
  "group_by_columns": ["컬럼1", "컬럼2", "컬럼3"],
  "reason": "각 컬럼을 그룹화 대상으로 선택한 이유를 간단히 설명"
}}

그룹화할 컬럼이 없으면 빈 배열 []을 반환하세요. 최대 4개까지만 추천하세요."""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",
                    "X-Title": "ForeCastly Analytics",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 데이터 분석 전문가입니다. 상관관계 분석 시 그룹별로 나누어서 분석할 컬럼들을 추천합니다. 반드시 JSON 형식으로만 응답하세요."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 300
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = str(error_json.get('error', error_detail))
                except:
                    pass
                print(f"⚠️ OpenRouter API 응답 오류: {error_detail}")
                response.raise_for_status()
            
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            
            # JSON 파싱 (```json 블록 제거)
            json_match = re.search(r"```json\n(.*)\n```", generated_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = generated_text
            
            try:
                suggestion = json.loads(json_string)
                group_by_columns = suggestion.get("group_by_columns", [])
                reason = suggestion.get("reason", "LLM 분석 결과")
                
                # 컬럼명 검증 (실제 컬럼 목록에 있는지 확인)
                valid_columns = [col for col in group_by_columns if col in columns]
                
                print(f"📊 LLM 그룹화 컬럼 추천: {valid_columns}")
                if reason:
                    print(f"   이유: {reason}")
                
                return {
                    "group_by_columns": valid_columns[:4],  # 최대 4개까지만
                    "reason": reason
                }
            except json.JSONDecodeError as e:
                print(f"❌ LLM 응답 JSON 파싱 실패: {e}")
                print(f"원본 LLM 응답:\n{generated_text}")
                return self._suggest_group_by_columns_default(columns, target_column)
    
    async def _generate_statistics_explanation_with_llm(self, prompt: str) -> str:
        """LLM을 사용한 통계 설명 생성"""
        if not settings.OPENROUTER_API_KEY:
            return "통계 분석이 완료되었습니다."
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://forecastly.app",
                        "X-Title": "ForeCastly Analytics",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.OPENROUTER_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "당신은 데이터 분석 전문가입니다. 통계 분석 결과를 기반으로 명확하고 간결한 설명을 제공합니다."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ LLM 통계 설명 생성 오류: {str(e)}")
            raise e
    
    def _suggest_group_by_columns_default(
        self,
        columns: List[str],
        target_column: str
    ) -> Dict[str, List[str]]:
        """기본 규칙 기반 그룹화 컬럼 추천"""
        group_by_columns = []
        
        # 그룹화 가능한 키워드
        group_keywords = [
            ['상품', '제품', 'product', 'item'],
            ['브랜드', 'brand'],
            ['카테고리', '분류', 'category'],
            ['지역', 'region', 'area']
        ]
        
        for keywords in group_keywords:
            for col in columns:
                if col == target_column:
                    continue
                col_lower = col.lower()
                if any(keyword.lower() in col_lower for keyword in keywords):
                    if col not in group_by_columns:
                        group_by_columns.append(col)
                        break  # 각 키워드 그룹당 하나씩만
        
        return {
            "group_by_columns": group_by_columns[:4]  # 최대 4개까지만
        }
    
    async def suggest_visualization_columns(
        self,
        target_column: str,
        chart_type: str,
        all_columns: List[str],
        data_sample: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """시각화를 위한 컬럼 자동 추천
        
        Args:
            target_column: 시각화하고 싶은 주요 컬럼명 (예: "판매량", "매출")
            chart_type: 차트 타입 (line, bar, scatter, heatmap, pie, area)
            all_columns: 전체 컬럼 목록
            data_sample: 데이터 샘플 (선택)
        
        Returns:
            {
                "x_column": "추천된_X축_컬럼명",
                "y_column": "추천된_Y축_컬럼명",
                "columns": ["컬럼1", "컬럼2", ...],  # heatmap 등에 사용
                "reason": "추천 이유"
            }
        """
        if not settings.OPENROUTER_API_KEY:
            return self._suggest_visualization_columns_default(target_column, chart_type, all_columns)
        
        try:
            return await self._suggest_visualization_columns_with_llm(target_column, chart_type, all_columns, data_sample)
        except Exception as e:
            print(f"⚠️ LLM 시각화 컬럼 추천 오류: {str(e)}, 기본 규칙 기반 추천 사용")
            import traceback
            print(traceback.format_exc())
            return self._suggest_visualization_columns_default(target_column, chart_type, all_columns)
    
    async def _suggest_visualization_columns_with_llm(
        self,
        target_column: str,
        chart_type: str,
        all_columns: List[str],
        data_sample: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """LLM을 사용한 시각화 컬럼 추천"""
        
        # 데이터 샘플 정보 추가
        sample_info = ""
        if data_sample and len(data_sample) > 0:
            sample_info = "\n\n**데이터 샘플 (처음 5행):**\n"
            for i, row in enumerate(data_sample[:5], 1):
                sample_info += f"행 {i}: {dict(list(row.items())[:5])}\n"
        
        chart_type_descriptions = {
            "line": "선 그래프 - 시계열 데이터의 추세를 보여줍니다. X축은 날짜/시간, Y축은 수치 데이터가 적합합니다.",
            "bar": "막대 그래프 - 카테고리별 값을 비교합니다. X축은 카테고리, Y축은 수치 데이터가 적합합니다.",
            "scatter": "산점도 - 두 변수 간의 관계를 보여줍니다. X축과 Y축 모두 수치 데이터가 적합합니다.",
            "heatmap": "히트맵 - 다중 변수 간의 상관관계를 보여줍니다. 여러 숫자형 컬럼이 필요합니다.",
            "pie": "파이 차트 - 전체 대비 비율을 보여줍니다. 카테고리와 수치 데이터가 필요합니다.",
            "area": "영역 그래프 - 누적 데이터나 여러 시계열을 표현합니다. X축은 날짜/시간, Y축은 수치 데이터가 적합합니다."
        }
        
        prompt = f"""다음 CSV 파일의 데이터를 시각화하려고 합니다.

**시각화 대상 컬럼**: "{target_column}"
**차트 타입**: {chart_type} - {chart_type_descriptions.get(chart_type, '')}
**전체 컬럼 목록**: {', '.join(all_columns)}
{sample_info}

**과제**: "{target_column}" 컬럼을 시각화하기에 가장 적합한 컬럼들을 추천해주세요.

**차트 타입별 추천 기준**:
- **line/area**: X축은 날짜/시간 컬럼, Y축은 "{target_column}" 또는 관련 수치 컬럼
- **bar**: X축은 카테고리/그룹 컬럼, Y축은 "{target_column}" 또는 관련 수치 컬럼
- **scatter**: X축과 Y축 모두 수치 데이터 (X축은 "{target_column}"과 관련된 다른 수치 컬럼)
- **heatmap**: 여러 숫자형 컬럼 (최소 3개 이상, "{target_column}" 포함)
- **pie**: 카테고리 컬럼과 "{target_column}" 또는 관련 수치 컬럼

**중요 규칙**:
1. "{target_column}" 컬럼이 실제 컬럼 목록에 있는지 확인
2. 차트 타입에 맞는 적절한 컬럼 조합 추천
3. 날짜/시간 컬럼은 X축에 우선 추천
4. 카테고리 컬럼은 bar, pie 차트의 X축에 추천
5. 숫자형 컬럼은 Y축에 추천

**반환 형식** (반드시 JSON만):
{{
  "x_column": "추천된_X축_컬럼명" 또는 null,
  "y_column": "추천된_Y축_컬럼명" (대부분 "{target_column}" 또는 관련 컬럼),
  "columns": ["컬럼1", "컬럼2", ...],  // heatmap 등에 사용 (최소 3개)
  "reason": "추천 이유를 간단히 설명"
}}

차트 타입에 따라 일부 필드는 null일 수 있습니다. 반드시 JSON 형식으로만 응답하세요."""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://forecastly.app",
                    "X-Title": "ForeCastly Analytics",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 데이터 시각화 전문가입니다. 차트 타입과 대상 컬럼에 맞는 최적의 컬럼 조합을 추천합니다. 반드시 JSON 형식으로만 응답하세요."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 400
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = str(error_json.get('error', error_detail))
                except:
                    pass
                print(f"⚠️ OpenRouter API 응답 오류: {error_detail}")
                response.raise_for_status()
            
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            
            # JSON 파싱
            try:
                # ```json 블록 제거
                if "```json" in generated_text:
                    generated_text = generated_text.split("```json")[1].split("```")[0].strip()
                elif "```" in generated_text:
                    generated_text = generated_text.split("```")[1].split("```")[0].strip()
                
                suggestion = json.loads(generated_text)
                
                # 컬럼명 검증
                x_column = suggestion.get("x_column")
                y_column = suggestion.get("y_column")
                columns = suggestion.get("columns", [])
                
                # 실제 컬럼 목록에 있는지 확인
                if x_column and x_column not in all_columns:
                    print(f"⚠️ LLM이 추천한 X축 컬럼 '{x_column}'이 실제 컬럼 목록에 없습니다.")
                    x_column = None
                
                if y_column and y_column not in all_columns:
                    print(f"⚠️ LLM이 추천한 Y축 컬럼 '{y_column}'이 실제 컬럼 목록에 없습니다.")
                    # target_column이 있으면 그것을 사용
                    y_column = target_column if target_column in all_columns else None
                
                if columns:
                    columns = [col for col in columns if col in all_columns]
                
                return {
                    "x_column": x_column,
                    "y_column": y_column or target_column,  # y_column이 없으면 target_column 사용
                    "columns": columns,
                    "reason": suggestion.get("reason", "LLM 분석 결과")
                }
            except json.JSONDecodeError as e:
                print(f"❌ LLM 응답 JSON 파싱 실패: {e}")
                print(f"원본 LLM 응답:\n{generated_text}")
                return self._suggest_visualization_columns_default(target_column, chart_type, all_columns)
    
    def _suggest_visualization_columns_default(
        self,
        target_column: str,
        chart_type: str,
        all_columns: List[str]
    ) -> Dict[str, any]:
        """기본 규칙 기반 시각화 컬럼 추천 (LLM 없을 때)"""
        # 날짜/시간 컬럼 찾기
        date_keywords = ['날짜', '시간', '일자', '기간', 'date', 'time', '날', '시', '월', '년', '일시']
        date_column = None
        for col in all_columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                date_column = col
                break
        
        # 카테고리 컬럼 찾기
        category_keywords = ['상품', '제품', 'product', 'item', '브랜드', 'brand', '카테고리', 'category', '지역', 'region']
        category_column = None
        for col in all_columns:
            if col == target_column:
                continue
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in category_keywords):
                category_column = col
                break
        
        # 차트 타입별 기본 추천
        if chart_type in ["line", "area"]:
            return {
                "x_column": date_column,
                "y_column": target_column if target_column in all_columns else None,
                "columns": None,
                "reason": f"규칙 기반 추천: {chart_type} 차트는 날짜를 X축, {target_column}을 Y축으로 사용"
            }
        elif chart_type == "bar":
            return {
                "x_column": category_column or date_column,
                "y_column": target_column if target_column in all_columns else None,
                "columns": None,
                "reason": f"규칙 기반 추천: bar 차트는 카테고리를 X축, {target_column}을 Y축으로 사용"
            }
        elif chart_type == "scatter":
            # target_column과 다른 숫자형 컬럼 찾기
            other_numeric = None
            for col in all_columns:
                if col != target_column and col not in [date_column, category_column]:
                    other_numeric = col
                    break
            
            return {
                "x_column": other_numeric or date_column,
                "y_column": target_column if target_column in all_columns else None,
                "columns": None,
                "reason": f"규칙 기반 추천: scatter 차트는 두 수치 변수를 사용"
            }
        elif chart_type == "heatmap":
            # 숫자형 컬럼 여러 개 찾기
            numeric_columns = [target_column] if target_column in all_columns else []
            for col in all_columns:
                if col != target_column and col not in [date_column, category_column]:
                    if len(numeric_columns) < 5:  # 최대 5개
                        numeric_columns.append(col)
            
            return {
                "x_column": None,
                "y_column": None,
                "columns": numeric_columns[:5] if len(numeric_columns) >= 3 else None,
                "reason": f"규칙 기반 추천: heatmap은 여러 숫자형 컬럼이 필요합니다"
            }
        elif chart_type == "pie":
            return {
                "x_column": category_column,
                "y_column": target_column if target_column in all_columns else None,
                "columns": None,
                "reason": f"규칙 기반 추천: pie 차트는 카테고리와 수치 데이터를 사용"
            }
        else:
            return {
                "x_column": date_column,
                "y_column": target_column if target_column in all_columns else None,
                "columns": None,
                "reason": "규칙 기반 추천"
            }


