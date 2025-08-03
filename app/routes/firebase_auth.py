from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse
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
        redirect_uri = "https://449d83cd1d08.ngrok-free.app/auth/kakao/callback"
        print(f"DEBUG: redirect_uri = {redirect_uri}")
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
            "message": "카카오 로그인 실패"
        }, status_code=400)

@router.post("/kakao/code")
async def kakao_login_with_code(code: str, redirect_uri: str = "https://449d83cd1d08.ngrok-free.app/auth/kakao/callback"):
    """카카오 인증 코드로 로그인"""
    try:
        # 1. 인증 코드를 액세스 토큰으로 교환
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