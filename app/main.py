from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import firebase_auth, blood_sugar, user_profile, meals, stats, foods, ml

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
app.include_router(stats.router, prefix="/stats", tags=["통계"])
app.include_router(foods.router, prefix="/foods", tags=["음식"])
app.include_router(ml.router, prefix="/ml", tags=["ML"])

@app.get("/")
async def root():
    return {"message": "Firebase 기반 Doctor API에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    """Firebase 연결 상태 확인"""
    try:
        from app.firebase_config import get_firestore_db
        db = get_firestore_db()
        # 간단한 쿼리로 연결 테스트
        test_query = db.collection("_health_check").limit(1).stream()
        list(test_query)  # 쿼리 실행
        return {
            "status": "healthy",
            "firebase": "connected",
            "project_id": "dang-doctor",
            "message": "Firebase 연결 성공"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "firebase": "disconnected",
            "error": str(e),
            "message": "Firebase 연결 실패 - 서비스 계정 키 파일을 확인해주세요"
        }

