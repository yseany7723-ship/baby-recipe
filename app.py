import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="20개월 아기 AI 레시피 분석기", page_icon="👶")

st.title("👶 20개월 아기 AI 레시피 분석기")
st.write("핸드폰 1, 2, 3번 폴더의 사진들을 선택해서 올리시면 AI가 분석하여 맞춤 요리를 추천해 드립니다!")

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

# 2. 다중 이미지 업로드
uploaded_files = st.file_uploader(
    "📷 핸드폰 갤러리에서 사진들을 선택해 주세요 (여러 장 가능)", 
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"📸 총 {len(uploaded_files)}장의 사진이 선택되었습니다.")
    
    additional_note = st.text_input(
        "추가 요청사항 (선택)", 
        placeholder="예: 10분 이내 조리, 매운 것 제외"
    )
    
    if st.button("✨ AI 셰프에게 전체 사진 분석받기", type="primary", use_container_width=True):
        if not api_key:
            st.error("Gemini API 키가 등록되지 않아 분석을 시작할 수 없습니다.")
        else:
            with st.spinner(f"AI가 {len(uploaded_files)}장의 사진 용량을 최적화하여 분석 중입니다... 잠시만 기다려주세요."):
                try:
                    # 스마트폰 대용량 이미지 용량 최적화 (자동 리사이징)
                    processed_images = []
                    for file in uploaded_files:
                        img = Image.open(file)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        # 가로/세로 최대 1024px로 조정하여 전송 속도 향상
                        img.thumbnail((1024, 1024))
                        processed_images.append(img)
                    
                    # Gemini 1.5 Flash 모델 불러오기
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    당신은 20개월 아기를 키우는 부모를 돕는 수석 AI 영유아 셰프입니다.
                    
                    [상황 정보]
                    - 선택한 폴더: {folder_choice}
                    - 아기 컨디션: {baby_condition if baby_condition else '보통'}
                    - 추가 요청사항: {additional_note if additional_note else '없음'}
                    
                    [작업 안내]
                    1. 첨부된 {len(processed_images)}장의 사진 속 레시피, 음식, 재료들을 정밀 분석하세요.
                    2. 20개월 아기에게 꼭 맞춘 추천 레시피 2가지를 작성해 주세요.
                    3. 다음 내용이 명확히 포함되어야 합니다:
                       - 💡 추천 요리 이름 및 사진 분석 결과 요약
                       - 🛒 필요 재료 (사진 속 내용 활용)
                       - 🍳 20개월 아기 맞춤 조리 순서 (3~4단계)
                       - 👶 20개월 아기 영양 & 섭취 주의 팁
                       - 📌 두 메뉴 중 오늘 가장 추천하는 요리와 그 이유
                    """
                    
                    # 프롬프트와 리사이즈된 이미지들을 함께 전달
                    request_content = [prompt] + processed_images
                    response = model.generate_content(request_content)
                    
                    st.success("분석이 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.info("💡 팁: API 키 설정이나 사진 개수를 3~5장 정도로 줄여서 시도해 보세요.")
else:
    st.info("👆 위 버튼을 눌러 갤러리에서 사진들을 선택해 주세요.")
