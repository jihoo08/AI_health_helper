import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import hospital_data
# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("의료 증상 AI 상담 봇 🩺")

# 증상 슬라이더
st.subheader("현재 증상을 선택하세요 (0: 없음, 10: 매우 심함)")
symptoms = {
    "오한": st.slider("오한", 0, 10, 0),
    "열": st.slider("열", 0, 10, 0),
    "복통": st.slider("복통", 0, 10, 0),
    "두통": st.slider("두통", 0, 10, 0),
    "콧물": st.slider("콧물", 0, 10, 0),
    "인후통": st.slider("인후통", 0, 10, 0),
}

if st.button("AI에게 상담하기"):
    # 증상 데이터를 문자열로 변환
    symptoms_text = "\n".join([f"{k}: {v}/10" for k, v in symptoms.items()])

    # 프롬프트 구성
    user_prompt = f"""
    다음은 환자의 증상 척도입니다:

    {symptoms_text}

    이 증상들을 종합적으로 고려하여 환자가 어떤 질환을 의심할 수 있는지,
    그리고 추가로 권장되는 조치(예: 병원 방문 필요 여부, 자가 관리 방법 등)를 알려주세요.
    """

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 의학 지식을 가진 친절한 상담 AI입니다. 진단 대신 참고용 조언을 제공합니다."},
            {"role": "user", "content": user_prompt}
        ]
    )

    ai_reply = response.choices[0].message.content
    st.markdown("### 🧾 AI의 조언")
    st.write(ai_reply)
