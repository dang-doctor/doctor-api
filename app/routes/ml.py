# app/routes/ml.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.tflite_service import TFLiteModel
import csv
import os

router = APIRouter()

# 모델은 서버 시작 시 바로 로드하지 않고, 첫 요청 시 지연 로드합니다.
_food_model = None
_food_model_path = "models/kfood30_mnv3_fp16.tflite"
_nutrition_csv_path = "app/data/food_nutrition_1.csv"
_nutrition_cache = None

def get_food_model() -> TFLiteModel:
    global _food_model
    if _food_model is None:
        try:
            _food_model = TFLiteModel(_food_model_path)
        except Exception as e:
            # 모델 로드 실패 시 503 반환
            raise HTTPException(503, f"TFLite 모델 로드 실패: {str(e)}")
    return _food_model

def get_nutrition_rows() -> list:
    global _nutrition_cache
    if _nutrition_cache is None:
        if not os.path.exists(_nutrition_csv_path):
            raise HTTPException(500, f"영양 CSV 파일을 찾을 수 없습니다: {_nutrition_csv_path}")
        rows = []
        with open(_nutrition_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        _nutrition_cache = rows
    return _nutrition_cache

@router.post("/food")
async def infer_food(file: UploadFile = File(...)):
    """음식 이미지 분류 예측"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "이미지 파일만 업로드 가능")
    
    try:
        img = await file.read()
        model = get_food_model()
        result = model.predict(img)
        
        if result["success"]:
            return {
                "model": "kfood30_mnv3_fp16",
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
    try:
        model = get_food_model()
        _ = getattr(model, 'input_details', None)
        return {
            "status": "healthy",
            "service": "tflite-ml",
            "model": _food_model_path,
            "message": "TFLite 모델이 정상적으로 로드되었습니다"
        }
    except HTTPException as e:
        return {
            "status": "degraded",
            "service": "tflite-ml",
            "model": _food_model_path,
            "message": e.detail
        }

@router.get("/nutrition")
async def get_food_nutrition(food_name: str = Query(..., alias="food")):
    """선택한 음식명에 대한 영양정보(탄/단/당/지방, 칼로리) 반환"""
    rows = get_nutrition_rows()
    # 완전 일치 우선, 없으면 포함 검색
    exact = [r for r in rows if r.get("식품명") == food_name]
    candidates = exact if exact else [r for r in rows if food_name in r.get("식품명", "")]
    if not candidates:
        raise HTTPException(404, f"CSV에서 음식을 찾지 못했습니다: {food_name}")
    r = candidates[0]
    def to_float(v):
        try:
            return float(v)
        except Exception:
            return None
    return {
        "food_name": r.get("식품명"),
        "energy_kcal": to_float(r.get("에너지(㎉)")),
        "carbohydrate_g": to_float(r.get("탄수화물(g)")),
        "protein_g": to_float(r.get("단백질(g)")),
        "sugars_g": to_float(r.get("총당류(g)")),
        "fat_g": to_float(r.get("지방(g)")),
        "source": os.path.basename(_nutrition_csv_path)
    }


def predict_with_nutrition(self, image_data: bytes):
    """예측 + 영양 정보 반환"""
    # 기존 예측 수행
    prediction_result = self.predict(image_data)
    
    if prediction_result["success"]:
        # 영양 정보 추가
        nutrition_info = self.get_nutrition_info(prediction_result["predicted_food"])
        
        return {
            **prediction_result,
            "nutrition": nutrition_info
        }
    
    return prediction_result

def get_nutrition_info(self, food_name: str):
    """음식명으로 영양 정보 조회"""
    try:
        df = pd.read_csv('nutrition_data.csv')
        food_data = df[df['음식명'] == food_name]
        
        if not food_data.empty:
            return {
                "탄수화물": float(food_data.iloc[0]['탄수화물(g)']),
                "단백질": float(food_data.iloc[0]['단백질(g)']),
                "지방": float(food_data.iloc[0]['지방(g)']),
                "칼로리": float(food_data.iloc[0]['칼로리(kcal)'])
            }
        else:
            return None
    except:
        return None