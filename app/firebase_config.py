import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from app.config import settings

# Firebase 서비스 계정 키 파일 경로 (나중에 설정)
SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "path/to/serviceAccountKey.json")

def initialize_firebase():
    """Firebase 초기화"""
    try:
        # 이미 초기화되었는지 확인
        firebase_admin.get_app()
    except ValueError:
        # 개발 모드인 경우 Firebase 없이 초기화
        if settings.DEV_MODE:
            print("🔥 개발 모드: Firebase 없이 실행 중")
            firebase_admin.initialize_app()
        elif os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
        else:
            # 기본 초기화 (환경변수 사용)
            firebase_admin.initialize_app()

def get_firestore_db():
    """Firestore 데이터베이스 인스턴스 반환"""
    initialize_firebase()
    return firestore.client()

def verify_firebase_token(id_token: str):
    """Firebase ID 토큰 검증"""
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        if settings.DEV_MODE:
            # 개발 모드에서는 더미 토큰 허용
            return {"uid": "dev_user_123", "email": "dev@example.com"}
        raise ValueError(f"토큰 검증 실패: {str(e)}") 