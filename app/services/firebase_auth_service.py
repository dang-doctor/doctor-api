import httpx
from firebase_admin import firestore
from app.firebase_config import get_firestore_db, verify_firebase_token
from app.config import settings

async def exchange_kakao_code_for_token(code: str, redirect_uri: str) -> str:
    """카카오 인증 코드를 액세스 토큰으로 교환"""
    token_url = settings.KAKAO_TOKEN_API
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "client_secret": settings.KAKAO_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri
    }
    
    print(f"DEBUG: 카카오 토큰 교환 시도")
    print(f"DEBUG: client_id = {settings.KAKAO_CLIENT_ID}")
    print(f"DEBUG: client_secret = {settings.KAKAO_CLIENT_SECRET[:10]}...")
    print(f"DEBUG: code = {code[:10]}...")
    print(f"DEBUG: redirect_uri = {redirect_uri}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        
    print(f"DEBUG: 응답 상태 코드 = {response.status_code}")
    print(f"DEBUG: 응답 내용 = {response.text}")
        
    if response.status_code != 200:
        raise Exception(f"토큰 교환 실패: {response.text}")
    
    token_data = response.json()
    return token_data.get("access_token")

async def kakao_login_with_firebase(access_token: str) -> dict:
    """카카오 로그인 후 Firebase에 사용자 정보 저장"""
    # 1. 카카오 API로 사용자 정보 가져오기
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(settings.KAKAO_USER_API, headers=headers)
    
    if res.status_code != 200:
        raise Exception("카카오 인증 실패")
    
    kakao_data = res.json()
    kakao_id = str(kakao_data["id"])
    
    # 2. 카카오 사용자 정보 추출
    kakao_account = kakao_data.get("kakao_account", {})
    profile = kakao_account.get("profile", {})
    
    user_data = {
        "kakao_id": kakao_id,
        "email": kakao_account.get("email"),
        "nickname": profile.get("nickname"),
        "profile_image": profile.get("profile_image_url"),
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }
    
    # 개발 모드에서는 Firebase 없이 사용자 정보만 반환
    if settings.DEV_MODE:
        print(f"DEBUG: 개발 모드 - Firebase 없이 사용자 정보 반환")
        return {
            "user_id": kakao_id,
            "email": user_data.get("email"),
            "nickname": user_data.get("nickname"),
            "profile_image": user_data.get("profile_image")
        }
    
    # 3. Firestore에 사용자 정보 저장/업데이트
    db = get_firestore_db()
    user_ref = db.collection('users').document(kakao_id)
    
    # 기존 사용자 확인
    user_doc = user_ref.get()
    if user_doc.exists:
        # 기존 사용자 업데이트
        user_ref.update({
            "nickname": user_data["nickname"],
            "profile_image": user_data["profile_image"],
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        user_data = user_doc.to_dict()
    else:
        # 새 사용자 생성
        user_ref.set(user_data)
    
    # 4. Firebase 커스텀 토큰 자동 생성
    try:
        from firebase_admin import auth
        custom_token = auth.create_custom_token(kakao_id)
        
        return {
            "user_id": kakao_id,
            "email": user_data.get("email"),
            "nickname": user_data.get("nickname"),
            "profile_image": user_data.get("profile_image"),
            "firebase_token": custom_token.decode()  # 자동으로 토큰 포함
        }
    except Exception as token_error:
        print(f"Firebase 토큰 생성 실패: {str(token_error)}")
        return {
            "user_id": kakao_id,
            "email": user_data.get("email"),
            "nickname": user_data.get("nickname"),
            "profile_image": user_data.get("profile_image")
        }

async def verify_user_token(token: str) -> dict:
    """Firebase ID 토큰으로 사용자 검증"""
    try:
        decoded_token = verify_firebase_token(token)
        user_id = decoded_token.get("uid")
        
        # Firestore에서 사용자 정보 가져오기
        db = get_firestore_db()
        user_doc = db.collection('users').document(user_id).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # kakao_id 추가
            user_data["kakao_id"] = user_id
            return user_data
        else:
            raise ValueError("사용자를 찾을 수 없습니다")
            
    except Exception as e:
        raise ValueError(f"토큰 검증 실패: {str(e)}") 