import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import tabulate

# Load 데이터셋과 룰
df = pd.read_csv('data/filtered_medicine_info.csv')

with open('data/fp_rules.pkl', 'rb') as f:
    fp_rules = pickle.load(f)

# WHO 기반 ATC 효능 매핑 (예시 일부)
atc_3_to_effect = {
    'A11A': '종합비타민 보충',
    'A02B': '위염/소화성 궤양',
    'R02A': '인후염 치료',
    # 추가 필요
}

# 성분 정제 함수 (중복 제거, 소문자 통일, 공백 제거)
def clean_ingredient_list(raw):
    return sorted(list({i.strip().lower() for i in str(raw).split('/') if i.strip()}))

def recommend_from_ingredients(input_ings: list):
    input_ings = [i.strip().lower() for i in input_ings]

    # 1. FP-Growth 룰 기반 추천 성분 Top 3
    candidate_rules = []
    for atc, rules in fp_rules.items():
        for _, row in rules.iterrows():
            if input_ings and row['antecedents'].issubset(set(input_ings)):
                candidate_rules.append((atc, list(row['consequents'])[0], row['lift']))

    if candidate_rules:
        # lift 기준 상위 3개 성분 추천
        top_ings = sorted(candidate_rules, key=lambda x: -x[2])[:3]
        recommended = list({item[1] for item in top_ings})
    else:
        recommended = []

    # 2. 확장 조합 생성
    expanded_ings = sorted(list(set(input_ings + recommended)))

    # 3. 제품 성분 벡터화
    df['ing_list'] = df['ing_en'].fillna('').apply(lambda x: [i.strip().lower() for i in x.split('/')])
    joined_ings = df['ing_list'].apply(lambda x: ' | '.join(x))
    vectorizer = CountVectorizer(tokenizer=lambda x: x.split(' | '))
    X = vectorizer.fit_transform(joined_ings)
    expanded_vec = vectorizer.transform([' | '.join(expanded_ings)])

    # 4. cosine 유사도 계산
    cos_sim = cosine_similarity(expanded_vec, X)[0]
    top_idx = cos_sim.argsort()[::-1][:5]
    similar_products = df.iloc[top_idx][['product_name', 'ing_en', 'atc_3']]

    # 5. 가장 많이 나온 ATC 코드 예측
    predicted_atc = similar_products['atc_3'].mode().iloc[0]

    # 6. 확장 조합 포함 제품 비율 (예측된 ATC 그룹 내)
    # 확장 조합을 정제해서 set으로 준비
    expanded_ings = clean_ingredient_list('/'.join(input_ings + recommended))
    expanded_set = set(expanded_ings)

    # 예측 ATC 그룹 내 제품 리스트 정제
    group_df = df[df['atc_3'] == predicted_atc].copy()
    group_df['ing_list'] = group_df['ing_en'].fillna('').apply(clean_ingredient_list)

    # 확장 조합이 포함된 제품 판별
    group_df['has_all'] = group_df['ing_list'].apply(
        lambda x: expanded_set.issubset(set(x))
    )
    # 🔍 디버깅
    for i, row in group_df.iterrows():
        missing = expanded_set - set(row['ing_list'])
        if not missing:
            print(f"✅ {row['product_name']} 포함")
        else:
            print(f"❌ {row['product_name']} 누락 → {missing}")

    # 비율 계산
    coverage_percent = 100 * group_df['has_all'].sum() / len(group_df)

    # 7. 효능 요약
    effect = atc_3_to_effect.get(predicted_atc, '효능 정보 없음')

    # 결과 포맷
    # 유사 제품 표 만들기
    similar_df = similar_products[['product_name', 'ing_en', 'atc_3']].copy()
    similar_df.columns = ['제품명', '주요 성분', 'atc']
    table_str = tabulate.tabulate(similar_df.values.tolist(), headers=similar_df.columns, tablefmt="github")

    # 요약 문장 생성
    summary = f"""✅ 입력된 성분 {', '.join(input_ings)}은(는) {', '.join(recommended)}과 자주 함께 사용됩니다.
    ➡️ 예측된 ATC 그룹은 {predicted_atc} ({effect}) 입니다.
    📊 확장 조합은 이 ATC 그룹 내 제품 중 {coverage_percent:.1f}%에서 실제 사용되고 있습니다.
    """

    # 결과 딕셔너리에 추가
    return {
        'input_ingredients': input_ings,
        'recommended_ingredients': recommended,
        'expanded_combination': expanded_ings,
        'predicted_atc': predicted_atc,
        'expected_effect': effect,
        'atc_internal_coverage_percent': round(coverage_percent, 2),
        'similar_products_table': table_str,
        'summary': summary
    }