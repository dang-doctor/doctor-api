from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class FoodItem(BaseModel):
    id: str
    name: str
    category: str  # "음식", "간식", "음료", "과일"
    gi_index: int  # 혈당지수
    sugar_content: float  # 당 함량 (g)
    calories: float  # 칼로리 (kcal)
    description: str  # 음식 설명
    benefits: Optional[str] = None  # 당뇨에 좋은 점
    warnings: Optional[str] = None  # 당뇨에 나쁜 점

class FoodCategory(BaseModel):
    category: str
    foods: List[FoodItem]

class FoodResponse(BaseModel):
    good_foods: List[FoodCategory]
    bad_foods: List[FoodCategory]

# 당뇨에 좋은 음식 데이터 (GI < 55)
GOOD_FOODS = {
    "음식": [
        FoodItem(
            id="brown_rice",
            name="현미밥",
            category="음식",
            gi_index=55,
            sugar_content=2.5,
            calories=110,
            description="현미는 도정이 덜 된 곡물로, 겉껍질과 배아가 남아 있어 흰쌀에 비해 식이섬유, 비타민 B군, 마그네슘, 셀레늄 등의 영양소가 풍부합니다. 이러한 성분들은 대사 건강과 인슐린 기능 개선에 긍정적인 영향을 미칩니다.",
            benefits="식이섬유가 풍부하여 혈당 상승을 완만하게 하고, 인슐린 감수성을 개선합니다."
        ),
        FoodItem(
            id="barley_rice",
            name="보리밥",
            category="음식",
            gi_index=25,
            sugar_content=1.8,
            calories=95,
            description="보리는 베타글루칸이 풍부한 곡물로, 혈당 조절과 콜레스테롤 감소에 효과적입니다. 식이섬유가 많아 포만감을 주고 소화를 돕습니다.",
            benefits="베타글루칸이 혈당 상승을 억제하고 인슐린 저항성을 개선합니다."
        ),
        FoodItem(
            id="oats",
            name="귀리",
            category="음식",
            gi_index=55,
            sugar_content=1.0,
            calories=68,
            description="귀리는 베타글루칸이 풍부한 곡물로, 혈당 조절과 심장 건강에 좋습니다. 아침 식사로 섭취하면 포만감을 오래 유지할 수 있습니다.",
            benefits="베타글루칸이 혈당 흡수를 늦추고 인슐린 감수성을 향상시킵니다."
        )
    ],
    "간식": [
        FoodItem(
            id="nuts",
            name="견과류",
            category="간식",
            gi_index=15,
            sugar_content=2.0,
            calories=160,
            description="아몬드, 호두, 캐슈넛 등은 건강한 지방과 단백질이 풍부합니다. 혈당 조절에 도움이 되며 심장 건강에도 좋습니다.",
            benefits="건강한 지방과 단백질이 혈당 상승을 억제하고 포만감을 줍니다."
        ),
        FoodItem(
            id="yogurt",
            name="요거트",
            category="간식",
            gi_index=35,
            sugar_content=4.0,
            calories=59,
            description="프로바이오틱스가 풍부한 요거트는 장 건강과 면역력 증진에 도움이 됩니다. 단백질이 풍부하여 포만감을 줍니다.",
            benefits="프로바이오틱스가 장 건강을 개선하고 혈당 조절에 도움을 줍니다."
        )
    ],
    "음료": [
        FoodItem(
            id="green_tea",
            name="녹차",
            category="음료",
            gi_index=0,
            sugar_content=0.0,
            calories=0,
            description="카테킨이 풍부한 녹차는 항산화 효과가 뛰어나며, 혈당 조절과 체중 관리에 도움이 됩니다.",
            benefits="카테킨이 혈당 상승을 억제하고 인슐린 감수성을 개선합니다."
        ),
        FoodItem(
            id="milk",
            name="우유",
            category="음료",
            gi_index=41,
            sugar_content=4.8,
            calories=42,
            description="칼슘과 단백질이 풍부한 우유는 뼈 건강과 근육 발달에 도움이 됩니다. 혈당 조절에도 효과적입니다.",
            benefits="단백질과 지방이 탄수화물의 흡수를 늦춰 혈당 상승을 완만하게 합니다."
        )
    ],
    "과일": [
        FoodItem(
            id="apple",
            name="사과",
            category="과일",
            gi_index=36,
            sugar_content=10.4,
            calories=52,
            description="펙틴이 풍부한 사과는 혈당 조절과 콜레스테롤 감소에 효과적입니다. 식이섬유가 많아 포만감을 줍니다.",
            benefits="펙틴이 혈당 흡수를 늦추고 포만감을 증가시킵니다."
        ),
        FoodItem(
            id="pear",
            name="배",
            category="과일",
            gi_index=38,
            sugar_content=9.8,
            calories=57,
            description="식이섬유가 풍부한 배는 소화를 돕고 혈당 조절에 효과적입니다. 수분 함량이 높아 수분 보충에도 좋습니다.",
            benefits="식이섬유가 혈당 상승을 완만하게 하고 포만감을 줍니다."
        )
    ]
}

