import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from app.config import settings

# Firebase 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "app/dang-doctor-firebase-adminsdk-fbsvc-062bcd6744.json")

def initialize_firebase():
    """Firebase 초기화"""
    try:
        # 이미 초기화되었는지 확인
        firebase_admin.get_app()
    except ValueError:
        # 서비스 계정 키 파일 사용
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase 연결 성공: dang-doctor 프로젝트")
        else:
            raise ValueError(f"Firebase 서비스 계정 키 파일을 찾을 수 없습니다: {SERVICE_ACCOUNT_KEY}")

def get_firestore_db():
    """Firestore 데이터베이스 인스턴스 반환"""
    initialize_firebase()
    return firestore.client()

def verify_firebase_token(id_token: str):
    """Firebase ID 토큰 검증 (시계 오차 허용)"""
    try:
        initialize_firebase()
        # 시계 오차를 10초까지 허용
        decoded_token = auth.verify_id_token(id_token, check_revoked=False, clock_skew_seconds=10)
        return decoded_token
    except Exception as e:
        raise ValueError(f"토큰 검증 실패: {str(e)}") 