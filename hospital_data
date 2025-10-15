import pandas as pd

# CSV 파일 경로
HOSPITAL_CSV = "dongu_hos.csv"

# 병원 데이터 읽기 함수
def get_hospital_data():
  
    try:
        df = pd.read_csv(HOSPITAL_CSV, encoding='cp949')  
    except UnicodeDecodeError:
        df = pd.read_csv(HOSPITAL_CSV, encoding='utf-8')
    return df

# 병원 데이터를 텍스트 형태로 반환 (Streamlit에서 출력용)
def get_hospital_text():
    df = get_hospital_data()
    text = ""
    for _, row in df.iterrows():
        text += f"{row['병원명']} | 주소: {row['주소']} | 전화번호: {row['전화번호']} | 진료과: {row['진료과']}\n"
    return text
