from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd
from eda_01 import selected_groups, atc_group_cutoff

# 연관 규칙 적용 결과 저장 dictionary 설정
fp_results = {}
rules_results = {}
single_rules_results = {}
multi_rules_results = {}


for atc_code in selected_groups:
    print(f"\n🔍 ATC 그룹: {atc_code}")
    group_df = atc_group_cutoff[atc_group_cutoff['atc_3'] == atc_code]

    # 주성분 리스트로 분리
    transactions = group_df['ing_en'].dropna().apply(
        lambda x: [i.strip().lower() for i in x.split('/') if i.strip()]
    ).tolist()

    if len(transactions) == 0:
        print("⚠️ 트랜잭션 없음 → 건너뜀")
        continue

    # 전체 성분 빈도 기준 상위 50개만 사용
    all_ingredients = [i for sublist in transactions for i in sublist]
    top_50 = pd.Series(all_ingredients).value_counts().head(50).index.tolist()

    # 원-핫 인코딩(주성분이 있으면 1, 없으면 0)
    te = TransactionEncoder()
    te_arr = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_arr, columns=te.columns_)[top_50]

    # FP-Growth 실행 + 최대 조합 수 3개로 제한(일반 OTC 조합 주성분 2~3가지)
    freq_items = fpgrowth(df, min_support=0.1, use_colnames=True, max_len=3)
    if freq_items.empty:
        continue
    fp_results[atc_code] = freq_items

    # 연관 규칙 추출
    rules = association_rules(freq_items, metric="lift", min_threshold=1.0)
    if rules.empty:
        continue
    rules_results[atc_code] = rules

    # 단항 규칙 (1:1)
    single_rules = rules[
        (rules['antecedents'].apply(len) == 1) &
        (rules['consequents'].apply(len) == 1)
    ]
    single_rules_results[atc_code] = single_rules

    # 다항 규칙 (2+:1 or N:M)
    multi_rules = rules[
        (rules['antecedents'].apply(len) > 1) |
        (rules['consequents'].apply(len) > 1)
    ]
    multi_rules_results[atc_code] = multi_rules

    print(f"✅ 단항 {len(single_rules)}개, 다항 {len(multi_rules)}개 규칙 추출 완료")


"""
연관 규칙 기반 최적 조합 리스트 정리
"""

# 결과 저장용 리스트
summary_rows = []

# 기준값(하이퍼파라미터 조정할 것)
min_support = 0.1 #최소 지지도
min_confidence = 0.6 #최소 신뢰도
min_lift = 1.5 #최소 향상도
top_n = 5  # 각 그룹당 상위 5개 rule 추출

for atc_code in selected_groups:
    # 규칙이 없는 그룹은 제외
    if atc_code not in rules_results:
        continue
    rules_df = rules_results[atc_code]
    if rules_df.empty:
        continue

    # 필터링된 연관 규칙 추출
    filtered = rules_df[
        (rules_df['support'] >= min_support) &
        (rules_df['confidence'] >= min_confidence) &
        (rules_df['lift'] >= min_lift)
    ]
    # print(f"✅ {atc_code}: {len(filtered)}개의 필터된 룰")

    if filtered.empty:
        continue

    # lift 기준 정렬 → 상위 N개 추출
    top_rules = filtered.sort_values(by='lift', ascending=False).head(top_n)

    # 결과 정리
    for _, row in top_rules.iterrows():
        summary_rows.append({
            'ATC 그룹': atc_code,
            'Antecedents': ', '.join(sorted(row['antecedents'])),
            'Consequents': ', '.join(sorted(row['consequents'])),
            'support': round(row['support'], 3),
            'confidence': round(row['confidence'], 3),
            'lift': round(row['lift'], 3)
        })

# 결과 DataFrame 생성
rules_summary_df = pd.DataFrame(summary_rows)
print(rules_summary_df.head(20))  # 앞부분 미리보기

# 연관 규칙 결과 저장
rules_summary_df.to_csv("atc_rule_summary.csv", index=False)