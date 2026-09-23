import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="20개월 아기 AI 레시피 분석기", page_icon="👶")

st.title("👶 20개월 아기 AI 레시피 분석기")
st.write("핸드폰 1, 2, 3번 폴더의 사진(레시피/재료)을 올리면 AI가 분석하여 맞춤 요리를 추천해 드립니다!")

# Secrets에서 Gemini API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", None)

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("⚠️ API 키가 설정되지 않았습니다. Streamlit Secrets에서 GEMINI_API_KEY를 등록해주세요.")

# 1. 카테고리 및 조건 선택
col1, col2 = st.columns(2)
with col1:
    folder_choice = st.selectbox(
        "어떤 폴더의 사진인가요?", 
        ["1번 (잘 먹는 레시피 사진)", "2번 (해주고 싶은 레시피 사진)", "3번 (아침/간식 사진)"]
    )
with col2:
    baby_condition = st.text_input("오늘 아기 컨디션 (선택)", placeholder="예: 이가 나는 중, 밥 잘 먹음")

# 2. 이미지 업로드
uploaded_file = st.file_uploader(
    "📷 핸드폰 갤러리에서 사진을 올려주세요 (JPG, PNG)", 
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    # 업로드된 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드한 레시피/재료 사진", use_container_width=True)
    
    additional_note = st.text_input(
        "추가 요청사항 (선택)", 
        placeholder="예: 10분 이내 조리, 매운 것 제외"
    )
    
    if st.button("✨ AI 셰프에게 이 사진 분석해서 추천받기", type="primary", use_container_width=True):
        if not api_key:
            st.error("Gemini API 키가 등록되지 않아 분석을 시작할 수 없습니다.")
        else:
            with st.spinner("AI가 올리신 사진을 시각적으로 분석 중입니다..."):
                try:
                    # 이미지 분석이 가능한 Gemini 1.5 Flash 모델 사용 (무료)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    당신은 20개월 아기를 키우는 부모를 돕는 수석 AI 영유아 셰프입니다.
                    
                    [상황 정보]
                    - 선택한 폴더: {folder_choice}
                    - 아기 컨디션: {baby_condition if baby_condition else '보통'}
                    - 추가 요청사항: {additional_note if additional_note else '없음'}
                    
                    [작업 안내]
                    1. 첨부된 사진(레시피 캡처본 또는 재료 사진)을 정밀하게 분석하세요.
                    2. 20개월 아기에게 꼭 맞춘 추천 레시피 2가지를 작성해 주세요.
                    3. 다음 내용이 명확히 포함되어야 합니다:
                       - 💡 추천 요리 이름 및 사진 분석 결과
                       - 🛒 필요 재료 (사진 속 재료 활용)
                       - 🍳 20개월 아기 맞춤 조리 순서 (3~4단계)
                       - 👶 20개월 아기 영양 & 섭취 주의 팁
                    """
                    
                    response = model.generate_content([prompt, image])
                    
                    st.success("분석이 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("👆 위 버튼을 눌러 핸드폰에 있는 레시피나 재료 사진을 올려보세요.")
