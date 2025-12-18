# 크롤링 목적
목적 : 인도의 온라인 식료품 배달 플랫폼인 블링킷(Blinkit)사이트의 경쟁사인 zepto에 대한 정보를 크롤링한다.

## Zepto
주요 기능:
1. 대분류 카테고리 크롤링: 메인 페이지에서 모든 대분류 카테고리 수집
2. 중분류 카테고리 크롤링: 각 대분류의 중분류 카테고리 수집
3. 상품 정보 추출: 각 중분류 페이지에서 다음 정보 수집:
    - 상품명
    - 가격 (할인된 가격)
    - 원래 가격
    - 할인율 (자동 계산)
    - sold out 여부
    - 무게/단위
    - 상품 URL
4. 데이터 저장: results/zepto/ 디렉토리에 01_zepto.csv, 01_zepto.json 형식으로 저장

---

## elements
- 상품 컨테이너 : a.B4vNQ -> 개별 상품을 감싸는 전체 링크 태그
- 상품명 : "div[data-slot-id=""ProductName""] span" -> 상품의 이름이 들어있는 span 태그
= 할인된 가격 : "div[data-slot-id=""EdlpPrice""] span.cptQT7" -> 현재 판매 중인 최종 가격
- 원래 가격 : "div[data-slot-id=""EdlpPrice""] span.cx3iWL" -> 할인 전 원래 가격
- 할인 금액/율 : div.cYCsFo span -> 10 OFF와 같이 할인 정보
- 품절 여부 : "div[data-is-out-of-stock=""true""]" -> 태그 속성에 품절 여부가 표시되거나, div[data-slot-id=""SystemTag""]에 ""Sold out"" 텍스트 갖고옮
- 무게/단위 : "div[data-slot-id=""PackSize""] span" -> 250 g, 1 pc 등의 단위 정보
- 상품 구매 URL : a.B4vNQ의 href 속성 -> 사이트 도메인 뒤에 붙는 상품 상세 경로입니다.

---

### 크롤링 성공 확률 높이기
-> 보편적으로 사용되는 태그와 클래스 이름
- 상품명 (Product Name)
    - .product-title, .product-name, .item-name, h1, h2, h3
    - [class*="title"], [class*="name"]
- 가격 (Price)
    - .price, .sale-price, .current-price, .final-price
    - .amount, .price-container
- 원래 가격 (Original Price)
    - .original-price, .old-price, .strike, .strikethrough, del
- 할인율/할인내용 (Discount)
    - .discount, .badge, .offer, .percentage, .savings
- 단위/무게 (Unit/Weight)
    - .unit, .weight, .quantity, .size, .pack-size
- 품절 (Sold Out)
    - .sold-out, .out-of-stock, .unavailable, .not-available
    - 버튼 텍스트가 "Notify Me"로 바뀌었는지 확인

---

### 코드 설명
- 동적 속성 활용 (data-slot-id):
    - Zepto는 B4vNQ, cptQT7 같은 난해한 클래스 이름을 사용하지만, data-slot-id="ProductName" 같은 속성은 고정될 확률이 매우 높습니다. 이 코드는 해당 속성을 최우선으로 찾습니다.

- 범용 선택자 (Fallback) 전략:
    - item.find_element(By.CSS_SELECTOR, "A, B, C") 형태를 사용하여, A가 없으면 B, B가 없으면 C를 찾도록 설정했습니다. (예: span.cptQT7, .price)

- 스크롤 로직:
    - 상품 페이지는 한 번에 모든 상품을 보여주지 않습니다. execute_script를 통해 페이지 끝까지 스크롤하여 추가 상품이 로드되도록 대기 시간을 주었습니다.

- 품절 여부 판단:
    - HTML 구조상 data-is-out-of-stock="true"라는 명확한 속성이 존재하므로 이를 추출합니다. 추가로 버튼 텍스트가 "Add"가 아닌 "Notify Me"인 경우를 체크하는 로직을 추가할 수도 있습니다.

- 예외 처리 (try-except):
    - 특정 상품에 할인 정보가 없거나 원래 가격이 없을 때 코드가 멈추지 않고 계속 진행되도록 설정했습니다.