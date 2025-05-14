import pandas as pd


## 원본 데이터 확인
# 1번 테이블 엑셀 파일 불러오기
file_path = "raw_Medicine_data/1_의약품등제품정보목록.xlsx"
medicine_info = pd.read_excel(file_path)

# ATC 코드 컬럼 이름 확인 (필요하면 변경)
print("컬럼명:", medicine_info.columns.tolist())

# ATC 코드별 개수 계산
atc_column = "ATC코드"  # 실제 컬럼명을 확인하고 변경
atc_counts = medicine_info[atc_column].value_counts()

# 데이터 확인
print("\n✅ ATC 코드별 개수")
print(atc_counts.head(10))  # 상위 10개 출력


## 데이터 전처리
# 1번 데이블 속성명 변경 (한글 → 새 이름)
column_map = {
    "품목기준코드": "product_code",
    "제품명": "product_name",
    "제품영문명": "name_en",
    "업체명": "comp",
    "업체영문명": "comp_en",
    "허가일": "appr_date",
    "품목구분": "product_type",
    "허가번호": "appr_no",
    "취소/취하": "cancel",
    "취소/취하일자": "cancel_date",
    "제형": "form",
    "장축": "length",
    "단축": "width",
    "신약구분": "new_drug",
    "표준코드명": "std_code",
    "ATC코드": "atc",
    "묶음의약품정보": "bundle",
    "e은약요": "e_code",
    "수입제조국": "import_country",
    "주성분영문": "ing_en",
    "주성분": "ing",
    "첨가제": "add",
    "품목분류": "product_category",
    "전문의약품": "rx_only",
    "완제/원료": "raw_material",
    "허가/신고": "appr_type",
    "제조/수입": "origin",
    "마약구분": "narcotic",
    "모양": "shape",
    "색상": "color"
}

mod_medicine_info = medicine_info.rename(columns=column_map)

print("************************컬럼명 수정된 데이터 프레임 확인**************************")
print(mod_medicine_info.head(10))

# 필요한 속성만 추출
selected_columns = [
    "product_code", "product_name", "comp", "cancel", "appr_date", "std_code", "atc",
    "ing_en", "e_code", "raw_material", "appr_type"
]

selected_medicine_info = mod_medicine_info[selected_columns].copy()

print("************************추출한 속성 데이터 프레임 확인****************************")
print(selected_medicine_info.head())
print(selected_medicine_info.info())

## 이상치&결측치 제거
# cancel 변수가 "정상"이고 atc 값이 존재하는 sample 필터링
filtered_medicine_info = selected_medicine_info[
    (selected_medicine_info["cancel"] == "정상") &
    (selected_medicine_info["atc"].notna())
].copy()

print("************************결측치 제거 데이터 프레임 확인****************************")
print(filtered_medicine_info.head())
print(filtered_medicine_info.info())

# ATC 코드 단계별 분리
filtered_medicine_info["atc_1"] = filtered_medicine_info["atc"].str[0] #1단계
filtered_medicine_info["atc_2"] = filtered_medicine_info["atc"].str[:3] #2단계
filtered_medicine_info["atc_3"] = filtered_medicine_info["atc"].str[:4] #3단계
filtered_medicine_info["atc_4"] = filtered_medicine_info["atc"].str[:5] #4단계

# 전처리 완료된 데이터 저장(CSV)
filtered_medicine_info.to_csv("raw_Medicine_data/filtered_medicine_info.csv", index=False)


