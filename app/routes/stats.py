from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.firebase_config import get_firestore_db
from app.config import settings
from firebase_admin import firestore
import calendar

router = APIRouter()

class NutritionStats(BaseModel):
    period: str  # "weekly" or "monthly"
    start_date: str
    end_date: str
    total_meals: int
    average_calories: float
    average_carbs: float
    average_protein: float
    average_fat: float
    carb_ratio: float
    protein_ratio: float
    fat_ratio: float
    daily_averages: List[Dict[str, Any]]

class BloodSugarStats(BaseModel):
    period: str
    start_date: str
    end_date: str
    total_records: int
    average_fasting: float  # 공복 혈당
    average_before_meal: float  # 식전 혈당
    time_period_averages: Dict[str, float]  # 시간대별 평균
    meal_type_averages: Dict[str, float]  # 식사 타입별 평균
    daily_trends: List[Dict[str, Any]]

class OverviewStats(BaseModel):
    period: str
    start_date: str
    end_date: str
    nutrition_summary: NutritionStats
    blood_sugar_summary: BloodSugarStats
    combined_insights: List[str]

async def get_current_user_id(authorization: str = Header(None)) -> str:
    if settings.DEV_MODE:
        return "dev_user_123"
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 필요합니다")
    try:
        from app.services.firebase_auth_service import verify_user_token
        token = authorization.split(" ")[1]
        decoded_token = await verify_user_token(token)
        return decoded_token.get("uid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {str(e)}")

def get_date_range(period: str, start_date: Optional[str] = None) -> tuple:
    """기간에 따른 시작/종료 날짜 계산"""
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.now()
    
    if period == "weekly":
        # 해당 주의 월요일부터 일요일까지
        days_since_monday = start.weekday()
        start = start - timedelta(days=days_since_monday)
        end = start + timedelta(days=6)
    elif period == "monthly":
        # 해당 월의 1일부터 마지막 날까지
        start = start.replace(day=1)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = start.replace(day=last_day)
    else:  # daily
        end = start
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

@router.get("/nutrition", response_model=NutritionStats)
async def get_nutrition_stats(
    period: str = Query(..., description="기간: weekly, monthly, daily"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user_id)
):
    """주간/월간 탄단지 비율, 평균 칼로리"""
    if period not in ["weekly", "monthly", "daily"]:
        raise HTTPException(status_code=400, detail="기간은 weekly, monthly, daily 중 하나여야 합니다")
    
    start_date_str, end_date_str = get_date_range(period, start_date)
    
    if settings.DEV_MODE:
        # 더미 데이터 반환
        daily_averages = []
        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        while current_date <= end_date:
            daily_averages.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "calories": 1800.0,
                "carbs": 225.0,
                "protein": 90.0,
                "fat": 60.0
            })
            current_date += timedelta(days=1)
        
        return NutritionStats(
            period=period,
            start_date=start_date_str,
            end_date=end_date_str,
            total_meals=21 if period == "weekly" else 90 if period == "monthly" else 3,
            average_calories=1800.0,
            average_carbs=225.0,
            average_protein=90.0,
            average_fat=60.0,
            carb_ratio=60.0,
            protein_ratio=20.0,
            fat_ratio=20.0,
            daily_averages=daily_averages
        )
    
    # Firebase에서 실제 데이터 조회
    db = get_firestore_db()
    meals_docs = db.collection("meals").where("user_id", "==", user_id).stream()
    
    meals_data = []
    for doc in meals_docs:
        data = doc.to_dict()
        meal_date = data.get("date")
        if start_date_str <= meal_date <= end_date_str:
            meals_data.append(data)
    
    if not meals_data:
        return NutritionStats(
            period=period,
            start_date=start_date_str,
            end_date=end_date_str,
            total_meals=0,
            average_calories=0.0,
            average_carbs=0.0,
            average_protein=0.0,
            average_fat=0.0,
            carb_ratio=0.0,
            protein_ratio=0.0,
            fat_ratio=0.0,
            daily_averages=[]
        )
    
    # 통계 계산
    total_calories = sum(m.get("analysis", {}).get("calories", 0) for m in meals_data)
    total_carbs = sum(m.get("analysis", {}).get("carbs", 0) for m in meals_data)
    total_protein = sum(m.get("analysis", {}).get("protein", 0) for m in meals_data)
    total_fat = sum(m.get("analysis", {}).get("fat", 0) for m in meals_data)
    
    total_meals = len(meals_data)
    average_calories = total_calories / total_meals
    average_carbs = total_carbs / total_meals
    average_protein = total_protein / total_meals
    average_fat = total_fat / total_meals
    
    # 비율 계산
    total_macros = total_carbs + total_protein + total_fat
    if total_macros > 0:
        carb_ratio = (total_carbs / total_macros) * 100
        protein_ratio = (total_protein / total_macros) * 100
        fat_ratio = (total_fat / total_macros) * 100
    else:
        carb_ratio = protein_ratio = fat_ratio = 0.0
    
    # 일별 평균 계산
    daily_totals = {}
    for meal in meals_data:
        date = meal.get("date")
        if date not in daily_totals:
            daily_totals[date] = {"calories": 0, "carbs": 0, "protein": 0, "fat": 0, "count": 0}
        
        analysis = meal.get("analysis", {})
        daily_totals[date]["calories"] += analysis.get("calories", 0)
        daily_totals[date]["carbs"] += analysis.get("carbs", 0)
        daily_totals[date]["protein"] += analysis.get("protein", 0)
        daily_totals[date]["fat"] += analysis.get("fat", 0)
        daily_totals[date]["count"] += 1
    
    daily_averages = []
    for date, totals in daily_totals.items():
        count = totals["count"]
        daily_averages.append({
            "date": date,
            "calories": totals["calories"] / count,
            "carbs": totals["carbs"] / count,
            "protein": totals["protein"] / count,
            "fat": totals["fat"] / count
        })
    
    daily_averages.sort(key=lambda x: x["date"])
    
    return NutritionStats(
        period=period,
        start_date=start_date_str,
        end_date=end_date_str,
        total_meals=total_meals,
        average_calories=round(average_calories, 1),
        average_carbs=round(average_carbs, 1),
        average_protein=round(average_protein, 1),
        average_fat=round(average_fat, 1),
        carb_ratio=round(carb_ratio, 1),
        protein_ratio=round(protein_ratio, 1),
        fat_ratio=round(fat_ratio, 1),
        daily_averages=daily_averages
    )

