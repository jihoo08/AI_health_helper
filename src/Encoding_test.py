import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

file_path = 'data.csv'
encoding = detect_encoding(file_path)
print(f"감지된 인코딩: {encoding}")

# 인코딩으로 파일 읽기 시도
import pandas as pd
try:
    df = pd.read_csv(file_path, encoding=encoding)
    print("성공적으로 읽었습니다!")
    print("컬럼 목록:", df.columns.tolist())
    print("\n첫 3행:")
    print(df.head(3))
except Exception as e:
    print(f"읽기 실패: {e}")