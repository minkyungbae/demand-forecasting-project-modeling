from xml.dom.pulldom import START_ELEMENT
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI() # 서버 설정은 된 상태

# React랑 통신을 위해서는 CORS 필수
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"], # 회사에 따라 달라져용
    allow_headers=["*"], # 회사에 따라 달라져용
)

@app.get("/")
def root():
    return {"message": "FastAPI 서버 정상 작동 중!"}

@app.get("/hello")
def hello(models: str = "Our Model can demand forecasting only Top 10 Products.", products: str = "Like Pet Treats, Toilet Cleaner, Lotion, Vitamins, Dish Soap, Baby Wipe, Cough Syrup, Cat Food, Pulses, Orange Juice 🥺 "):
    return {"message": f"{models}\n{products}"}