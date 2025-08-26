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
        ),
        FoodItem(
            id="quinoa",
            name="퀴노아",
            category="음식",
            gi_index=53,
            sugar_content=0.9,
            calories=120,
            description="퀴노아는 단백질과 식이섬유가 풍부한 가짜 곡물로 혈당 반응을 완만하게 합니다.",
            benefits="낮은 GI와 높은 단백질로 식후 혈당 급등을 줄여줍니다."
        ),
        FoodItem(
            id="sweet_potato",
            name="고구마",
            category="음식",
            gi_index=54,
            sugar_content=4.2,
            calories=86,
            description="고구마는 식이섬유와 베타카로틴이 풍부하여 포만감과 혈당 조절에 도움을 줍니다.",
            benefits="식이섬유가 소화를 늦춰 혈당 상승을 완화합니다."
        ),
        FoodItem(
            id="lentils",
            name="렌틸콩",
            category="음식",
            gi_index=32,
            sugar_content=1.8,
            calories=116,
            description="렌틸콩은 단백질과 식이섬유가 풍부해 혈당 반응이 낮습니다.",
            benefits="낮은 GI와 높은 단백질로 혈당 안정화에 도움."
        ),
        FoodItem(
            id="soba",
            name="메밀국수",
            category="음식",
            gi_index=46,
            sugar_content=0.6,
            calories=99,
            description="메밀은 루틴과 식이섬유가 풍부하여 혈당 반응이 낮습니다.",
            benefits="낮은 GI로 식후 혈당 상승을 완만하게 합니다."
        ),
        FoodItem(
            id="whole_wheat_pasta",
            name="통밀 파스타",
            category="음식",
            gi_index=48,
            sugar_content=1.5,
            calories=124,
            description="통밀 파스타는 정제 파스타보다 식이섬유가 많아 혈당 반응이 낮습니다.",
            benefits="식이섬유가 탄수화물 흡수를 늦춥니다."
        ),
        FoodItem(
            id="tofu_steak",
            name="두부 스테이크",
            category="음식",
            gi_index=15,
            sugar_content=0.7,
            calories=80,
            description="두부는 단백질이 풍부하고 탄수화물이 적어 혈당 영향이 낮습니다.",
            benefits="단백질 공급과 낮은 GI로 혈당 관리에 유리합니다."
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
        ),
        FoodItem(
            id="boiled_egg",
            name="삶은 달걀",
            category="간식",
            gi_index=0,
            sugar_content=0.6,
            calories=77,
            description="달걀은 단백질과 필수 아미노산이 풍부하며 탄수화물이 거의 없습니다.",
            benefits="탄수화물이 거의 없어 혈당에 미치는 영향이 매우 낮습니다."
        ),
        FoodItem(
            id="hummus_veggies",
            name="후무스와 생채소",
            category="간식",
            gi_index=10,
            sugar_content=1.5,
            calories=120,
            description="병아리콩 딥과 채소 조합으로 혈당 반응이 낮은 간식입니다.",
            benefits="단백질·식이섬유가 포만감과 혈당 안정에 도움."
        ),
        FoodItem(
            id="cheese_stick",
            name="치즈 스틱",
            category="간식",
            gi_index=0,
            sugar_content=0.3,
            calories=80,
            description="탄수화물이 거의 없고 단백질과 지방이 있어 혈당 영향이 낮습니다.",
            benefits="저탄수 간식으로 혈당 변동 최소화."
        ),
        FoodItem(
            id="avocado",
            name="아보카도",
            category="간식",
            gi_index=15,
            sugar_content=0.7,
            calories=160,
            description="불포화지방과 식이섬유가 풍부하여 혈당 반응이 낮습니다.",
            benefits="식이섬유가 포만감 유지와 혈당 안정에 도움."
        ),
        FoodItem(
            id="edamame",
            name="에다마메",
            category="간식",
            gi_index=15,
            sugar_content=1.2,
            calories=120,
            description="삶은 풋콩으로 단백질과 식이섬유가 풍부합니다.",
            benefits="낮은 GI와 단백질로 간식에 적합합니다."
        ),
        FoodItem(
            id="dark_chocolate_85",
            name="다크 초콜릿(85%)",
            category="간식",
            gi_index=23,
            sugar_content=6.0,
            calories=170,
            description="설탕이 적은 고카카오 초콜릿은 당 흡수가 느립니다.",
            benefits="적당량 섭취 시 혈당 영향이 낮습니다."
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
        ),
        FoodItem(
            id="unsweetened_soymilk",
            name="무가당 두유",
            category="음료",
            gi_index=34,
            sugar_content=2.7,
            calories=54,
            description="무가당 두유는 단백질과 식물성 지방이 포함되어 혈당 반응이 낮습니다.",
            benefits="낮은 GI로 식후 혈당 급증을 줄이는 데 도움을 줍니다."
        ),
        FoodItem(
            id="water",
            name="물",
            category="음료",
            gi_index=0,
            sugar_content=0.0,
            calories=0,
            description="혈당에 영향을 주지 않는 최적의 수분 공급원입니다.",
            benefits="혈당과 대사 균형 유지에 필수적입니다."
        ),
        FoodItem(
            id="black_coffee",
            name="블랙 커피",
            category="음료",
            gi_index=0,
            sugar_content=0.0,
            calories=2,
            description="무가당 블랙 커피는 열량과 당이 거의 없습니다.",
            benefits="무가당 섭취 시 혈당 영향이 사실상 없습니다."
        ),
        FoodItem(
            id="herbal_tea",
            name="허브티(무가당)",
            category="음료",
            gi_index=0,
            sugar_content=0.0,
            calories=0,
            description="카페인이 적고 무가당이면 혈당 영향이 없습니다.",
            benefits="무가당 수분 보충에 적합합니다."
        ),
        FoodItem(
            id="sparkling_water",
            name="탄산수(무가당)",
            category="음료",
            gi_index=0,
            sugar_content=0.0,
            calories=0,
            description="무가당 탄산수는 혈당에 영향을 주지 않습니다.",
            benefits="음료 대체로 혈당 안전합니다."
        ),
        FoodItem(
            id="kefir_unsweetened",
            name="케피어(무가당)",
            category="음료",
            gi_index=30,
            sugar_content=3.5,
            calories=55,
            description="발효 유제품으로 설탕을 첨가하지 않으면 혈당 반응이 낮습니다.",
            benefits="장 건강과 혈당 안정에 도움."
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
        ),
        FoodItem(
            id="cherry",
            name="체리",
            category="과일",
            gi_index=22,
            sugar_content=8.0,
            calories=50,
            description="체리는 낮은 GI를 가지며 항산화 성분이 풍부합니다.",
            benefits="낮은 GI로 혈당 변동을 줄이고 항산화 효과를 제공합니다."
        ),
        FoodItem(
            id="plum",
            name="자두",
            category="과일",
            gi_index=24,
            sugar_content=10.0,
            calories=46,
            description="자두는 수분과 식이섬유가 많아 포만감을 주며 혈당 반응이 낮습니다.",
            benefits="낮은 GI와 식이섬유로 식후 혈당 상승을 완만하게 합니다."
        ),
        FoodItem(
            id="strawberry",
            name="딸기",
            category="과일",
            gi_index=41,
            sugar_content=4.9,
            calories=33,
            description="딸기는 수분과 식이섬유가 많고 GI가 낮습니다.",
            benefits="낮은 GI 과일로 간식에 적합합니다."
        ),
        FoodItem(
            id="blueberry",
            name="블루베리",
            category="과일",
            gi_index=53,
            sugar_content=10.0,
            calories=57,
            description="블루베리는 항산화가 풍부하며 GI가 낮은 편입니다.",
            benefits="항산화와 비교적 낮은 GI로 혈당 관리에 도움."
        ),
        FoodItem(
            id="orange",
            name="오렌지",
            category="과일",
            gi_index=43,
            sugar_content=9.0,
            calories=47,
            description="비타민 C와 식이섬유가 풍부합니다.",
            benefits="식이섬유가 혈당 흡수를 늦춥니다."
        ),
        FoodItem(
            id="grapefruit",
            name="자몽",
            category="과일",
            gi_index=25,
            sugar_content=7.0,
            calories=42,
            description="자몽은 비교적 낮은 GI를 가집니다.",
            benefits="낮은 GI로 식후 혈당 변화를 완화합니다."
        ),
        FoodItem(
            id="kiwi",
            name="키위",
            category="과일",
            gi_index=50,
            sugar_content=8.9,
            calories=61,
            description="키위는 식이섬유가 풍부하고 GI가 낮은 편입니다.",
            benefits="섬유질로 혈당 상승을 억제합니다."
        )
    ]
}

