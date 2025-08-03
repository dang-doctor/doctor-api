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
    
    # Firebase 설정
    FIREBASE_SERVICE_ACCOUNT_KEY: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    
    # 개발 모드 (Firebase 없이 테스트 가능)
    DEV_MODE: bool = os.getenv("DEV_MODE", "True").lower() == "true"
    
    # 앱 설정
    APP_NAME: str = os.getenv("APP_NAME", "Doctor API (Firebase)")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings() 