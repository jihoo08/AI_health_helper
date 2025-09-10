# app.py
import os
import streamlit as st
import openai
from dotenv import load_dotenv
from typing import List, Dict

# .env 파일 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = st.sidebar.text_input("OpenAI API Key", type="password")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="의료정보 챗봇 데모", layout="wide")
st.title("의료정보 서비스 봇 — 증상 슬라이더 버전")

st.markdown(
    """
**주의:** 이 챗봇은 일반 정보 제공용입니다. 
진단·치료는 반드시 의료 전문가와 상의하세요.
"""
)

SYSTEM_PROMPT = (
    "You are a helpful medical information assistant. "
    "The user provides symptom severity on a scale of 0–10 for several categories. "
    "Summarize the likely general health context, provide general medical information, "
    "and always include a disclaimer that you are not a substitute for professional medical advice."
)

if "history" not in st.session_state:
    st.session_state.history: List[Dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

# 사이드바 옵션
with st.sidebar:
    st.header("설정")
    model = st.selectbox("모델", options=["gpt-3.5-turbo"], index=0)
    max_tokens = st.slider("Max tokens", 100, 2000, 600)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2)
    clear = st.button("대화 초기화")

if clear:
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.experimental_rerun()

# === 증상 입력 슬라이더 ===
st.subheader("증상 척도 입력 (0=없음, 10=매우 심함)")
symptoms = {
    "오한": st.slider("오한", 0, 10, 0),
    "열": st.slider("열", 0, 10, 0),
    "복통": st.slider("복통", 0, 10, 0),
    "두통": st.slider("두통", 0, 10, 0),
    "콧물": st.slider("콧물", 0, 10, 0),
    "인후통": st.slider("인후통", 0, 10, 0),
}

if st.button("분석 요청"):
    # 사용자 입력을 하나의 문자열로 요약
    user_input = "증상 척도:\n" + "\n".join([f"- {k}: {v}/10" for k, v in symptoms.items()])
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.spinner("응답 생성 중..."):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=st.session_state.history,
                temperature=float(temperature),
                max_tokens=int(max_tokens),
                n=1,
            )
            content = resp["choices"][0]["message"]["content"]
            st.session_state.history.append({"role": "assistant", "content": content})
        except Exception as e:
            st.error(f"API 호출 중 오류 발생: {e}")

# 채팅 기록 출력
for msg in st.session_state.history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**사용자:** {msg['content']}")
    else:
        st.markdown(f"**봇:** {msg['content']}")

st.markdown("---")
st.markdown(
    """
**면책 고지:**  
이 앱은 증상 척도를 기반으로 일반 의료정보를 제공합니다.  
**진단·치료를 대신하지 않으며, 심각한 증상 시 즉시 전문 의료기관을 방문하세요.**
"""
)