@router.get("/blood-sugar", response_model=BloodSugarStats)
async def get_blood_sugar_stats(
    period: str = Query(..., description="기간: weekly, monthly, daily"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user_id)
):
    """공복/식전 혈당 통계, 시간대별 평균"""
    if period not in ["weekly", "monthly", "daily"]:
        raise HTTPException(status_code=400, detail="기간은 weekly, monthly, daily 중 하나여야 합니다")
    
    start_date_str, end_date_str = get_date_range(period, start_date)
    
    if settings.DEV_MODE:
        # 더미 데이터 반환
        daily_trends = []
        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        while current_date <= end_date:
            daily_trends.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "average": 120.0,
                "count": 3
            })
            current_date += timedelta(days=1)
        
        return BloodSugarStats(
            period=period,
            start_date=start_date_str,
            end_date=end_date_str,
            total_records=21 if period == "weekly" else 90 if period == "monthly" else 3,
            average_fasting=110.0,
            average_before_meal=125.0,
            time_period_averages={
                "06:00-09:00": 105.0,
                "09:00-12:00": 120.0,
                "12:00-15:00": 130.0,
                "15:00-18:00": 125.0,
                "18:00-21:00": 135.0,
                "21:00-24:00": 115.0
            },
            meal_type_averages={
                "기상직후": 105.0,
                "아침": 125.0,
                "점심": 130.0,
                "저녁": 135.0
            },
            daily_trends=daily_trends
        )
    
    # Firebase에서 실제 데이터 조회
    db = get_firestore_db()
    blood_sugar_docs = db.collection("blood_sugar").where("user_id", "==", user_id).stream()
    
    blood_sugar_data = []
    for doc in blood_sugar_docs:
        data = doc.to_dict()
        if start_date_str <= data.get("date") <= end_date_str:
            blood_sugar_data.append(data)
    
    if not blood_sugar_data:
        return BloodSugarStats(
            period=period,
            start_date=start_date_str,
            end_date=end_date_str,
            total_records=0,
            average_fasting=0.0,
            average_before_meal=0.0,
            time_period_averages={},
            meal_type_averages={},
            daily_trends=[]
        )
    
    # 통계 계산
    total_records = len(blood_sugar_data)
    
    # 공복/식전 혈당 구분 (간단한 로직)
    fasting_data = [d for d in blood_sugar_data if d.get("meal_type") == "기상직후"]
    before_meal_data = [d for d in blood_sugar_data if d.get("meal_type") in ["아침", "점심", "저녁"]]
    
    average_fasting = sum(d.get("blood_sugar", 0) for d in fasting_data) / len(fasting_data) if fasting_data else 0
    average_before_meal = sum(d.get("blood_sugar", 0) for d in before_meal_data) / len(before_meal_data) if before_meal_data else 0
    
    # 시간대별 평균
    time_periods = {
        "06:00-09:00": [],
        "09:00-12:00": [],
        "12:00-15:00": [],
        "15:00-18:00": [],
        "18:00-21:00": [],
        "21:00-24:00": []
    }
    
    for data in blood_sugar_data:
        time_str = data.get("time", "00:00")
        hour = int(time_str.split(":")[0])
        
        if 6 <= hour < 9:
            time_periods["06:00-09:00"].append(data.get("blood_sugar", 0))
        elif 9 <= hour < 12:
            time_periods["09:00-12:00"].append(data.get("blood_sugar", 0))
        elif 12 <= hour < 15:
            time_periods["12:00-15:00"].append(data.get("blood_sugar", 0))
        elif 15 <= hour < 18:
            time_periods["15:00-18:00"].append(data.get("blood_sugar", 0))
        elif 18 <= hour < 21:
            time_periods["18:00-21:00"].append(data.get("blood_sugar", 0))
        else:
            time_periods["21:00-24:00"].append(data.get("blood_sugar", 0))
    
    time_period_averages = {}
    for period, values in time_periods.items():
        if values:
            time_period_averages[period] = round(sum(values) / len(values), 1)
    
    # 식사 타입별 평균
    meal_type_totals = {"기상직후": [], "아침": [], "점심": [], "저녁": []}
    for data in blood_sugar_data:
        meal_type = data.get("meal_type")
        if meal_type in meal_type_totals:
            meal_type_totals[meal_type].append(data.get("blood_sugar", 0))
    
    meal_type_averages = {}
    for meal_type, values in meal_type_totals.items():
        if values:
            meal_type_averages[meal_type] = round(sum(values) / len(values), 1)
    
    # 일별 트렌드
    daily_totals = {}
    for data in blood_sugar_data:
        date = data.get("date")
        if date not in daily_totals:
            daily_totals[date] = {"total": 0, "count": 0}
        daily_totals[date]["total"] += data.get("blood_sugar", 0)
        daily_totals[date]["count"] += 1
    
    daily_trends = []
    for date, totals in daily_totals.items():
        daily_trends.append({
            "date": date,
            "average": round(totals["total"] / totals["count"], 1),
            "count": totals["count"]
        })
    
    daily_trends.sort(key=lambda x: x["date"])
    
    return BloodSugarStats(
        period=period,
        start_date=start_date_str,
        end_date=end_date_str,
        total_records=total_records,
        average_fasting=round(average_fasting, 1),
        average_before_meal=round(average_before_meal, 1),
        time_period_averages=time_period_averages,
        meal_type_averages=meal_type_averages,
        daily_trends=daily_trends
    )