# 당뇨에 나쁜 음식 데이터
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
        ),
        FoodItem(
            id="tteok",
            name="가래떡/떡",
            category="음식",
            gi_index=85,
            sugar_content=1.0,
            calories=140,
            description="찹쌀/멥쌀로 만든 떡은 정제 전분 비중이 높아 혈당을 급격히 올립니다.",
            warnings="높은 GI로 식후 혈당 급상승을 유발합니다."
        ),
        FoodItem(
            id="instant_noodles",
            name="인스턴트 면",
            category="음식",
            gi_index=85,
            sugar_content=1.5,
            calories=470,
            description="정제 밀가루와 유지가 많은 면류는 혈당 반응이 높습니다.",
            warnings="정제 전분과 지방으로 혈당·체중 관리에 불리합니다."
        ),
        FoodItem(
            id="french_fries",
            name="감자튀김",
            category="음식",
            gi_index=75,
            sugar_content=0.5,
            calories=312,
            description="튀긴 감자는 GI와 열량이 모두 높습니다.",
            warnings="고지방·고GI로 혈당 급등과 체중 증가 위험."
        ),
        FoodItem(
            id="ramen",
            name="라면",
            category="음식",
            gi_index=73,
            sugar_content=1.2,
            calories=480,
            description="정제 전분 면과 나트륨/지방이 많은 스프 구성입니다.",
            warnings="혈당·혈압·체중 관리에 모두 불리합니다."
        ),
        FoodItem(
            id="corn_flakes",
            name="콘플레이크",
            category="음식",
            gi_index=81,
            sugar_content=8.0,
            calories=370,
            description="정제 옥수수 가공 시리얼로 GI가 매우 높습니다.",
            warnings="아침 섭취 시 혈당 급상승 유발."
        ),
        FoodItem(
            id="glutinous_rice",
            name="찹쌀밥",
            category="음식",
            gi_index=87,
            sugar_content=0.4,
            calories=140,
            description="찹쌀은 아밀로펙틴 비중이 높아 혈당 상승이 빠릅니다.",
            warnings="높은 GI로 식후 혈당 급증."
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
        ),
        FoodItem(
            id="donut",
            name="도넛",
            category="간식",
            gi_index=76,
            sugar_content=20.0,
            calories=452,
            description="정제 밀가루와 설탕, 기름으로 만든 도넛은 혈당 반응과 칼로리가 매우 높습니다.",
            warnings="고당·고지방 조합으로 혈당과 체중 관리에 모두 불리합니다."
        ),
        FoodItem(
            id="cookies",
            name="쿠키",
            category="간식",
            gi_index=77,
            sugar_content=18.0,
            calories=480,
            description="설탕·밀가루·버터 비중이 높은 과자류입니다.",
            warnings="고당분·정제 전분으로 혈당 급상승."
        ),
        FoodItem(
            id="chocolate_bar",
            name="초콜릿바(가당)",
            category="간식",
            gi_index=70,
            sugar_content=25.0,
            calories=520,
            description="설탕이 많이 들어간 초콜릿 바.",
            warnings="당분 과다로 혈당에 매우 불리."
        ),
        FoodItem(
            id="churros",
            name="츄러스",
            category="간식",
            gi_index=75,
            sugar_content=16.0,
            calories=450,
            description="튀김과 설탕 코팅으로 고칼로리·고당분 간식입니다.",
            warnings="혈당 급등과 체중 증가 위험."
        ),
        FoodItem(
            id="sweet_bread",
            name="달콤한 빵(크림/단팥)",
            category="간식",
            gi_index=75,
            sugar_content=22.0,
            calories=330,
            description="정제 전분과 설탕 충전물이 많은 제과류.",
            warnings="혈당과 칼로리 모두 높습니다."
        ),
        FoodItem(
            id="caramel_popcorn",
            name="카라멜 팝콘",
            category="간식",
            gi_index=72,
            sugar_content=30.0,
            calories=400,
            description="설탕 코팅으로 당 함량이 높습니다.",
            warnings="과다 섭취 시 혈당 급상승."
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
        ),
        FoodItem(
            id="sweet_latte",
            name="가당 라떼/모카",
            category="음료",
            gi_index=60,
            sugar_content=25.0,
            calories=290,
            description="시럽이 들어간 커피 음료는 당 함량이 높아 혈당에 불리합니다.",
            warnings="추가 당분으로 혈당 급상승을 유발할 수 있습니다."
        ),
        FoodItem(
            id="milk_tea_sweet",
            name="가당 밀크티",
            category="음료",
            gi_index=62,
            sugar_content=28.0,
            calories=240,
            description="설탕과 시럽이 들어간 밀크티.",
            warnings="고당분으로 혈당 급상승."
        ),
        FoodItem(
            id="energy_drink",
            name="에너지 드링크",
            category="음료",
            gi_index=70,
            sugar_content=27.0,
            calories=200,
            description="당과 카페인이 높은 음료.",
            warnings="당분 과다로 혈당에 불리."
        ),
        FoodItem(
            id="sports_drink",
            name="스포츠 드링크",
            category="음료",
            gi_index=78,
            sugar_content=21.0,
            calories=130,
            description="운동용 당 보충 음료지만 당뇨에는 부적합.",
            warnings="당분 과다로 혈당 급상승."
        ),
        FoodItem(
            id="flavored_yogurt_drink",
            name="가당 요거트 음료",
            category="음료",
            gi_index=58,
            sugar_content=24.0,
            calories=150,
            description="설탕이 첨가된 발효유 음료.",
            warnings="추가 당분으로 혈당에 불리."
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
        ),
        FoodItem(
            id="pineapple",
            name="파인애플",
            category="과일",
            gi_index=59,
            sugar_content=10.0,
            calories=50,
            description="파인애플은 당 함량과 GI가 상대적으로 높아 주의가 필요합니다.",
            warnings="과다 섭취 시 식후 혈당 상승을 유발할 수 있습니다."
        ),
        FoodItem(
            id="mango",
            name="망고",
            category="과일",
            gi_index=56,
            sugar_content=14.0,
            calories=60,
            description="망고는 당도가 높아 혈당 관리에 주의가 필요합니다.",
            warnings="당 함량이 높아 소량 섭취가 권장됩니다."
        ),
        FoodItem(
            id="banana_ripe",
            name="잘 익은 바나나",
            category="과일",
            gi_index=62,
            sugar_content=12.0,
            calories=89,
            description="숙성도가 높은 바나나는 당 흡수가 빠릅니다.",
            warnings="식후 혈당 급상승 유발 가능."
        ),
        FoodItem(
            id="dates",
            name="대추야자",
            category="과일",
            gi_index=62,
            sugar_content=66.0,
            calories=282,
            description="건조 과일로 당 함량이 매우 높습니다.",
            warnings="소량만 허용 권장."
        ),
        FoodItem(
            id="raisins",
            name="건포도",
            category="과일",
            gi_index=64,
            sugar_content=59.0,
            calories=299,
            description="건조 포도로 당밀도가 매우 높습니다.",
            warnings="적은 양에도 당 섭취가 큽니다."
        ),
        FoodItem(
            id="lychee",
            name="리치",
            category="과일",
            gi_index=79,
            sugar_content=15.0,
            calories=66,
            description="당도가 높은 열대 과일입니다.",
            warnings="혈당 관리에 불리하여 제한 필요."
        ),
        FoodItem(
            id="jackfruit",
            name="잭프루트",
            category="과일",
            gi_index=75,
            sugar_content=19.0,
            calories=95,
            description="당이 풍부한 열대 과일로 혈당 반응이 높습니다.",
            warnings="소량 섭취 권장."
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