# 당뇨에 나쁜 음식 데이터 (GI > 70)
BAD_FOODS = {
    "음식": [
        FoodItem(
            id="white_rice",
            name="흰쌀밥",
            category="음식",
            gi_index=73,
            sugar_content=0.3,
            calories=130,
            description="정제된 흰쌀은 영양소가 제거되어 혈당을 빠르게 올립니다. 식이섬유가 적어 포만감이 적고 소화가 빠릅니다.",
            warnings="정제된 탄수화물로 혈당을 빠르게 올리고 인슐린 저항성을 악화시킬 수 있습니다."
        ),
        FoodItem(
            id="bread",
            name="빵",
            category="음식",
            gi_index=75,
            sugar_content=1.0,
            calories=265,
            description="정제된 밀가루로 만든 빵은 혈당을 빠르게 올립니다. 식이섬유가 적어 포만감이 적습니다.",
            warnings="정제된 밀가루는 혈당을 급격히 올리고 당뇨 합병증을 악화시킬 수 있습니다."
        )
    ],
    "간식": [
        FoodItem(
            id="candy",
            name="사탕",
            category="간식",
            gi_index=100,
            sugar_content=25.0,
            calories=100,
            description="순수한 설탕으로 만든 사탕은 혈당을 매우 빠르게 올립니다. 영양가가 전혀 없고 당뇨에 매우 해롭습니다.",
            warnings="순수 설탕으로 혈당을 급격히 올리고 당뇨 합병증을 악화시킵니다."
        ),
        FoodItem(
            id="ice_cream",
            name="아이스크림",
            category="간식",
            gi_index=87,
            sugar_content=21.0,
            calories=207,
            description="설탕과 지방이 많이 함유된 아이스크림은 혈당을 빠르게 올리고 체중 증가를 유발합니다.",
            warnings="높은 설탕 함량으로 혈당을 급격히 올리고 당뇨 관리에 악영향을 줍니다."
        )
    ],
    "음료": [
        FoodItem(
            id="soda",
            name="탄산음료",
            category="음료",
            gi_index=63,
            sugar_content=39.0,
            calories=150,
            description="대량의 설탕이 함유된 탄산음료는 혈당을 빠르게 올리고 체중 증가를 유발합니다.",
            warnings="높은 설탕 함량으로 혈당을 급격히 올리고 당뇨 합병증을 악화시킵니다."
        ),
        FoodItem(
            id="juice",
            name="주스",
            category="음료",
            gi_index=66,
            sugar_content=24.0,
            calories=96,
            description="과일을 압착한 주스는 식이섬유가 제거되어 혈당을 빠르게 올립니다.",
            warnings="식이섬유가 제거되어 혈당을 급격히 올리고 당뇨 관리에 악영향을 줍니다."
        )
    ],
    "과일": [
        FoodItem(
            id="watermelon",
            name="수박",
            category="과일",
            gi_index=72,
            sugar_content=6.2,
            calories=30,
            description="수분이 많고 당도가 높은 수박은 혈당을 빠르게 올립니다. 과다 섭취 시 혈당 관리에 어려움을 줄 수 있습니다.",
            warnings="높은 당도로 혈당을 빠르게 올리고 당뇨 관리에 어려움을 줄 수 있습니다."
        ),
        FoodItem(
            id="grapes",
            name="포도",
            category="과일",
            gi_index=59,
            sugar_content=16.0,
            calories=62,
            description="당도가 높은 포도는 혈당을 빠르게 올립니다. 과다 섭취 시 혈당 관리에 어려움을 줄 수 있습니다.",
            warnings="높은 당도로 혈당을 빠르게 올리고 당뇨 관리에 어려움을 줄 수 있습니다."
        )
    ]
}

@router.get("/", response_model=FoodResponse)
async def get_all_foods():
    """모든 음식 데이터 조회 (좋은 음식과 나쁜 음식 분류)"""
    good_foods_categories = [
        FoodCategory(category=cat, foods=foods) 
        for cat, foods in GOOD_FOODS.items()
    ]
    
    bad_foods_categories = [
        FoodCategory(category=cat, foods=foods) 
        for cat, foods in BAD_FOODS.items()
    ]
    
    return FoodResponse(
        good_foods=good_foods_categories,
        bad_foods=bad_foods_categories
    )

@router.get("/good", response_model=List[FoodCategory])
async def get_good_foods():
    """당뇨에 좋은 음식만 조회"""
    return [
        FoodCategory(category=cat, foods=foods) 
        for cat, foods in GOOD_FOODS.items()
    ]

@router.get("/bad", response_model=List[FoodCategory])
async def get_bad_foods():
    """당뇨에 나쁜 음식만 조회"""
    return [
        FoodCategory(category=cat, foods=foods) 
        for cat, foods in BAD_FOODS.items()
    ]

@router.get("/category/{category_name}")
async def get_foods_by_category(category_name: str):
    """특정 카테고리의 음식 조회"""
    if category_name not in ["음식", "간식", "음료", "과일"]:
        raise HTTPException(status_code=400, detail="잘못된 카테고리입니다. '음식', '간식', '음료', '과일' 중 선택하세요.")
    
    good_foods = GOOD_FOODS.get(category_name, [])
    bad_foods = BAD_FOODS.get(category_name, [])
    
    return {
        "category": category_name,
        "good_foods": good_foods,
        "bad_foods": bad_foods
    }

@router.get("/search/{food_name}")
async def search_food(food_name: str):
    """음식 이름으로 검색"""
    all_foods = []
    
    # 좋은 음식에서 검색
    for category, foods in GOOD_FOODS.items():
        for food in foods:
            if food_name.lower() in food.name.lower():
                all_foods.append({"food": food, "type": "good", "category": category})
    
    # 나쁜 음식에서 검색
    for category, foods in BAD_FOODS.items():
        for food in foods:
            if food_name.lower() in food.name.lower():
                all_foods.append({"food": food, "type": "bad", "category": category})
    
    if not all_foods:
        raise HTTPException(status_code=404, detail=f"'{food_name}'을(를) 찾을 수 없습니다.")
    
    return {
        "search_term": food_name,
        "results": all_foods
    }
