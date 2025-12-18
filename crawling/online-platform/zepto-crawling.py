import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# 1. 브라우저 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 화면 없이 실행하고 싶을 때 주석 제거
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def crawl_zepto_products(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # 상품 데이터 저장 리스트
    product_list = []

    # 동적 로딩 대응: 스크롤 내리기
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):  # 필요에 따라 반복 횟수 조절
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 상품 컨테이너 찾기 (제공된 HTML의 클래스 B4vNQ 활용)
    # 범용 선택자: [class*='ProductCard'], .product-item, a[href*='/pn/']
    items = driver.find_elements(By.CSS_SELECTOR, "a.B4vNQ, [data-testid='product-card'], .product-item")

    for item in items:
        try:
            # 1. 상품명 (data-slot-id 우선, 실패시 범용 클래스)
            name = item.find_element(By.CSS_SELECTOR, "div[data-slot-id='ProductName'] span, .product-title, h3").text
            
            # 2. 할인된 가격 (현재 가격)
            try:
                price = item.find_element(By.CSS_SELECTOR, "span.cptQT7, [data-slot-id='EdlpPrice'] span:first-child, .price").text
            except:
                price = "N/A"

            # 3. 원래 가격 (취소선 가격)
            try:
                original_price = item.find_element(By.CSS_SELECTOR, "span.cx3iWL, .strike, .original-price, del").text
            except:
                original_price = price # 할인이 없으면 현재가와 동일하게 처리

            # 4. 할인 정보 (할인율 또는 할인 금액)
            try:
                discount = item.find_element(By.CSS_SELECTOR, ".cYCsFo, .discount-badge, [class*='discount']").text.replace('\n', ' ')
            except:
                discount = "0%"

            # 5. 품절 여부 (data-is-out-of-stock 속성 확인)
            # container 내부의 특정 div 속성 확인
            try:
                out_of_stock_attr = item.find_element(By.XPATH, ".//div[@data-is-out-of-stock]").get_attribute("data-is-out-of-stock")
                is_sold_out = "Yes" if out_of_stock_attr == "true" else "No"
            except:
                is_sold_out = "No"

            # 6. 무게/단위
            try:
                weight = item.find_element(By.CSS_SELECTOR, "div[data-slot-id='PackSize'] span, .unit, .quantity").text
            except:
                weight = "N/A"

            # 7. 상품 구매 URL
            product_url = item.get_attribute("href")

            product_list.append({
                "상품명": name,
                "현재 가격": price,
                "원래 가격": original_price,
                "할인율": discount,
                "품절 여부": is_sold_out,
                "무게/단위": weight,
                "상품 구매 URL": product_url
            })
        except Exception as e:
            continue # 데이터가 불완전한 상품은 건너뜀

    return product_list

# 실행
target_url = "https://www.zepto.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3"
data = crawl_zepto_products(target_url)

# 데이터프레임 변환 및 저장
# 1. 저장할 디렉토리 설정 및 생성
save_dir = "crawling/online-platform/results/zepto"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 2. 오늘 날짜 가져오기
today_date = datetime.now().strftime("%y%m%d") # 251218

# 3. 파일 순번(Execution Count) 계산
# 해당 폴더 내의 .csv 파일 개수를 확인하여 다음 번호를 부여합니다.
existing_files = [f for f in os.listdir(save_dir) if f.endswith(".csv")]
run_count = len(existing_files) + 1

# 4. 파일명 조합 (순번_zepto_날짜.csv)
# :02d는 숫자를 두 자리로 맞춤 (예: 1 -> 01, 10 -> 10)
file_name = f"{run_count:02d}_zepto_{today_date}.csv"
save_path = os.path.join(save_dir, file_name)

# 5. 데이터프레임 변환 및 저장
df = pd.DataFrame(data)
df.to_csv(save_path, index=False, encoding="utf-8-sig")

print("-" * 30)
print(f"✅ 저장 완료: {save_path}")
print(f"📊 수집된 상품 개수: {len(df)}개")
print("-" * 30)

driver.quit()