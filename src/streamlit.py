import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
import sys
from translations import get_translation

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 초기화
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# 병원 검색 시스템 초기화
@st.cache_resource
def init_hospital_search():
    try:
        from hospital_search import HospitalSearch
        
        if os.path.exists('data.csv'):
            return HospitalSearch('data.csv')
        else:
            st.error("data.csv 파일을 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"병원 검색 시스템 초기화 중 오류 발생: {e}")
        return None

hospital_search = init_hospital_search()

# 언어 설정 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'ko'

# CSS 스타일 적용
st.markdown("""
<style>
    /* 전체 배경 색상 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 메인 타이틀 스타일 */
    .main-title {
        color: #2c3e50;
        text-align: center;
        padding: 20px 0;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 30px;
    }
    
    /* 서브헤더 스타일 */
    .subheader {
        color: #34495e;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
    }
    
    /* 위치 입력창 스타일 - 파란 선만 */
    .location-input {
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #3498db;
        margin: 15px 0;
        background-color: transparent;
    }
    
    /* 증상 입력창 스타일 - 노란 선만 */
    .symptom-input {
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #ff9800;
        margin: 15px 0;
        background-color: transparent;
    }
    
    /* 모든 입력 필드의 포커스 효과 완전 제거 */
    .stTextInput input:focus, .stTextArea textarea:focus,
    [data-baseweb="input"] input:focus,
    [data-baseweb="textarea"] textarea:focus,
    .stTextInput [data-baseweb="input"]:focus-within,
    .stTextArea [data-baseweb="textarea"]:focus-within {
        outline: none !important;
        box-shadow: none !important;
        border-color: #e0e0e0 !important;
    }
    
    /* 텍스트 입력 필드 기본 스타일 - 포커스 시 변화 없음 */
    .stTextInput input {
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        padding: 8px 12px !important;
    }
    
    /* 텍스트 영역 기본 스타일 - 포커스 시 변화 없음 */
    .stTextArea textarea {
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        padding: 8px 12px !important;
    }
    
    /* 슬라이더 컨테이너 스타일 */
    .slider-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* 버튼 스타일 */
    .stButton button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 12px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 25px;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: 600;
    }
    
    .stButton button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* AI 응답 스타일 */
    .ai-response {
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 4px solid #27ae60;
    }
    
    /* 병원 정보 스타일 */
    .hospital-info {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
    
    /* 위험/경고 메시지 스타일 */
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 15px 0;
    }
    
    /* 언어 선택기 스타일 */
    .language-selector {
        background-color: #ecf0f1;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* 언어 버튼 스타일 */
    .stButton button {
        font-size: 14px !important;
        padding: 8px 12px !important;
        margin: 3px 0 !important;
    }
    
    /* 나머지 CSS는 동일하게 유지 */
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #2c3e50; text-align: center; padding: 20px 0; font-size: 2.5rem; font-weight: 700; margin-bottom: 30px; }
    .subheader { color: #34495e; font-size: 1.4rem; font-weight: 600; margin: 25px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #3498db; }
    .location-input { padding: 15px; border-radius: 8px; border: 2px solid #3498db; margin: 15px 0; background-color: transparent; }
    .symptom-input { padding: 15px; border-radius: 8px; border: 2px solid #ff9800; margin: 15px 0; background-color: transparent; }
    .stTextInput input:focus, .stTextArea textarea:focus, [data-baseweb="input"] input:focus, [data-baseweb="textarea"] textarea:focus, .stTextInput [data-baseweb="input"]:focus-within, .stTextArea [data-baseweb="textarea"]:focus-within { outline: none !important; box-shadow: none !important; border-color: #e0e0e0 !important; }
    .stTextInput input { border: 1px solid #e0e0e0 !important; border-radius: 4px !important; padding: 8px 12px !important; }
    .stTextArea textarea { border: 1px solid #e0e0e0 !important; border-radius: 4px !important; padding: 8px 12px !important; }
    .slider-container { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 10px 0; }
    .ai-response { background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; border-left: 4px solid #27ae60; }
    .hospital-info { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 15px 0; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 8px; border: 1px solid #ffeaa7; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

# 언어 선택기
st.sidebar.markdown('<div class="language-selector">', unsafe_allow_html=True)
st.sidebar.markdown("### 🌐 언어 선택 / Language")

# 언어 선택 버튼 - 3x3 그리드로 변경
col1, col2, col3 = st.sidebar.columns(3)
col4, col5, col6 = st.sidebar.columns(3)
col7, col8, col9 = st.sidebar.columns(3)

with col1:
    if st.button("🇰🇷 한국어", use_container_width=True):
        st.session_state.language = 'ko'
        st.rerun()

with col2:
    if st.button("🇺🇸 English", use_container_width=True):
        st.session_state.language = 'en'
        st.rerun()

with col3:
    if st.button("🇵🇭 Filipino", use_container_width=True):
        st.session_state.language = 'fil'
        st.rerun()

with col4:
    if st.button("🇻🇳 Tiếng Việt", use_container_width=True):
        st.session_state.language = 'vi'
        st.rerun()

with col5:
    if st.button("🇨🇳 中文", use_container_width=True):
        st.session_state.language = 'zh'
        st.rerun()

with col6:
    if st.button("🇹🇭 ไทย", use_container_width=True):
        st.session_state.language = 'th'
        st.rerun()

with col7:
    if st.button("🇺🇿 O'zbek", use_container_width=True):
        st.session_state.language = 'uz'
        st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# 현재 언어 가져오기
lang = st.session_state.language

# 메인 타이틀
st.markdown(f'<div class="main-title">{get_translation(lang, "title")}</div>', unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown(f"### {get_translation(lang, 'location_title')}")
    st.markdown('<div class="location-input">', unsafe_allow_html=True)
    location = st.text_input(
        get_translation(lang, "location_placeholder"), 
        placeholder=get_translation(lang, "location_placeholder"),
        key="location_input"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### {get_translation(lang, 'tips_title')}")
    st.info(f"""
    {get_translation(lang, "tip1")}
    {get_translation(lang, "tip2")}
    {get_translation(lang, "tip3")}
    """)

# 증상 입력 섹션
st.markdown(f'<div class="subheader">{get_translation(lang, "symptoms_title")}</div>', unsafe_allow_html=True)

# 증상 슬라이더 그리드
st.markdown(f"#### {get_translation(lang, 'symptoms_intro')}")
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="slider-container">', unsafe_allow_html=True)
    symptoms = {
        get_translation(lang, "chills"): st.slider(get_translation(lang, "chills"), 0, 10, 0, key="chills"),
        get_translation(lang, "fever"): st.slider(get_translation(lang, "fever"), 0, 10, 0, key="fever"),
        get_translation(lang, "stomach_pain"): st.slider(get_translation(lang, "stomach_pain"), 0, 10, 0, key="stomach"),
    }
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="slider-container">', unsafe_allow_html=True)
    symptoms.update({
        get_translation(lang, "headache"): st.slider(get_translation(lang, "headache"), 0, 10, 0, key="headache"),
        get_translation(lang, "runny_nose"): st.slider(get_translation(lang, "runny_nose"), 0, 10, 0, key="runny_nose"),
        get_translation(lang, "sore_throat"): st.slider(get_translation(lang, "sore_throat"), 0, 10, 0, key="sore_throat"),
    })
    st.markdown('</div>', unsafe_allow_html=True)

# 추가 증상 입력
st.markdown('<div class="symptom-input">', unsafe_allow_html=True)
st.markdown(f"#### {get_translation(lang, 'additional_symptoms')}")
additional_symptoms = st.text_area(
    get_translation(lang, "additional_placeholder"),
    placeholder=get_translation(lang, "additional_placeholder"),
    height=100,
    key="additional_symptoms"
)
st.markdown('</div>', unsafe_allow_html=True)

# 상담 버튼
col1, col2, col3 = st.columns([1,2,1])
with col2:
    consult_button = st.button(get_translation(lang, "consult_button"), use_container_width=True)

# 경고 메시지 (위치 미입력 시)
if not location and consult_button:
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.warning(get_translation(lang, "location_warning"))
    st.markdown('</div>', unsafe_allow_html=True)

# 상담 처리
if consult_button and hospital_search is not None:
    # 증상 데이터를 문자열로 변환
    active_symptoms = {k: v for k, v in symptoms.items() if v > 0}
    if active_symptoms:
        symptoms_text = "\n".join([f"{k}: {v}/10" for k, v in active_symptoms.items()])
    else:
        symptoms_text = get_translation(lang, "no_symptoms")
    
    if additional_symptoms:
        symptoms_text += f"\n{get_translation(lang, 'additional_symptoms')}: {additional_symptoms}"
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(get_translation(lang, "analyzing"))
    progress_bar.progress(30)
    
    # 병원 검색
    try:
        status_text.text(get_translation(lang, "finding_hospitals"))
        recommended_hospitals = hospital_search.search_hospitals(
            symptoms_text, 
            location=location if location else None
        )
        progress_bar.progress(70)
    except Exception as e:
        st.error(f"병원 검색 중 오류 발생: {e}")
        recommended_hospitals = pd.DataFrame()
    
    # 병원 정보 포맷팅
    hospital_info = ""
    if not recommended_hospitals.empty:
        hospital_info = f"\n\n🏥 **{get_translation(lang, 'recommended_hospitals')}:**\n\n"
        for idx, hospital in recommended_hospitals.iterrows():
            hospital_name = hospital.get('사업장명', f"{get_translation(lang, 'hospital_name')} 정보 없음")
            address = hospital.get('소재지전체주소', hospital.get('도로명전체주소', f"{get_translation(lang, 'address')} 정보 없음"))
            phone = hospital.get('소재지전화', f"{get_translation(lang, 'phone')} 정보 없음")
            
            hospital_info += f"**{idx+1}. {hospital_name}**\n"
            hospital_info += f"   📍 {address}\n"
            if phone and pd.notna(phone) and phone != f"{get_translation(lang, 'phone')} 정보 없음":
                hospital_info += f"   📞 {phone}\n"
            hospital_info += "\n"
    else:
        hospital_info = f"\n\n⚠️ {get_translation(lang, 'no_hospitals')}"
    
    status_text.text(get_translation(lang, "ai_analyzing"))
    progress_bar.progress(90)
    
    # 언어별 AI 프롬프트 설정
    language_prompts = {
    'ko': "한국어로 답변해주세요.",
    'en': "Please respond in English.",
    'fil': "Mangyaring sumagot sa Filipino.",
    'vi': "Hãy trả lời bằng tiếng Việt.",
    'zh': "请用中文回答。",
    'th': "กรุณาตอบเป็นภาษาไทย",
    'uz': "Iltimos, o'zbek tilida javob bering."
}
    
    # 프롬프트 구성
    user_prompt = f"""
    {language_prompts[lang]}

    다음은 환자의 증상 정보입니다:

    {symptoms_text}

    {hospital_info}

    이 정보를 바탕으로 다음 내용을 친절하게 설명해주세요:
    1. 이러한 증상으로 의심될 수 있는 질환들
    2. 증상의 심각도 평가 (병원 방문이 얼마나 시급한지)
    3. 즉시 실천할 수 있는 자가 관리 방법
    4. 어떤 진료과를 방문하면 좋을지

    매우 중요한 주의사항: 
    - 이것은 진단이 아닌 참고용 조언입니다.
    - 실제 진료는 반드시 의사에게 받아야 합니다.
    - 응급 상황이라면 즉시 119나 응급실을 방문하세요.
    """

    # OpenAI API 호출
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"""당신은 의학 지식을 가진 친절한 상담 AI 어시스턴트입니다. 
                사용자의 증상을 분석하고 적절한 조언을 제공해야 합니다. 
                {language_prompts[lang]}
                항상 다음을 강조하세요:
                - 이것은 참고용 조언일 뿐 진단이 아님
                - 심각한 증상이면 즉시 병원 방문
                - 응급 상황 대처법"""},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content
        progress_bar.progress(100)
        status_text.text(get_translation(lang, "analysis_complete"))
        
    except Exception as e:
        st.error(f"AI API 호출 중 오류 발생: {e}")
        st.stop()
    
    # 결과 표시
    st.markdown("---")
    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
    st.markdown(f"### {get_translation(lang, 'ai_advice')}")
    st.write(ai_reply)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 병원 정보 별도 표시 (있는 경우)
    if not recommended_hospitals.empty:
        st.markdown('<div class="hospital-info">', unsafe_allow_html=True)
        st.markdown(f"### {get_translation(lang, 'recommended_hospitals')}")
        
        for idx, hospital in recommended_hospitals.iterrows():
            hospital_name = hospital.get('사업장명', f"{get_translation(lang, 'hospital_name')} 정보 없음")
            similarity = hospital.get('similarity', 0)
            
            with st.expander(f"🏥 {hospital_name} ({get_translation(lang, 'similarity')}: {similarity:.2f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # 주소 정보
                    address = hospital.get('소재지전체주소', hospital.get('도로명전체주소', f"{get_translation(lang, 'address')} 정보 없음"))
                    st.write(f"**📍 {get_translation(lang, 'address')}:** {address}")
                    
                    # 전화번호
                    phone = hospital.get('소재지전화', '')
                    if phone and pd.notna(phone):
                        st.write(f"**📞 {get_translation(lang, 'phone')}:** {phone}")
                
                with col2:
                    # 진료과목 정보
                    department = hospital.get('진료과목내용명', '')
                    if department and pd.notna(department):
                        st.write(f"**🩺 {get_translation(lang, 'department')}:** {department}")
                    
                    # 병원 종류
                    hospital_type = hospital.get('의료기관종별명', '')
                    if hospital_type and pd.notna(hospital_type):
                        st.write(f"**🏢 {get_translation(lang, 'hospital_type')}:** {hospital_type}")
                    
                    
        st.markdown('</div>', unsafe_allow_html=True)

# 데이터셋 정보 표시
if hospital_search and not hospital_search.data.empty:
    with st.expander(get_translation(lang, "data_info")):
        st.write(f"총 {len(hospital_search.data)} {get_translation(lang, 'total_hospitals')}")
        
        # 보여줄 컬럼 선택
        display_columns = ['사업장명', '소재지전체주소', '진료과목내용명', '의료기관종별명']
        available_columns = [col for col in display_columns if col in hospital_search.data.columns]
        
        if available_columns:
            st.dataframe(hospital_search.data[available_columns].head(10))
        else:
            st.write("표시할 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>
        <p>{get_translation(lang, 'disclaimer')}</p>
        <p>{get_translation(lang, 'emergency')}</p>
    </div>
    """, 
    unsafe_allow_html=True
)