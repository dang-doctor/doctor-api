from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.firebase_config import get_firestore_db
from app.config import settings
import firebase_admin
from firebase_admin import firestore

router = APIRouter()

class UserProfile(BaseModel):
    user_id: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    gender: Optional[str] = None  # "남자", "여자"
    height: Optional[float] = None  # 키 (cm)
    weight: Optional[float] = None  # 몸무게 (kg)
    activity_level: Optional[str] = None  # "가벼운활동", "보통활동", "힘든활동"
    carb_ratio: Optional[float] = None  # 탄수화물 비율 (%)
    protein_ratio: Optional[float] = None  # 단백질 비율 (%)
    fat_ratio: Optional[float] = None  # 지방 비율 (%)
    created_at: str
    updated_at: str

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[str] = None
    carb_ratio: Optional[float] = None
    protein_ratio: Optional[float] = None
    fat_ratio: Optional[float] = None

class BloodSugarSummary(BaseModel):
    total_records: int
    average_blood_sugar: float
    meal_type_counts: Dict[str, int]
    recent_records: List[Dict[str, Any]]

class UserDashboard(BaseModel):
    user_profile: UserProfile
    blood_sugar_summary: BloodSugarSummary
    total_days: int

class NutritionCalculation(BaseModel):
    daily_calories: float  # 하루 섭취열량 (kcal)
    carbohydrates: float   # 탄수화물 (g)
    protein: float        # 단백질 (g)
    fat: float           # 지방 (g)
    calculation_details: dict  # 계산 과정 상세 정보

class NutritionCalculationRequest(BaseModel):
    height: float        # 키 (cm)
    gender: str         # 성별 ("남자" 또는 "여자")
    activity_level: str # 활동수준 ("가벼운활동", "보통활동", "힘든활동")
    carb_ratio: float   # 탄수화물 비율 (%)
    protein_ratio: float # 단백질 비율 (%)
    fat_ratio: float    # 지방 비율 (%)

async def get_current_user_id(authorization: str = Header(None)):
    """현재 로그인한 사용자 ID 가져오기"""
    # 개발자 모드에서는 토큰 없이도 허용
    if settings.DEV_MODE:
        return "dev_user_123"
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 필요합니다")
    
    try:
        # 실제 Firebase 토큰 검증
        from app.services.firebase_auth_service import verify_user_token
        token = authorization.split(" ")[1]
        decoded_token = await verify_user_token(token)
        return decoded_token.get("uid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {str(e)}")

