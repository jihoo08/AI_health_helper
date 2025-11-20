import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class HospitalSearch:
    def __init__(self, data_path):
        # EUC-KR 인코딩으로 데이터 로드
        self.data = pd.read_csv(data_path, encoding='euc-kr')
        print("데이터 컬럼:", self.data.columns.tolist())
        self.vectorizer = None
        self.symptom_vectors = None
        self._prepare_data()
    
    def _prepare_data(self):
        """병원 데이터 전처리 및 벡터화"""
        # 사용 가능한 텍스트 컬럼 찾기
        text_columns = []
        
        if '진료과목내용명' in self.data.columns:
            text_columns.append('진료과목내용명')
        if '사업장명' in self.data.columns:
            text_columns.append('사업장명')
        if '의료기관종별명' in self.data.columns:
            text_columns.append('의료기관종별명')
        
        if not text_columns:
            text_columns = self.data.select_dtypes(include=['object']).columns.tolist()
        
        print(f"사용할 텍스트 컬럼: {text_columns}")
        
        # 증상 텍스트 결합
        self.data['symptom_text'] = self.data[text_columns].fillna('').astype(str).agg(' '.join, axis=1)
        
        # TF-IDF 벡터화 - 한국어 처리를 위해 파라미터 조정
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # 단어와 2-gram 모두 사용
            min_df=2  # 너무 드문 단어는 제외
        )
        self.symptom_vectors = self.vectorizer.fit_transform(self.data['symptom_text'])
        
        print(f"TF-IDF 단어 사장 크기: {len(self.vectorizer.get_feature_names_out())}")
        print(f"총 {len(self.data)}개의 병원 데이터를 벡터화했습니다.")
    
    def map_symptoms_to_departments(self, symptoms_text):
        """증상 텍스트를 진료과목 키워드로 매핑"""
        # 증상-진료과 매핑 딕셔너리
        symptom_mapping = {
            '오한': ['감기', '내과', '호흡기', '발열'],
            '열': ['감기', '내과', '소아과', '발열', '체온'],
            '복통': ['내과', '소화기', '외과', '위장', '복부'],
            '두통': ['내과', '신경과', '두통', '편두통'],
            '콧물': ['이비인후과', '감기', '코', '비염'],
            '인후통': ['이비인후과', '목', '인후', '편도']
        }
        
        # 기본 키워드 (모든 증상에 공통)
        base_keywords = ['병원', '의원', '클리닉', '의료', '진료']
        
        # 증상별 키워드 추출
        department_keywords = base_keywords.copy()
        
        for symptom, keywords in symptom_mapping.items():
            if symptom in symptoms_text:
                department_keywords.extend(keywords)
        
        # 증상 텍스트에서 숫자와 특수문자 제거 후 키워드 추출
        clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', symptoms_text)
        words = clean_text.split()
        department_keywords.extend(words)
        
        # 중복 제거
        department_keywords = list(set(department_keywords))
        
        # 키워드들을 하나의 문자열로 결합
        mapped_text = ' '.join(department_keywords)
        print(f"원본 증상: {symptoms_text}")
        print(f"매핑된 키워드: {mapped_text}")
        
        return mapped_text
    
    def search_hospitals(self, symptoms_text, location=None, top_k=5):
        """증상과 위치 기반 병원 검색"""
        try:
            # 증상 텍스트를 진료과목 키워드로 매핑
            mapped_symptoms = self.map_symptoms_to_departments(symptoms_text)
            
            # 증상 벡터화
            symptom_vector = self.vectorizer.transform([mapped_symptoms])
            
            # 유사도 계산
            similarities = cosine_similarity(symptom_vector, self.symptom_vectors).flatten()
            
            # 결과 정렬
            results = self.data.copy()
            results['similarity'] = similarities
            results = results.sort_values('similarity', ascending=False)
            
            # 위치 필터링
            if location:
                address_columns = ['소재지전체주소', '도로명전체주소']
                location_found = False
                
                for addr_col in address_columns:
                    if addr_col in results.columns:
                        location_mask = results[addr_col].str.contains(location, na=False, case=False)
                        if location_mask.any():
                            results = results[location_mask]
                            location_found = True
                            break
                
                if not location_found:
                    print(f"위치 '{location}'에 해당하는 병원을 찾지 못했습니다. 모든 지역의 병원을 표시합니다.")
            
            # 유사도가 너무 낮은 결과는 제외 (0.01 이상만)
            results = results[results['similarity'] > 0.01]
            
            if len(results) == 0:
                print("유사도가 충분히 높은 병원을 찾지 못했습니다. 모든 병원을 유사도 무관하게 표시합니다.")
                results = self.data.copy()
                if location:
                    for addr_col in address_columns:
                        if addr_col in results.columns:
                            location_mask = results[addr_col].str.contains(location, na=False, case=False)
                            if location_mask.any():
                                results = results[location_mask]
                                break
                results['similarity'] = 0.5  # 기본 유사도 값
                results = results.head(top_k)
            
            return results.head(top_k)
        
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            results = self.data.copy()
            results['similarity'] = 0.3
            if location:
                address_columns = ['소재지전체주소', '도로명전체주소']
                for addr_col in address_columns:
                    if addr_col in results.columns:
                        location_mask = results[addr_col].str.contains(location, na=False, case=False)
                        if location_mask.any():
                            results = results[location_mask]
                            break
            return results.head(top_k)