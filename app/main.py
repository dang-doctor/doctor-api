from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import firebase_auth, blood_sugar, user_profile, meals

app = FastAPI(title="Doctor API (Firebase)", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 기반 라우터 등록
app.include_router(firebase_auth.router, prefix="/auth", tags=["인증"])
app.include_router(blood_sugar.router, prefix="/blood-sugar", tags=["혈당"])
app.include_router(user_profile.router, prefix="/user", tags=["마이페이지"])
app.include_router(meals.router, prefix="/meals", tags=["식단"])

@app.get("/")
async def root():
    return {"message": "Firebase 기반 Doctor API에 오신 것을 환영합니다!"}

