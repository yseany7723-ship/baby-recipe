import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 페이지 기본 설정
st.set_page_config(page_title="20개월 아기 AI 레시피 분석기", page_icon="👶")

st.title("👶 20개월 아기 AI 레시피 분석기")
st.write("오늘 냉장고에 있는 재료를 적고 보유하신 레시피 사진들을 올리시면, 사진 속 메뉴 중 **지금 바로 만들 수 있는 맞춤 요리**를 AI가 찾아드립니다!")

# Secrets에서 Gemini API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", None)

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("⚠️ API 키가 설정되지 않았습니다. Streamlit Secrets에서 GEMINI_API_KEY를 등록해주세요.")

# 1. 사진 업로더
st.subheader("1. 📷 보유하신 레시피 캡처 사진 업로드")
st.caption("💡 팁: 20~30장 이상 다량 올리실 때는 10장씩 나누어 올려주시면 훨씬 안정적입니다.")

uploaded_files = st.file_uploader(
    "레시피 사진들을 선택해 주세요 (여러 장 가능)", 
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    key="recipe_images"
)

# 사진 전송 완료 시 실시간 상태 표시
if uploaded_files:
    st.success(f"📸 총 {len(uploaded_files)}장의 사진이 안전하게 올려졌습니다!")

# 2. 입력란과 제출 버튼
with st.form(key="recipe_matching_form"):
    st.subheader("2. 🥦 오늘 냉장고에 있는 재료 (야채, 고기 등)")
    fridge_ingredients = st.text_area(
        "활용하고 싶은 재료를 적어주세요 (필수)",
        placeholder="예: 소고기 다짐육, 당근, 양파, 애호박, 두부, 계란",
        height=80
    )

    st.subheader("3. ⚙️ 요리 조건 선택")
    col1, col2, col3 = st.columns(3)
    with col1:
        folder_choice = st.selectbox(
            "어떤 레시피 폴더인가요?", 
            ["1번 (잘 먹는 레시피 모음)", "2번 (해주고 싶은 레시피 모음)", "3번 (아침/간식 모음)"]
        )
    with col2:
        cooking_time = st.selectbox(
            "⏱️ 요리 가능 시간",
            ["10분 이내 (초스피드)", "15분~20분 (보통)", "30분 이상 (정성 요리)", "시간 상관없음"]
        )
    with col3:
        baby_condition = st.text_input("아기 컨디션 (선택)", placeholder="예: 이가 나는 중, 밥 잘 먹음")

    additional_note = st.text_input(
        "추가 요청사항 (선택)", 
        placeholder="예: 매운 것 제외, 소금 간 줄이기 등"
    )

    submitted = st.form_submit_button("✨ 냉장고 재료 + 캡처 사진 매칭하여 레시피 찾기", type="primary", use_container_width=True)

# 제출 동작
if submitted:
    if not uploaded_files:
        st.warning("⚠️ 캡처해 두신 레시피 사진을 1장 이상 선택해 주세요!")
    elif not fridge_ingredients.strip():
        st.warning("⚠️ 냉장고에 있는 재료를 먼저 입력해 주세요!")
    elif not api_key:
        st.error("Gemini API 키가 등록되지 않았습니다.")
    else:
        with st.spinner(f"AI가 냉장고 재료('{fridge_ingredients}')와 올리신 레시피 사진 {len(uploaded_files)}장을 교차 분석 중입니다..."):
            try:
                # 메모리 과부하 방지를 위한 압축 리사이징
                processed_images = []
                for file in uploaded_files:
                    file.seek(0)
                    img = Image.open(file)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.thumbnail((500, 500))  # 다량 전송 시 500px로 슬림하게 압축
                    processed_images.append(img)
                
                # 최신 AI 모델 호출
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                prompt = f"""
                당신은 20개월 아기를 키우는 부모를 돕는 수석 AI 영유아 셰프입니다.

                [사용자가 보유한 냉장고 재료]
                - 재료 목록: {fridge_ingredients}

                [요리 조건]
                - 레시피 폴더 종류: {folder_choice}
                - 요리 가능 시간: {cooking_time}
                - 아기 컨디션: {baby_condition if baby_condition else '보통'}
                - 추가 요청사항: {additional_note if additional_note else '없음'}

                [미션 및 분석 규칙]
                1. 첨부된 총 {len(processed_images)}장의 레시피/요리 캡처 사진들을 빠짐없이 읽고 종합 분석하세요.
                2. 사진 속 레시피들 중에서, **[사용자가 입력한 냉장고 재료]를 가장 잘 활용할 수 있는 메뉴 2~3가지**를 엄선하여 추천해 주세요.
                3. 만약 냉장고 재료만으로 부족하다면, 대체 가능한 재료나 추가하면 좋은 재료를 친절히 안내해 주세요.
                4. 지정된 요리 시간({cooking_time})과 20개월 아기의 영양 상태에 맞추어 아래 양식으로 답변하세요:

                ---
                ### 💡 [추천 레시피 1] (사진 속 메뉴명)
                - **사진 분석 내용**: (올린 캡처 사진 중 어떤 레시피 사진을 기반으로 했는지 상세 설명)
                - **냉장고 활용 재료**: (입력된 재료 중 사용된 재료)
                - **⏱️ 예상 조리 시간**: 
                - **🍳 20개월 아기 맞춤 조리 방법**: (3~4단계로 간결하게)

                ### 💡 [추천 레시피 2] (사진 속 메뉴명)
                - **사진 분석 내용**:
                - **냉장고 활용 재료**:
                - **⏱️ 예상 조리 시간**:
                - **🍳 20개월 아기 맞춤 조리 방법**:

                ### 👶 20개월 아기 영양 & 섭취 팁
                - (냉장고 재료와 아기 상태를 고려한 영양 팁)
                ---
                """
                
                request_content = [prompt] + processed_images
                response = model.generate_content(request_content)
                
                st.success(f"🎉 총 {len(uploaded_files)}장의 레시피 사진 분석 및 냉장고 재료 매칭이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ 분석 도중 오류가 발생했습니다: {str(e)}")
