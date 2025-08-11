from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.firebase_config import get_firestore_db
from app.config import settings
from firebase_admin import firestore
import uuid

router = APIRouter()

class MealAnalysis(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    carbs: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None

class MealResponse(BaseModel):
    id: str
    user_id: str
    date: str
    time: str
    notes: Optional[str] = None
    image_filename: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    analysis: MealAnalysis
    created_at: str

class ManualMealCreate(BaseModel):
    name: str
    calories: float
    carbs: float
    protein: float
    fat: float
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    notes: Optional[str] = None

async def get_current_user_id(authorization: str = Header(None)) -> str:
    if settings.DEV_MODE:
        return "dev_user_123"
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 필요합니다")
    try:
        from app.services.firebase_auth_service import verify_user_token
        token = authorization.split(" ")[1]
        decoded_token = await verify_user_token(token)
        return decoded_token.get("uid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {str(e)}")

def _validate_date_time(date_str: str, time_str: str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        datetime.strptime(time_str, "%H:%M")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"날짜/시간 형식 오류: {str(e)}")

@router.post("/upload", response_model=MealResponse)
async def upload_meal_image(
    image: UploadFile = File(...),
    date: str = Form(...),
    time: str = Form(...),
    notes: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    """음식 이미지 업로드 (multipart/form-data)"""
    _validate_date_time(date, time)

    # 간단한 분석 더미/플레이스홀더
    if settings.DEV_MODE:
        analysis = MealAnalysis(
            name="비빔밥",
            calories=650.0,
            carbs=85.0,
            protein=20.0,
            fat=20.0,
        )
    else:
        analysis = MealAnalysis(name=None, calories=None, carbs=None, protein=None, fat=None)

    # Firestore 저장
    if settings.DEV_MODE:
        created_at_str = datetime.now().isoformat()
        return MealResponse(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date,
            time=time,
            notes=notes,
            image_filename=image.filename,
            content_type=image.content_type,
            size_bytes=0,
            analysis=analysis,
            created_at=created_at_str,
        )

    db = get_firestore_db()
    meal_doc = {
        "user_id": user_id,
        "date": date,
        "time": time,
        "notes": notes,
        "image_filename": image.filename,
        "content_type": image.content_type,
        "size_bytes": None,
        "analysis": analysis.model_dump(),
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    doc_ref = db.collection("meals").add(meal_doc)
    return MealResponse(
        id=doc_ref[1].id,
        user_id=user_id,
        date=date,
        time=time,
        notes=notes,
        image_filename=image.filename,
        content_type=image.content_type,
        size_bytes=None,
        analysis=analysis,
        created_at=datetime.now().isoformat(),
    )

@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal(meal_id: str, user_id: str = Depends(get_current_user_id)):
    """분석 결과 조회 (예: 음식명, 칼로리, 탄단지 등)"""
    if settings.DEV_MODE:
        return MealResponse(
            id=meal_id,
            user_id=user_id,
            date="2024-08-01",
            time="12:15",
            notes="개발 모드 더미",
            image_filename="lunch.jpg",
            content_type="image/jpeg",
            size_bytes=123456,
            analysis=MealAnalysis(name="치킨샐러드", calories=420.0, carbs=15.0, protein=35.0, fat=22.0),
            created_at=datetime.now().isoformat(),
        )

    db = get_firestore_db()
    doc = db.collection("meals").document(meal_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="식단을 찾을 수 없습니다")
    data = doc.to_dict()
    if data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
    analysis = MealAnalysis(**(data.get("analysis") or {}))
    return MealResponse(
        id=meal_id,
        user_id=data["user_id"],
        date=data["date"],
        time=data["time"],
        notes=data.get("notes"),
        image_filename=data.get("image_filename"),
        content_type=data.get("content_type"),
        size_bytes=data.get("size_bytes"),
        analysis=analysis,
        created_at=(data.get("created_at").isoformat() if hasattr(data.get("created_at"), "isoformat") else str(data.get("created_at"))),
    )

@router.post("/manual", response_model=MealResponse)
async def create_manual_meal(payload: ManualMealCreate, user_id: str = Depends(get_current_user_id)):
    """수동 식단 등록 (직접 입력)"""
    _validate_date_time(payload.date, payload.time)

    analysis = MealAnalysis(
        name=payload.name,
        calories=payload.calories,
        carbs=payload.carbs,
        protein=payload.protein,
        fat=payload.fat,
    )

    if settings.DEV_MODE:
        return MealResponse(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=payload.date,
            time=payload.time,
            notes=payload.notes,
            image_filename=None,
            content_type=None,
            size_bytes=None,
            analysis=analysis,
            created_at=datetime.now().isoformat(),
        )

    db = get_firestore_db()
    meal_doc = {
        "user_id": user_id,
        "date": payload.date,
        "time": payload.time,
        "notes": payload.notes,
        "image_filename": None,
        "content_type": None,
        "size_bytes": None,
        "analysis": analysis.model_dump(),
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    doc_ref = db.collection("meals").add(meal_doc)
    return MealResponse(
        id=doc_ref[1].id,
        user_id=user_id,
        date=payload.date,
        time=payload.time,
        notes=payload.notes,
        image_filename=None,
        content_type=None,
        size_bytes=None,
        analysis=analysis,
        created_at=datetime.now().isoformat(),
    )

@router.get("/history", response_model=List[MealResponse])
async def get_meal_history(
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """식단 기록 전체 조회 (날짜/시간 필터 가능)"""
    # 입력 검증 (있을 때만)
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"날짜 형식 오류: {str(e)}")
    if start_time:
        try:
            datetime.strptime(start_time, "%H:%M")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"시간 형식 오류(start_time): {str(e)}")
    if end_time:
        try:
            datetime.strptime(end_time, "%H:%M")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"시간 형식 오류(end_time): {str(e)}")

    if settings.DEV_MODE:
        dummy = [
            MealResponse(
                id=str(uuid.uuid4()),
                user_id=user_id,
                date="2024-08-01",
                time="08:15",
                notes="아침",
                image_filename="breakfast.jpg",
                content_type="image/jpeg",
                size_bytes=100000,
                analysis=MealAnalysis(name="시리얼", calories=320, carbs=60, protein=8, fat=5),
                created_at=datetime.now().isoformat(),
            ),
            MealResponse(
                id=str(uuid.uuid4()),
                user_id=user_id,
                date="2024-08-01",
                time="12:30",
                notes="점심",
                image_filename="lunch.jpg",
                content_type="image/jpeg",
                size_bytes=200000,
                analysis=MealAnalysis(name="비빔밥", calories=650, carbs=85, protein=20, fat=20),
                created_at=datetime.now().isoformat(),
            ),
        ]
        # 간단 필터링
        def match(item: MealResponse) -> bool:
            if date and item.date != date:
                return False
            if start_time and item.time < start_time:
                return False
            if end_time and item.time > end_time:
                return False
            return True
        return [m for m in dummy if match(m)]

    db = get_firestore_db()
    # 기본 쿼리: 사용자 기준
    docs = db.collection("meals").where("user_id", "==", user_id).stream()

    meals: List[MealResponse] = []
    for d in docs:
        data = d.to_dict()
        analysis = MealAnalysis(**(data.get("analysis") or {}))
        meal = MealResponse(
            id=d.id,
            user_id=data["user_id"],
            date=data["date"],
            time=data["time"],
            notes=data.get("notes"),
            image_filename=data.get("image_filename"),
            content_type=data.get("content_type"),
            size_bytes=data.get("size_bytes"),
            analysis=analysis,
            created_at=(data.get("created_at").isoformat() if hasattr(data.get("created_at"), "isoformat") else str(data.get("created_at"))),
        )
        meals.append(meal)

    # 정렬 및 필터링 (클라이언트측)
    meals.sort(key=lambda x: (x.date, x.time), reverse=True)
    if date:
        meals = [m for m in meals if m.date == date]
    if start_time:
        meals = [m for m in meals if m.time >= start_time]
    if end_time:
        meals = [m for m in meals if m.time <= end_time]

    return meals