@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    period: str = Query(..., description="기간: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user_id)
):
    """식단 + 혈당 종합 통계 요약"""
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="기간은 daily, weekly, monthly 중 하나여야 합니다")
    
    # 영양 통계와 혈당 통계 조회
    nutrition_stats = await get_nutrition_stats(period, start_date, user_id)
    blood_sugar_stats = await get_blood_sugar_stats(period, start_date, user_id)
    
    # 종합 인사이트 생성
    combined_insights = []
    
    # 영양 관련 인사이트
    if nutrition_stats.average_calories > 0:
        if nutrition_stats.average_calories > 2000:
            combined_insights.append("평균 칼로리 섭취가 높습니다. 식사량 조절을 고려해보세요.")
        elif nutrition_stats.average_calories < 1200:
            combined_insights.append("평균 칼로리 섭취가 낮습니다. 균형잡힌 식사를 권장합니다.")
        
        if nutrition_stats.carb_ratio > 70:
            combined_insights.append("탄수화물 비율이 높습니다. 단백질과 지방 섭취를 늘려보세요.")
        elif nutrition_stats.protein_ratio < 15:
            combined_insights.append("단백질 섭취가 부족합니다. 단백질이 풍부한 식품을 추가해보세요.")
    
    # 혈당 관련 인사이트
    if blood_sugar_stats.average_fasting > 0:
        if blood_sugar_stats.average_fasting > 126:
            combined_insights.append("공복 혈당이 높습니다. 의료진과 상담을 권장합니다.")
        elif blood_sugar_stats.average_fasting < 70:
            combined_insights.append("공복 혈당이 낮습니다. 식사 간격을 조절해보세요.")
        
        if blood_sugar_stats.average_before_meal > 140:
            combined_insights.append("식전 혈당이 높습니다. 식사량과 탄수화물 섭취를 조절해보세요.")
    
    # 종합 권장사항
    if not combined_insights:
        combined_insights.append("현재 식단과 혈당 관리가 양호합니다. 꾸준히 유지해보세요.")
    
    return OverviewStats(
        period=period,
        start_date=nutrition_stats.start_date,
        end_date=nutrition_stats.end_date,
        nutrition_summary=nutrition_stats,
        blood_sugar_summary=blood_sugar_stats,
        combined_insights=combined_insights
    )
