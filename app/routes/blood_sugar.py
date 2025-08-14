from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from app.firebase_config import get_firestore_db
from app.config import settings
import firebase_admin
from firebase_admin import firestore

router = APIRouter()

class BloodSugarData(BaseModel):
    blood_sugar: int  # 혈당 수치
    meal_type: str  # 기상직후, 아침, 점심, 저녁
    date: str  # YYYY-MM-DD 형식
    time: str  # HH:MM 형식
    notes: Optional[str] = None  # 메모

class BloodSugarResponse(BaseModel):
    id: str
    blood_sugar: int
    meal_type: str
    date: str
    time: str
    notes: Optional[str] = None
    created_at: str

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

@router.post("/", response_model=BloodSugarResponse)
async def create_blood_sugar(data: BloodSugarData, user_id: str = Depends(get_current_user_id)):
    """혈당 데이터 등록"""
    try:
        # 날짜 형식 검증
        datetime.strptime(data.date, "%Y-%m-%d")
        datetime.strptime(data.time, "%H:%M")
        
        # 식사 타입 검증
        valid_meal_types = ["기상직후", "아침", "점심", "저녁"]
        if data.meal_type not in valid_meal_types:
            raise HTTPException(status_code=400, detail=f"잘못된 식사 타입입니다. 가능한 값: {valid_meal_types}")
        
        # 혈당 수치 검증
        if data.blood_sugar < 0 or data.blood_sugar > 1000:
            raise HTTPException(status_code=400, detail="혈당 수치는 0-1000 사이여야 합니다")
        
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return BloodSugarResponse(
                id="dev_blood_sugar_123",
                blood_sugar=data.blood_sugar,
                meal_type=data.meal_type,
                date=data.date,
                time=data.time,
                notes=data.notes,
                created_at=datetime.now().isoformat()
            )
        
        # Firebase에 저장
        db = get_firestore_db()
        blood_sugar_data = {
            "user_id": user_id,
            "blood_sugar": data.blood_sugar,
            "meal_type": data.meal_type,
            "date": data.date,
            "time": data.time,
            "notes": data.notes,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('blood_sugar').add(blood_sugar_data)
        
        return BloodSugarResponse(
            id=doc_ref[1].id,
            blood_sugar=data.blood_sugar,
            meal_type=data.meal_type,
            date=data.date,
            time=data.time,
            notes=data.notes,
            created_at=datetime.now().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"날짜/시간 형식 오류: {str(e)}")

@router.get("/", response_model=List[BloodSugarResponse])
async def get_blood_sugar_list(user_id: str = Depends(get_current_user_id)):
    """사용자의 혈당 데이터 목록 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return [
                BloodSugarResponse(
                    id="dev_1",
                    blood_sugar=120,
                    meal_type="아침",
                    date="2024-01-15",
                    time="08:30",
                    notes="테스트",
                    created_at="2024-01-15T08:30:00"
                ),
                BloodSugarResponse(
                    id="dev_2",
                    blood_sugar=95,
                    meal_type="점심",
                    date="2024-01-15",
                    time="12:30",
                    notes="테스트",
                    created_at="2024-01-15T12:30:00"
                )
            ]
        
        # Firebase에서 사용자의 혈당 데이터 조회
        db = get_firestore_db()
        blood_sugar_docs = db.collection('blood_sugar').where('user_id', '==', user_id).stream()
        
        blood_sugar_list = []
        for doc in blood_sugar_docs:
            data = doc.to_dict()
            blood_sugar_list.append(BloodSugarResponse(
                id=doc.id,
                blood_sugar=data['blood_sugar'],
                meal_type=data['meal_type'],
                date=data['date'],
                time=data['time'],
                notes=data.get('notes'),
                created_at=data['created_at'].isoformat() if hasattr(data['created_at'], 'isoformat') else str(data['created_at'])
            ))
        
        return blood_sugar_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 데이터 조회 실패: {str(e)}")

@router.get("/health")
async def blood_sugar_health():
    """혈당 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "blood-sugar",
        "message": "혈당 서비스가 정상적으로 작동 중입니다"
    }

