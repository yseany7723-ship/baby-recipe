import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="20개월 아기 AI 레시피 분석기", page_icon="👶")

st.title("👶 20개월 아기 AI 레시피 분석기")
st.write("핸드폰 1, 2, 3번 폴더의 사진들을 **여러 장(또는 전체)** 선택해서 올리시면 AI가 한꺼번에 분석하여 맞춤 요리를 추천해 드립니다!")

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

# 2. 다중 이미지 업로드 설정 (accept_multiple_files=True)
uploaded_files = st.file_uploader(
    "📷 핸드폰 갤러리에서 사진들을 여러 장 선택해 주세요 (다중 선택 지원)", 
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True  # 여러 장 한 번에 선택 가능하도록 설정
)

if uploaded_files:
    st.success(f"📸 총 {len(uploaded_files)}장의 사진이 등록되었습니다.")
    
    # 업로드된 이미지 4개씩 줄지어 미리보기
    images = []
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        img = Image.open(file)
        images.append(img)
        with cols[idx % 4]:
            st.image(img, use_container_width=True)
    
    additional_note = st.text_input(
        "추가 요청사항 (선택)", 
        placeholder="예: 10분 이내 조리, 매운 것 제외"
    )
    
    if st.button("✨ AI 셰프에게 전체 사진 분석받기", type="primary", use_container_width=True):
        if not api_key:
            st.error("Gemini API 키가 등록되지 않아 분석을 시작할 수 없습니다.")
        else:
            with st.spinner(f"AI가 올리신 {len(uploaded_files)}장의 사진을 한꺼번에 정밀 분석 중입니다..."):
                try:
                    # 이미지 분석이 가능한 Gemini 1.5 Flash 모델 사용
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    당신은 20개월 아기를 키우는 부모를 돕는 수석 AI 영유아 셰프입니다.
                    
                    [상황 정보]
                    - 선택한 폴더 카테고리: {folder_choice}
                    - 아기 컨디션: {baby_condition if baby_condition else '보통'}
                    - 추가 요청사항: {additional_note if additional_note else '없음'}
                    - 제공된 사진 수: 총 {len(uploaded_files)}장
                    
                    [작업 안내]
                    1. 첨부된 모든 사진들(레시피 캡처본 또는 재료 사진들)의 내용을 종합적으로 분석하세요.
                    2. 올려진 사진 속의 요리법/재료들을 종합 고려하여 20개월 아기에게 꼭 맞는 2가지 맞춤 레시피를 골라주세요.
                    3. 다음 내용이 명확히 포함되어야 합니다:
                       - 💡 추천 요리 이름 및 사진 분석 요약
                       - 🛒 필요 재료 (사진 속 내용 활용)
                       - 🍳 20개월 아기 맞춤 조리 순서 (3~4단계)
                       - 👶 20개월 아기 영양 & 섭취 주의 팁
                       - 📌 두 메뉴 중 오늘 더 추천하는 요리와 그 이유
                    """
                    
                    # 프롬프트 텍스트와 모든 이미지 리스트를 함께 Gemini 전달
                    content = [prompt] + images
                    response = model.generate_content(content)
                    
                    st.success("분석이 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("👆 위 버튼을 누르고 갤러리 창이 열리면, 손가락으로 원하는 사진들을 여러 장(또는 전체) 터치/드래그하여 올려보세요.")