async def get_user_by_kakao_id(kakao_id: str):
    """kakao_id로 사용자 정보 조회"""
    try:
        db = get_firestore_db()
        user_doc = db.collection('users').document(kakao_id).get()
        
        if not user_doc.exists:
            return None
        
        return user_doc.to_dict()
    except Exception:
        return None

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(user_id: str = Depends(get_current_user_id)):
    """사용자 프로필 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return UserProfile(
                user_id=user_id,
                email="dev@example.com",
                nickname="개발자",
                profile_image="https://example.com/profile.jpg",
                gender="남자",
                height=175.0,
                weight=70.0,
                activity_level="보통활동",
                carb_ratio=50.0,
                protein_ratio=25.0,
                fat_ratio=25.0,
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-15T12:00:00"
            )
        
        # Firebase에서 사용자 정보 조회
        db = get_firestore_db()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        user_data = user_doc.to_dict()
        
        return UserProfile(
            user_id=user_id,
            email=user_data.get('email'),
            nickname=user_data.get('nickname'),
            profile_image=user_data.get('profile_image'),
            gender=user_data.get('gender'),
            height=user_data.get('height'),
            weight=user_data.get('weight'),
            activity_level=user_data.get('activity_level'),
            carb_ratio=user_data.get('carb_ratio'),
            protein_ratio=user_data.get('protein_ratio'),
            fat_ratio=user_data.get('fat_ratio'),
            created_at=user_data.get('created_at', '').isoformat() if hasattr(user_data.get('created_at'), 'isoformat') else str(user_data.get('created_at', '')),
            updated_at=user_data.get('updated_at', '').isoformat() if hasattr(user_data.get('updated_at'), 'isoformat') else str(user_data.get('updated_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 프로필 조회 실패: {str(e)}")

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserProfileUpdate, 
    user_id: str = Depends(get_current_user_id)
):
    """사용자 프로필 수정"""
    try:
        # 데이터 검증
        if profile_data.gender and profile_data.gender not in ["남자", "여자"]:
            raise HTTPException(status_code=400, detail="성별은 '남자' 또는 '여자'여야 합니다")
        
        if profile_data.activity_level and profile_data.activity_level not in ["가벼운활동", "보통활동", "힘든활동"]:
            raise HTTPException(status_code=400, detail="활동수준은 '가벼운활동', '보통활동', '힘든활동' 중 하나여야 합니다")
        
        # 탄단지 비율 검증 (총합 100%인지 확인)
        if any([profile_data.carb_ratio, profile_data.protein_ratio, profile_data.fat_ratio]):
            total_ratio = (profile_data.carb_ratio or 0) + (profile_data.protein_ratio or 0) + (profile_data.fat_ratio or 0)
            if abs(total_ratio - 100.0) > 0.1:  # 0.1% 오차 허용
                raise HTTPException(status_code=400, detail="탄단지 비율의 총합은 100%여야 합니다")
        
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return UserProfile(
                user_id=user_id,
                email="dev@example.com",
                nickname=profile_data.nickname or "개발자",
                profile_image="https://example.com/profile.jpg",
                gender=profile_data.gender or "남자",
                height=profile_data.height or 175.0,
                weight=profile_data.weight or 70.0,
                activity_level=profile_data.activity_level or "보통활동",
                carb_ratio=profile_data.carb_ratio or 50.0,
                protein_ratio=profile_data.protein_ratio or 25.0,
                fat_ratio=profile_data.fat_ratio or 25.0,
                created_at="2024-01-01T00:00:00",
                updated_at=datetime.now().isoformat()
            )
        
        # Firebase에서 사용자 정보 업데이트
        db = get_firestore_db()
        user_ref = db.collection('users').document(user_id)
        
        # 기존 데이터 조회
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        existing_data = user_doc.to_dict()
        
        # 업데이트할 데이터 준비
        update_data = {}
        if profile_data.nickname is not None:
            update_data['nickname'] = profile_data.nickname
        if profile_data.gender is not None:
            update_data['gender'] = profile_data.gender
        if profile_data.height is not None:
            update_data['height'] = profile_data.height
        if profile_data.weight is not None:
            update_data['weight'] = profile_data.weight
        if profile_data.activity_level is not None:
            update_data['activity_level'] = profile_data.activity_level
        if profile_data.carb_ratio is not None:
            update_data['carb_ratio'] = profile_data.carb_ratio
        if profile_data.protein_ratio is not None:
            update_data['protein_ratio'] = profile_data.protein_ratio
        if profile_data.fat_ratio is not None:
            update_data['fat_ratio'] = profile_data.fat_ratio
        
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # 데이터 업데이트
        user_ref.update(update_data)
        
        # 업데이트된 데이터 조회
        updated_doc = user_ref.get()
        updated_data = updated_doc.to_dict()
        
        return UserProfile(
            user_id=user_id,
            email=updated_data.get('email'),
            nickname=updated_data.get('nickname'),
            profile_image=updated_data.get('profile_image'),
            gender=updated_data.get('gender'),
            height=updated_data.get('height'),
            weight=updated_data.get('weight'),
            activity_level=updated_data.get('activity_level'),
            carb_ratio=updated_data.get('carb_ratio'),
            protein_ratio=updated_data.get('protein_ratio'),
            fat_ratio=updated_data.get('fat_ratio'),
            created_at=updated_data.get('created_at', '').isoformat() if hasattr(updated_data.get('created_at'), 'isoformat') else str(updated_data.get('created_at', '')),
            updated_at=updated_data.get('updated_at', '').isoformat() if hasattr(updated_data.get('updated_at'), 'isoformat') else str(updated_data.get('updated_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 프로필 수정 실패: {str(e)}")

def calculate_nutrition_requirements(
    height_cm: float,
    gender: str,
    activity_level: str,
    carb_ratio: float,
    protein_ratio: float,
    fat_ratio: float
) -> NutritionCalculation:
    """영양 요구량 계산"""
    
    # 키를 m로 변환
    height_m = height_cm / 100
    
    # 성별에 따른 표준체중 계수
    gender_coefficient = 22 if gender == "남자" else 21
    
    # 표준체중 계산
    standard_weight = height_m ** 2 * gender_coefficient
    
    # 활동별 열량 계수 (중간값 사용)
    activity_coefficients = {
        "가벼운활동": 27.5,  # 25~30의 중간값
        "보통활동": 32.5,   # 30~35의 중간값
        "힘든활동": 37.5    # 35~40의 중간값
    }
    
    activity_coefficient = activity_coefficients.get(activity_level, 32.5)
    
    # 하루 섭취열량 계산
    daily_calories = standard_weight * activity_coefficient
    
    # 탄단지 계산 (g 단위)
    carbohydrates = (daily_calories * carb_ratio / 100) / 4
    protein = (daily_calories * protein_ratio / 100) / 4
    fat = (daily_calories * fat_ratio / 100) / 9  # 지방은 1g당 9kcal
    
    # 계산 과정 상세 정보
    calculation_details = {
        "height_cm": height_cm,
        "height_m": round(height_m, 2),
        "gender": gender,
        "gender_coefficient": gender_coefficient,
        "standard_weight_kg": round(standard_weight, 1),
        "activity_level": activity_level,
        "activity_coefficient": activity_coefficient,
        "daily_calories_formula": f"{round(standard_weight, 1)} × {activity_coefficient}",
        "carb_ratio": carb_ratio,
        "protein_ratio": protein_ratio,
        "fat_ratio": fat_ratio
    }
    
    return NutritionCalculation(
        daily_calories=round(daily_calories, 1),
        carbohydrates=round(carbohydrates, 1),
        protein=round(protein, 1),
        fat=round(fat, 1),
        calculation_details=calculation_details
    )

@router.post("/nutrition/calculate", response_model=NutritionCalculation)
async def calculate_nutrition(
    request: NutritionCalculationRequest
):
    """영양 요구량 계산"""
    try:
        # 데이터 검증
        if request.gender not in ["남자", "여자"]:
            raise HTTPException(status_code=400, detail="성별은 '남자' 또는 '여자'여야 합니다")
        
        if request.activity_level not in ["가벼운활동", "보통활동", "힘든활동"]:
            raise HTTPException(status_code=400, detail="활동수준은 '가벼운활동', '보통활동', '힘든활동' 중 하나여야 합니다")
        
        # 탄단지 비율 검증 (총합 100%인지 확인)
        total_ratio = request.carb_ratio + request.protein_ratio + request.fat_ratio
        if abs(total_ratio - 100.0) > 0.1:  # 0.1% 오차 허용
            raise HTTPException(status_code=400, detail="탄단지 비율의 총합은 100%여야 합니다")
        
        # 영양 계산
        nutrition = calculate_nutrition_requirements(
            height_cm=request.height,
            gender=request.gender,
            activity_level=request.activity_level,
            carb_ratio=request.carb_ratio,
            protein_ratio=request.protein_ratio,
            fat_ratio=request.fat_ratio
        )
        
        return nutrition
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영양 계산 실패: {str(e)}")

@router.post("/nutrition/calculate-from-profile", response_model=NutritionCalculation)
async def calculate_nutrition_from_profile(user_id: str = Depends(get_current_user_id)):
    """사용자 프로필 정보로 영양 요구량 계산"""
    try:
        # 사용자 프로필 정보 조회
        db = get_firestore_db()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        user_data = user_doc.to_dict()
        
        # 필수 정보 확인
        required_fields = ['height', 'gender', 'activity_level', 'carb_ratio', 'protein_ratio', 'fat_ratio']
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"프로필에 다음 정보가 필요합니다: {', '.join(missing_fields)}"
            )
        
        # 영양 계산
        nutrition = calculate_nutrition_requirements(
            height_cm=user_data['height'],
            gender=user_data['gender'],
            activity_level=user_data['activity_level'],
            carb_ratio=user_data['carb_ratio'],
            protein_ratio=user_data['protein_ratio'],
            fat_ratio=user_data['fat_ratio']
        )
        
        return nutrition
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영양 계산 실패: {str(e)}")

@router.get("/dashboard", response_model=UserDashboard)
async def get_user_dashboard(user_id: str = Depends(get_current_user_id)):
    """사용자 대시보드 데이터 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return UserDashboard(
                user_profile=UserProfile(
                    user_id=user_id,
                    email="dev@example.com",
                    nickname="개발자",
                    profile_image="https://example.com/profile.jpg",
                    gender="남자",
                    height=175.0,
                    weight=70.0,
                    activity_level="보통활동",
                    carb_ratio=50.0,
                    protein_ratio=25.0,
                    fat_ratio=25.0,
                    created_at="2024-01-01T00:00:00",
                    updated_at="2024-01-15T12:00:00"
                ),
                blood_sugar_summary=BloodSugarSummary(
                    total_records=15,
                    average_blood_sugar=118.5,
                    meal_type_counts={
                        "기상직후": 3,
                        "아침": 5,
                        "점심": 4,
                        "저녁": 3
                    },
                    recent_records=[
                        {
                            "id": "dev_1",
                            "blood_sugar": 120,
                            "meal_type": "아침",
                            "date": "2024-01-15",
                            "time": "08:30"
                        },
                        {
                            "id": "dev_2",
                            "blood_sugar": 95,
                            "meal_type": "점심",
                            "date": "2024-01-15",
                            "time": "12:30"
                        }
                    ]
                ),
                total_days=7
            )
        
        # Firebase에서 데이터 조회
        db = get_firestore_db()
        
        # 사용자 정보 조회
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        user_data = user_doc.to_dict()
        user_profile = UserProfile(
            user_id=user_id,
            email=user_data.get('email'),
            nickname=user_data.get('nickname'),
            profile_image=user_data.get('profile_image'),
            gender=user_data.get('gender'),
            height=user_data.get('height'),
            weight=user_data.get('weight'),
            activity_level=user_data.get('activity_level'),
            carb_ratio=user_data.get('carb_ratio'),
            protein_ratio=user_data.get('protein_ratio'),
            fat_ratio=user_data.get('fat_ratio'),
            created_at=user_data.get('created_at', '').isoformat() if hasattr(user_data.get('created_at'), 'isoformat') else str(user_data.get('created_at', '')),
            updated_at=user_data.get('updated_at', '').isoformat() if hasattr(user_data.get('updated_at'), 'isoformat') else str(user_data.get('updated_at', ''))
        )
        
        # 혈당 데이터 조회
        blood_sugar_docs = db.collection('blood_sugar').where('user_id', '==', user_id).stream()
        
        blood_sugar_records = []
        meal_type_counts = {"기상직후": 0, "아침": 0, "점심": 0, "저녁": 0}
        total_blood_sugar = 0
        
        for doc in blood_sugar_docs:
            data = doc.to_dict()
            blood_sugar_records.append({
                "id": doc.id,
                "blood_sugar": data['blood_sugar'],
                "meal_type": data['meal_type'],
                "date": data['date'],
                "time": data['time']
            })
            
            meal_type_counts[data['meal_type']] += 1
            total_blood_sugar += data['blood_sugar']
        
        # 최근 5개 기록만 반환
        recent_records = sorted(blood_sugar_records, key=lambda x: (x['date'], x['time']), reverse=True)[:5]
        
        average_blood_sugar = total_blood_sugar / len(blood_sugar_records) if blood_sugar_records else 0
        
        blood_sugar_summary = BloodSugarSummary(
            total_records=len(blood_sugar_records),
            average_blood_sugar=round(average_blood_sugar, 1),
            meal_type_counts=meal_type_counts,
            recent_records=recent_records
        )
        
        # 총 기록 일수 계산
        unique_dates = set(record['date'] for record in blood_sugar_records)
        total_days = len(unique_dates)
        
        return UserDashboard(
            user_profile=user_profile,
            blood_sugar_summary=blood_sugar_summary,
            total_days=total_days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 실패: {str(e)}")

@router.get("/blood-sugar/stats")
async def get_blood_sugar_statistics(user_id: str = Depends(get_current_user_id)):
    """혈당 통계 데이터 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return {
                "total_records": 15,
                "average_blood_sugar": 118.5,
                "highest_blood_sugar": 150,
                "lowest_blood_sugar": 85,
                "meal_type_averages": {
                    "기상직후": 110.0,
                    "아침": 125.0,
                    "점심": 115.0,
                    "저녁": 120.0
                },
                "weekly_trend": [
                    {"date": "2024-01-09", "average": 120},
                    {"date": "2024-01-10", "average": 118},
                    {"date": "2024-01-11", "average": 122},
                    {"date": "2024-01-12", "average": 115},
                    {"date": "2024-01-13", "average": 125},
                    {"date": "2024-01-14", "average": 118},
                    {"date": "2024-01-15", "average": 120}
                ]
            }
        
        # Firebase에서 통계 데이터 조회
        db = get_firestore_db()
        blood_sugar_docs = db.collection('blood_sugar').where('user_id', '==', user_id).stream()
        
        blood_sugar_records = []
        meal_type_totals = {"기상직후": [], "아침": [], "점심": [], "저녁": []}
        
        for doc in blood_sugar_docs:
            data = doc.to_dict()
            blood_sugar_records.append(data['blood_sugar'])
            meal_type_totals[data['meal_type']].append(data['blood_sugar'])
        
        if not blood_sugar_records:
            return {
                "total_records": 0,
                "average_blood_sugar": 0,
                "highest_blood_sugar": 0,
                "lowest_blood_sugar": 0,
                "meal_type_averages": {"기상직후": 0, "아침": 0, "점심": 0, "저녁": 0},
                "weekly_trend": []
            }
        
        # 통계 계산
        total_records = len(blood_sugar_records)
        average_blood_sugar = sum(blood_sugar_records) / total_records
        highest_blood_sugar = max(blood_sugar_records)
        lowest_blood_sugar = min(blood_sugar_records)
        
        meal_type_averages = {}
        for meal_type, values in meal_type_totals.items():
            meal_type_averages[meal_type] = sum(values) / len(values) if values else 0
        
        return {
            "total_records": total_records,
            "average_blood_sugar": round(average_blood_sugar, 1),
            "highest_blood_sugar": highest_blood_sugar,
            "lowest_blood_sugar": lowest_blood_sugar,
            "meal_type_averages": {k: round(v, 1) for k, v in meal_type_averages.items()},
            "weekly_trend": []  # 주간 트렌드는 복잡하므로 생략
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 통계 조회 실패: {str(e)}")

# kakao_id로 직접 접근하는 엔드포인트들
@router.get("/kakao/{kakao_id}/profile", response_model=UserProfile)
async def get_user_profile_by_kakao_id(kakao_id: str):
    """kakao_id로 사용자 상세 프로필 조회"""
    try:
        # kakao_id로 사용자 정보 조회
        user_data = await get_user_by_kakao_id(kakao_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return UserProfile(
            user_id=kakao_id,
            email=user_data.get('email'),
            nickname=user_data.get('nickname'),
            profile_image=user_data.get('profile_image'),
            gender=user_data.get('gender'),
            height=user_data.get('height'),
            weight=user_data.get('weight'),
            activity_level=user_data.get('activity_level'),
            carb_ratio=user_data.get('carb_ratio'),
            protein_ratio=user_data.get('protein_ratio'),
            fat_ratio=user_data.get('fat_ratio'),
            created_at=user_data.get('created_at', '').isoformat() if hasattr(user_data.get('created_at'), 'isoformat') else str(user_data.get('created_at', '')),
            updated_at=user_data.get('updated_at', '').isoformat() if hasattr(user_data.get('updated_at'), 'isoformat') else str(user_data.get('updated_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 프로필 조회 실패: {str(e)}")

@router.put("/kakao/{kakao_id}/profile", response_model=UserProfile)
async def update_user_profile_by_kakao_id(
    kakao_id: str, 
    profile_data: UserProfileUpdate
):
    """kakao_id로 사용자 상세 프로필 수정"""
    try:
        # 데이터 검증
        if profile_data.gender and profile_data.gender not in ["남자", "여자"]:
            raise HTTPException(status_code=400, detail="성별은 '남자' 또는 '여자'여야 합니다")
        
        if profile_data.activity_level and profile_data.activity_level not in ["가벼운활동", "보통활동", "힘든활동"]:
            raise HTTPException(status_code=400, detail="활동수준은 '가벼운활동', '보통활동', '힘든활동' 중 하나여야 합니다")
        
        # 탄단지 비율 검증 (총합 100%인지 확인)
        if any([profile_data.carb_ratio, profile_data.protein_ratio, profile_data.fat_ratio]):
            total_ratio = (profile_data.carb_ratio or 0) + (profile_data.protein_ratio or 0) + (profile_data.fat_ratio or 0)
            if abs(total_ratio - 100.0) > 0.1:  # 0.1% 오차 허용
                raise HTTPException(status_code=400, detail="탄단지 비율의 총합은 100%여야 합니다")
        
        # Firebase에서 사용자 정보 업데이트
        db = get_firestore_db()
        user_ref = db.collection('users').document(kakao_id)
        
        # 기존 데이터 조회
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        # 업데이트할 데이터 준비
        update_data = {}
        if profile_data.nickname is not None:
            update_data['nickname'] = profile_data.nickname
        if profile_data.gender is not None:
            update_data['gender'] = profile_data.gender
        if profile_data.height is not None:
            update_data['height'] = profile_data.height
        if profile_data.weight is not None:
            update_data['weight'] = profile_data.weight
        if profile_data.activity_level is not None:
            update_data['activity_level'] = profile_data.activity_level
        if profile_data.carb_ratio is not None:
            update_data['carb_ratio'] = profile_data.carb_ratio
        if profile_data.protein_ratio is not None:
            update_data['protein_ratio'] = profile_data.protein_ratio
        if profile_data.fat_ratio is not None:
            update_data['fat_ratio'] = profile_data.fat_ratio
        
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # 데이터 업데이트
        user_ref.update(update_data)
        
        # 업데이트된 데이터 조회
        updated_doc = user_ref.get()
        updated_data = updated_doc.to_dict()
        
        return UserProfile(
            user_id=kakao_id,
            email=updated_data.get('email'),
            nickname=updated_data.get('nickname'),
            profile_image=updated_data.get('profile_image'),
            gender=updated_data.get('gender'),
            height=updated_data.get('height'),
            weight=updated_data.get('weight'),
            activity_level=updated_data.get('activity_level'),
            carb_ratio=updated_data.get('carb_ratio'),
            protein_ratio=updated_data.get('protein_ratio'),
            fat_ratio=updated_data.get('fat_ratio'),
            created_at=updated_data.get('created_at', '').isoformat() if hasattr(updated_data.get('created_at'), 'isoformat') else str(updated_data.get('created_at', '')),
            updated_at=updated_data.get('updated_at', '').isoformat() if hasattr(updated_data.get('updated_at'), 'isoformat') else str(updated_data.get('updated_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 프로필 수정 실패: {str(e)}") 