import streamlit as st
import json
import os
from openai import OpenAI

# 1. API 설정 (자신의 API 키로 변경하세요)
os.environ["OPENAI_API_KEY"] = "AQ.Ab8RN6K_smKIf0kvYEJfY_ogiW6QJDXD4Cl74zE_43NiJfyK7g"
client = OpenAI()
DATA_FILE = "recipe_data.json"

# 2. 데이터 로드/저장 함수
def load_recipes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_recipe(new_recipe):
    recipes = load_recipes()
    new_id = max([r.get("id", 0) for r in recipes]) + 1 if recipes else 1
    new_recipe["id"] = new_id
    recipes.append(new_recipe)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

# 3. AI 맞춤 추천 함수 (고도화된 프롬프트)
def recommend_baby_food(folder, ingredients, parent_condition, baby_condition, recipes):
    system_prompt = """
    당신은 20개월 아기를 키우는 부모의 마음을 누구보다 잘 아는 수석 AI 영유아 셰프입니다.
    사용자는 자신의 스마트폰에 3가지 폴더(1번: 잘 먹는 레시피, 2번: 해주고 싶은 레시피, 3번: 아침/간식)로 레시피를 분류해 두었습니다.
    
    [분석 및 추천 규칙]
    1. 사용자가 지정한 폴더의 레시피만 엄격하게 필터링해서 분석하세요.
    2. 사용자의 '현재 재료', '부모의 상태(조리시간/피로도)', '아기의 컨디션'을 종합하여 가장 완벽한 딱 2가지 메뉴만 추천하세요.
    3. 왜 이 2가지를 골랐는지 부모의 상황에 공감하며 명확한 추천 이유를 먼저 설명하세요.
    4. 각 메뉴의 조리 순서를 3~4단계로 간결하게 보여주세요.
    5. 마지막에 부모가 두 메뉴 중 하나를 쉽게 고를 수 있도록 '선택 가이드'를 한 줄로 제공하세요.
    """
    
    user_prompt = f"""
    - 선택한 폴더: {folder}
    - 오늘 냉장고 재료: {ingredients}
    - 나의 현재 상태(피로도/희망시간): {parent_condition}
    - 오늘 아기 컨디션: {baby_condition}
    
    [보유 레시피 DB]: {json.dumps(recipes, ensure_ascii=False)}
    
    위 조건에 맞춰 DB 안에서 2가지 레시피를 신중하게 골라 추천해 줘.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- 4. 웹 화면 구성 (UI) ---
st.set_page_config(page_title="20개월 아기 AI 요리비서", page_icon="👶", layout="centered")
st.title("👶 20개월 아기 AI 요리비서")

tab1, tab2 = st.tabs(["🍳 오늘의 맞춤 추천", "📝 새 레시피 저장"])

# [탭 1] AI 추천 받기 화면
with tab1:
    st.subheader("오늘의 상황을 알려주세요!")
    
    col1, col2 = st.columns(2)
    with col1:
        folder_choice = st.selectbox("어떤 폴더에서 찾을까요?", 
                                     ["1번 (잘 먹는 레시피)", "2번 (해주고 싶은 레시피)", "3번 (아침/간식)"])
    with col2:
        ingredients_input = st.text_input("오늘 냉장고 재료", placeholder="예: 양파, 소고기, 두부")
        
    parent_input = st.text_input("나의 현재 상태 (피로도/조리시간 등)", placeholder="예: 오늘 피곤하니까 10분 이내로 쉬운 것")
    baby_input = st.text_input("아기의 컨디션", placeholder="예: 컨디션 좋음, 밥맛 있음")
    
    if st.button("AI 셰프에게 2가지 추천받기", type="primary", use_container_width=True):
        if ingredients_input:
            recipes_db = load_recipes()
            with st.spinner("부모님과 아기의 상황을 분석하여 2가지 레시피를 엄선 중입니다..."):
                result = recommend_baby_food(folder_choice, ingredients_input, parent_input, baby_input, recipes_db)
                st.success("분석 완료! 오늘의 추천 메뉴입니다.")
                st.markdown(f"---")
                st.markdown(result)
        else:
            st.warning("재료를 하나 이상 입력해 주세요!")

# [탭 2] 새로운 레시피 저장 화면
with tab2:
    st.subheader("새로운 레시피를 폴더에 저장하세요")
    with st.form("new_recipe_form"):
        save_folder = st.radio("저장할 폴더 선택", ["1번 (잘 먹는 레시피)", "2번 (해주고 싶은 레시피)", "3번 (아침/간식)"], horizontal=True)
        title = st.text_input("요리 이름", placeholder="예: 양파 참치 주먹밥")
        ingredients = st.text_input("필요한 재료 (쉼표로 구분)", placeholder="양파, 참치, 밥")
        cooking_time = st.text_input("조리 시간", placeholder="예: 10분")
        difficulty = st.selectbox("난이도", ["매우 쉬움", "쉬움", "보통"])
        recipe_steps = st.text_area("조리 순서 (엔터로 구분)", placeholder="1. 양파를 다진다.\n2. 참치와 볶는다.")
        
        submitted = st.form_submit_button("이 레시피 기억하기")
        
        if submitted:
            if title and ingredients and recipe_steps:
                new_recipe_data = {
                    "folder": save_folder,
                    "title": title,
                    "ingredients": [i.strip() for i in ingredients.split(",")],
                    "cooking_time": cooking_time,
                    "difficulty": difficulty,
                    "recipe_steps": [step.strip() for step in recipe_steps.split("\n") if step.strip()]
                }
                save_recipe(new_recipe_data)
                st.success(f"[{save_folder}]에 '{title}' 레시피가 쏙 들어갔습니다!")
            else:
                st.error("요리 이름, 재료, 조리 순서는 꼭 적어주세요!")