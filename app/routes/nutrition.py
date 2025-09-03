# app/routes/nutrition.py
from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

@router.get("/nutrition/foods")
async def get_all_foods():
    """모든 음식 영양 정보 조회"""
    try:
        df = pd.read_csv('nutrition_data.csv')
        return {"foods": df.to_dict('records')}
    except Exception as e:
        raise HTTPException(500, f"영양 정보 로드 실패: {str(e)}")

@router.get("/nutrition/food/{food_name}")
async def get_food_nutrition(food_name: str):
    """특정 음식 영양 정보 조회"""
    try:
        df = pd.read_csv('nutrition_data.csv')
        food_data = df[df['음식명'] == food_name]
        
        if food_data.empty:
            raise HTTPException(404, f"음식을 찾을 수 없음: {food_name}")
        
        return food_data.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(500, f"영양 정보 조회 실패: {str(e)}")