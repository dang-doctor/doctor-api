import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    # 카카오 API 설정
    KAKAO_USER_API: str = os.getenv("KAKAO_USER_API", "https://kapi.kakao.com/v2/user/me")
    KAKAO_TOKEN_API: str = os.getenv("KAKAO_TOKEN_API", "https://kauth.kakao.com/oauth/token")
    
    # 카카오 인증 정보
    KAKAO_CLIENT_ID: str = os.getenv("KAKAO_CLIENT_ID", "")
    KAKAO_CLIENT_SECRET: str = os.getenv("KAKAO_CLIENT_SECRET", "")
    
    # 디버깅: 환경변수 로딩 확인
    def __init__(self):
        print(f"🔍 환경변수 로딩 확인:")
        print(f"   KAKAO_CLIENT_ID: {self.KAKAO_CLIENT_ID[:10] if self.KAKAO_CLIENT_ID else 'None'}...")
        print(f"   KAKAO_CLIENT_SECRET: {self.KAKAO_CLIENT_SECRET[:10] if self.KAKAO_CLIENT_SECRET else 'None'}...")
        print(f"   KAKAO_REDIRECT_URI: {self.KAKAO_REDIRECT_URI}")
        print(f"   FIREBASE_WEB_API_KEY: {'set' if self.FIREBASE_WEB_API_KEY else 'None'}")
        print(f"   DEV_MODE: {self.DEV_MODE}")
    
    # 카카오 리다이렉트 URI (환경변수로 설정 가능)
    KAKAO_REDIRECT_URI: str = os.getenv("KAKAO_REDIRECT_URI", "https://aec0dea9bcc1.ngrok-free.app/auth/kakao/callback")
    
    # Firebase 설정
    FIREBASE_SERVICE_ACCOUNT_KEY: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    FIREBASE_WEB_API_KEY: Optional[str] = os.getenv("FIREBASE_WEB_API_KEY")
    
    # 개발 모드 (Firebase 없이 테스트 가능)
    DEV_MODE: bool = os.getenv("DEV_MODE", "False").lower() == "true"
    
    # 앱 설정
    APP_NAME: str = os.getenv("APP_NAME", "Doctor API (Firebase)")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings() 