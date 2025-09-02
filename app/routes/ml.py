# app/routes/ml.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.tflite_service import TFLiteModel

router = APIRouter()
# food_fp16.tflite 모델 1개만 사용
food_model = TFLiteModel("models/food_fp16.tflite")
# food_model = TFLiteModel("models/food_cls_fp16.tflite")

@router.post("/food")
async def infer_food(file: UploadFile = File(...)):
    """음식 이미지 분류 예측"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "이미지 파일만 업로드 가능")
    
    try:
        img = await file.read()
        result = food_model.predict(img)
        
        if result["success"]:
            return {
                "model": "food_fp16",
                "predicted_food": result["predicted_food"],
                "confidence": result["confidence"],
                "confidence_percentage": result["confidence_percentage"],
                "top_5_predictions": result["top_5_predictions"]
            }
        else:
            raise HTTPException(500, f"예측 실패: {result['error']}")
            
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise HTTPException(500, f"처리 오류: {str(e)}")

@router.get("/health")
async def ml_health():
    """ML 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "tflite-ml",
        "model": "food_fp16.tflite",
        "message": "TFLite 모델이 정상적으로 로드되었습니다"
    }