@router.get("/", response_model=List[BloodSugarResponse])
async def get_blood_sugar_list(
    date: Optional[str] = None,
    meal_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """혈당 데이터 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            dummy_data = [
                BloodSugarResponse(
                    id="dev_1",
                    blood_sugar=120,
                    meal_type="아침",
                    date="2024-01-15",
                    time="08:30",
                    notes="아침 식사 후",
                    created_at="2024-01-15T08:30:00"
                ),
                BloodSugarResponse(
                    id="dev_2",
                    blood_sugar=95,
                    meal_type="점심",
                    date="2024-01-15",
                    time="12:30",
                    notes="점심 식사 후",
                    created_at="2024-01-15T12:30:00"
                )
            ]
            return dummy_data
        
        # Firebase에서 조회
        db = get_firestore_db()
        query = db.collection('blood_sugar').where('user_id', '==', user_id)
        
        if date:
            query = query.where('date', '==', date)
        
        if meal_type:
            query = query.where('meal_type', '==', meal_type)
        
        docs = query.order_by('date', direction=firestore.Query.DESCENDING).order_by('time', direction=firestore.Query.DESCENDING).stream()
        
        blood_sugar_list = []
        for doc in docs:
            data = doc.to_dict()
            blood_sugar_list.append(BloodSugarResponse(
                id=doc.id,
                blood_sugar=data['blood_sugar'],
                meal_type=data['meal_type'],
                date=data['date'],
                time=data['time'],
                notes=data.get('notes'),
                created_at=data.get('created_at', '').isoformat() if hasattr(data.get('created_at'), 'isoformat') else str(data.get('created_at', ''))
            ))
        
        return blood_sugar_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 데이터 조회 실패: {str(e)}")

@router.get("/{blood_sugar_id}", response_model=BloodSugarResponse)
async def get_blood_sugar_detail(blood_sugar_id: str, user_id: str = Depends(get_current_user_id)):
    """특정 혈당 데이터 조회"""
    try:
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return BloodSugarResponse(
                id=blood_sugar_id,
                blood_sugar=120,
                meal_type="아침",
                date="2024-01-15",
                time="08:30",
                notes="아침 식사 후",
                created_at="2024-01-15T08:30:00"
            )
        
        # Firebase에서 조회
        db = get_firestore_db()
        doc = db.collection('blood_sugar').document(blood_sugar_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="혈당 데이터를 찾을 수 없습니다")
        
        data = doc.to_dict()
        if data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        return BloodSugarResponse(
            id=doc.id,
            blood_sugar=data['blood_sugar'],
            meal_type=data['meal_type'],
            date=data['date'],
            time=data['time'],
            notes=data.get('notes'),
            created_at=data.get('created_at', '').isoformat() if hasattr(data.get('created_at'), 'isoformat') else str(data.get('created_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 데이터 조회 실패: {str(e)}")

@router.put("/{blood_sugar_id}", response_model=BloodSugarResponse)
async def update_blood_sugar(
    blood_sugar_id: str, 
    data: BloodSugarData, 
    user_id: str = Depends(get_current_user_id)
):
    """혈당 데이터 수정"""
    try:
        # 날짜 형식 검증
        datetime.strptime(data.date, "%Y-%m-%d")
        datetime.strptime(data.time, "%H:%M")
        
        # 식사 타입 검증
        valid_meal_types = ["기상직후", "아침", "점심", "저녁"]
        if data.meal_type not in valid_meal_types:
            raise HTTPException(status_code=400, detail=f"잘못된 식사 타입입니다. 가능한 값: {valid_meal_types}")
        
        # 혈당 수치 검증
        if data.blood_sugar < 0 or data.blood_sugar > 1000:
            raise HTTPException(status_code=400, detail="혈당 수치는 0-1000 사이여야 합니다")
        
        # 개발자 모드에서는 더미 데이터 반환
        if settings.DEV_MODE:
            return BloodSugarResponse(
                id=blood_sugar_id,
                blood_sugar=data.blood_sugar,
                meal_type=data.meal_type,
                date=data.date,
                time=data.time,
                notes=data.notes,
                created_at=datetime.now().isoformat()
            )
        
        # Firebase에서 수정
        db = get_firestore_db()
        doc_ref = db.collection('blood_sugar').document(blood_sugar_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="혈당 데이터를 찾을 수 없습니다")
        
        doc_data = doc.to_dict()
        if doc_data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        update_data = {
            "blood_sugar": data.blood_sugar,
            "meal_type": data.meal_type,
            "date": data.date,
            "time": data.time,
            "notes": data.notes,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.update(update_data)
        
        return BloodSugarResponse(
            id=blood_sugar_id,
            blood_sugar=data.blood_sugar,
            meal_type=data.meal_type,
            date=data.date,
            time=data.time,
            notes=data.notes,
            created_at=datetime.now().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"날짜/시간 형식 오류: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 데이터 수정 실패: {str(e)}")

@router.delete("/{blood_sugar_id}")
async def delete_blood_sugar(blood_sugar_id: str, user_id: str = Depends(get_current_user_id)):
    """혈당 데이터 삭제"""
    try:
        # 개발자 모드에서는 더미 응답 반환
        if settings.DEV_MODE:
            return {"message": "혈당 데이터가 삭제되었습니다", "id": blood_sugar_id}
        
        # Firebase에서 삭제
        db = get_firestore_db()
        doc_ref = db.collection('blood_sugar').document(blood_sugar_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="혈당 데이터를 찾을 수 없습니다")
        
        doc_data = doc.to_dict()
        if doc_data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        doc_ref.delete()
        
        return {"message": "혈당 데이터가 삭제되었습니다", "id": blood_sugar_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"혈당 데이터 삭제 실패: {str(e)}")
