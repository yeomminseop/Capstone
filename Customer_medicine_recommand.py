import pandas as pd

# 1. 데이터 불러오기
file_path = "Medicine/filtered_medicine_info.csv"  # 파일 경로 맞게 수정
medicine_df = pd.read_csv(file_path)

# 2. ATC_3 코드 → 내부 효능 카테고리 매핑
atc3_effect_mapping = {
    "A11J": "영양제(기타 비타민)",
    "R05X": "기타 호흡기계약물",
    "M02A": "국소 진통소염제",
    "M01A": "비스테로이드성 소염진통제",
    "R05C": "거담제",
    "R05D": "기침 억제제",
    "A06A": "완하제",
    "A07E": "지사제",
    "R01B": "비충혈 제거제",
    "R06A": "항히스타민제",
    "N02B": "해열진통제",
    "A11C": "비타민 A, D 및 조합",
    "A02B": "위산분비억제제",
    "A01A": "구강용 소독제",
    "A05B": "간기능 개선제",
    "A12C": "미네랄 보충제",
    "D08A": "국소 살균소독제",
    "A13A": "대사촉진제",
    "A04A": "항구토제",
    "N05C": "수면제 및 진정제",
    "N05B": "항불안제",
    "M03B": "근이완제",
    "D04A": "피부질환 치료제",
    "D06A": "국소 항생제",
    "A07D": "소화기계 항감염제"
}

# 3. 증상 키워드 → 복수 효능 카테고리 매핑
symptom_to_effects = {
    "두통": ["해열진통제"],
    "감기": ["기타 호흡기계약물", "기침 억제제", "거담제"],
    "인후염": ["구강용 소독제"],
    "알레르기": ["항히스타민제"],
    "기침": ["기침 억제제", "거담제"],
    "콧물": ["항히스타민제"],
    "발열": ["해열진통제"],
    "위염": ["위산분비억제제"],
    "소화불량": ["위산분비억제제"],
    "스트레스성 소화장애": ["위산분비억제제"],
    "설사": ["지사제"],
    "변비": ["완하제"],
    "장트러블": ["지사제", "완하제"],
    "피부염": ["국소 살균소독제"],
    "가려움증": ["항히스타민제", "피부질환 치료제"],
    "피로누적": ["대사촉진제", "영양제(기타 비타민)"],
    "생리통": ["해열진통제", "비스테로이드성 소염진통제"],
    "근육통": ["국소 진통소염제"],
    "허리통증": ["비스테로이드성 소염진통제"],
    "관절통": ["비스테로이드성 소염진통제"],
    "구강염/입병": ["구강용 소독제"],
    "멀미": ["항구토제"],
    "수면장애": ["수면제 및 진정제"],
    "불안증": ["항불안제"],
    "눈피로": ["비타민 A, D 및 조합"],
    "근육경련": ["근이완제"]
}


# 4. e약은요 링크 생성 (e_code 사용)
def generate_e_drug_url(e_code):
    if pd.isna(e_code):  # e_code가 NaN이면 링크 없음 처리
        return "링크없음"
    e_code_int = int(float(e_code))  # float를 int로 변환해서 .0 완벽 제거
    e_code_str = str(e_code_int)
    base_url = "https://nedrug.mfds.go.kr/searchEasyDrug/easyDetail?itemSeq="
    return base_url + e_code_str


# 5. 데이터 전처리: 효능 매핑
medicine_df['effect_category'] = medicine_df['atc_3'].map(atc3_effect_mapping)
medicine_df['effect_category'] = medicine_df['effect_category'].fillna('기타(Other)')


# 6. 추천 시스템 함수 (랜덤 X, 전체 출력)
def recommend_by_symptom_grouped(symptom_keyword, data):
    """
    증상 키워드 기반 복수 효능 매칭 + 효능별 전체 제품 출력 시스템
    """
    effect_list = symptom_to_effects.get(symptom_keyword)

    if not effect_list:
        print(f"❌ '{symptom_keyword}'에 해당하는 등록된 효능이 없습니다.")
        return

    print(f"\n✅ '{symptom_keyword}' 관련 추천 제품 (효능별 그룹핑)\n")

    for effect in effect_list:
        matched = data[data['effect_category'] == effect].copy()  # ✅ 슬라이스 copy 추가

        if matched.empty:
            continue

        matched['e약은요_링크'] = matched['e_code'].apply(generate_e_drug_url)

        print(f"\n🩺 [효능: {effect}]")
        display_cols = ['product_name', 'comp', 'e약은요_링크']
        print(matched[display_cols].to_string(index=False))


# 7. 메인 실행
if __name__ == "__main__":
    print("💊 고도화된 의약품 추천 시스템에 오신 걸 환영합니다!")

    while True:
        keyword = input("\n찾고 싶은 증상 키워드를 입력하세요 (예: 두통, 감기, 인후염, 알레르기 등) (종료하려면 'exit') : ")

        if keyword.lower() == 'exit':
            print("프로그램을 종료합니다. 👋")
            break
        else:
            recommend_by_symptom_grouped(
                symptom_keyword=keyword,
                data=medicine_df
            )