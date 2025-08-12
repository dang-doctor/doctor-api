from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from app.services.firebase_auth_service import kakao_login_with_firebase, verify_user_token, exchange_kakao_code_for_token

router = APIRouter()

@router.get("/kakao/callback")
async def kakao_callback(code: str = None, error: str = None):
    """카카오 로그인 콜백 처리"""
    print(f"DEBUG: 카카오 콜백 호출됨")
    print(f"DEBUG: code = {code}")
    print(f"DEBUG: error = {error}")
    
    if error:
        return JSONResponse(content={
            "success": False,
            "error": error,
            "message": "카카오 로그인 실패"
        }, status_code=400)
    
    if not code:
        return JSONResponse(content={
            "success": False,
            "error": "인증 코드가 없습니다",
            "message": "카카오 로그인 실패"
        }, status_code=400)
    
    try:
        # 1. 인증 코드를 액세스 토큰으로 교환
        from app.config import settings
        redirect_uri = settings.KAKAO_REDIRECT_URI
        print(f"DEBUG: redirect_uri = {redirect_uri}")
        print(f"DEBUG: 새로운 인증 코드로 토큰 교환 시도")
        
        access_token = await exchange_kakao_code_for_token(code, redirect_uri)
        
        # 2. 액세스 토큰으로 사용자 정보 가져오기
        user_data = await kakao_login_with_firebase(access_token)
        
        return JSONResponse(content={
            "success": True,
            "user": user_data,
            "message": "카카오 로그인 성공"
        })
    except Exception as e:
        print(f"DEBUG: 에러 발생 = {str(e)}")
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "message": "카카오 로그인 실패 - 새로운 인증 코드로 다시 시도해주세요"
        }, status_code=400)

@router.post("/kakao/code")
async def kakao_login_with_code(code: str, redirect_uri: str = None):
    """카카오 인증 코드로 로그인"""
    try:
        # 1. 인증 코드를 액세스 토큰으로 교환
        if not redirect_uri:
            from app.config import settings
            redirect_uri = settings.KAKAO_REDIRECT_URI
        access_token = await exchange_kakao_code_for_token(code, redirect_uri)
        
        # 2. 액세스 토큰으로 사용자 정보 가져오기
        user_data = await kakao_login_with_firebase(access_token)
        
        return JSONResponse(content={
            "success": True,
            "user": user_data,
            "message": "카카오 로그인 성공"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/kakao/login")
async def login_kakao_firebase(token: str):
    """카카오 액세스 토큰으로 로그인 (Firebase 기반)"""
    try:
        user_data = await kakao_login_with_firebase(token)
        return JSONResponse(content={
            "success": True,
            "user": user_data,
            "message": "카카오 로그인 성공"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user_firebase(
    authorization: str = Header(None)
):
    """현재 로그인한 사용자 정보 조회 (Firebase 토큰 필요)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 필요합니다")
    
    try:
        token = authorization.split(" ")[1]
        user_data = await verify_user_token(token)
        
        return {
            "success": True,
            "user": user_data
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")

@router.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "message": "Firebase 기반 Doctor API"}

@router.get("/kakao/login-url")
async def get_kakao_login_url():
    """카카오 로그인 URL 생성"""
    from app.config import settings
    
    # 카카오 로그인 URL 생성
    login_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    
    return {
        "login_url": login_url,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "client_id": settings.KAKAO_CLIENT_ID
    }

@router.get("/users")
async def get_all_users():
    """모든 사용자 목록 조회"""
    try:
        from app.firebase_config import get_firestore_db
        
        db = get_firestore_db()
        users_ref = db.collection('users')
        users = []
        
        for doc in users_ref.stream():
            user_data = doc.to_dict()
            users.append({
                "id": doc.id,
                "kakao_id": user_data.get("kakao_id"),
                "email": user_data.get("email"),
                "nickname": user_data.get("nickname"),
                "profile_image": user_data.get("profile_image"),
                "created_at": user_data.get("created_at"),
                "updated_at": user_data.get("updated_at")
            })
        
        return {
            "success": True,
            "total_users": len(users),
            "users": users
        }
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "message": "사용자 목록 조회 실패"
        }, status_code=500)

@router.put("/users/{kakao_id}/profile")
async def update_user_profile(kakao_id: str, profile_data: dict):
    """사용자 프로필 업데이트"""
    try:
        from app.firebase_config import get_firestore_db
        from firebase_admin import firestore
        
        db = get_firestore_db()
        user_ref = db.collection('users').document(kakao_id)
        
        # 사용자 존재 확인
        user_doc = user_ref.get()
        if not user_doc.exists:
            return JSONResponse(content={
                "success": False,
                "error": "사용자를 찾을 수 없습니다",
                "message": f"kakao_id {kakao_id}에 해당하는 사용자가 없습니다"
            }, status_code=404)
        
        # 업데이트할 데이터 준비
        update_data = {}
        if "nickname" in profile_data:
            update_data["nickname"] = profile_data["nickname"]
        if "email" in profile_data:
            update_data["email"] = profile_data["email"]
        if "profile_image" in profile_data:
            update_data["profile_image"] = profile_data["profile_image"]
        
        # updated_at 자동 설정
        update_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # 프로필 업데이트
        user_ref.update(update_data)
        
        # 업데이트된 사용자 정보 반환
        updated_doc = user_ref.get()
        updated_data = updated_doc.to_dict()
        
        return {
            "success": True,
            "message": "프로필 업데이트 성공",
            "user": {
                "kakao_id": updated_data.get("kakao_id"),
                "email": updated_data.get("email"),
                "nickname": updated_data.get("nickname"),
                "profile_image": updated_data.get("profile_image"),
                "updated_at": updated_data.get("updated_at")
            }
        }
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "message": "프로필 업데이트 실패"
        }, status_code=500)

@router.get("/users/{kakao_id}")
async def get_user_by_kakao_id(kakao_id: str):
    """kakao_id로 특정 사용자 조회"""
    try:
        from app.firebase_config import get_firestore_db
        
        db = get_firestore_db()
        user_ref = db.collection('users').document(kakao_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return JSONResponse(content={
                "success": False,
                "error": "사용자를 찾을 수 없습니다",
                "message": f"kakao_id {kakao_id}에 해당하는 사용자가 없습니다"
            }, status_code=404)
        
        user_data = user_doc.to_dict()
        return {
            "success": True,
            "user": {
                "kakao_id": user_data.get("kakao_id"),
                "email": user_data.get("email"),
                "nickname": user_data.get("nickname"),
                "profile_image": user_data.get("profile_image"),
                "created_at": user_data.get("created_at"),
                "updated_at": user_data.get("updated_at")
            }
        }
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "message": "사용자 조회 실패"
        }, status_code=500) 