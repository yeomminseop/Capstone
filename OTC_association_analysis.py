import pandas as pd
import matplotlib.pyplot as plt
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
import pickle, os

from visualization_function import draw_rules_for_group, draw_lift_heatmap, draw_chord_diagram


"""
전처리된 데이터셋 불러오고, 효능이 같은(atc 앞 4자리 일치) OTC 그룹화
그룹들 중에서 빈도가 적어 의미없는 그룹 cutoff(빈도 30이하)
"""
# 데이터 불러오기
file_path = 'Medicine/filtered_medicine_info.csv'
medicine_info = pd.read_csv(file_path)

# atc_3 컬럼(앞 4자리)을 기준으로 그룹화
atc_group_counts = medicine_info['atc_3'].value_counts().reset_index()
atc_group_counts.columns = ['atc_3', 'count']

# 결과 출력 -> 총 97개의 ATC 그룹 발생(효능이 일치하는 그룹)
print("************************ATC 앞 4자리 기준 그룹************************")
print(atc_group_counts)

# 그룹별 빈도에서 30개 이상인 그룹만 선택
selected_groups = atc_group_counts[atc_group_counts['count'] >= 50]['atc_3'].tolist()
# print(len(selected_groups)) # 100개 이상: 21개 그룹 / 50개 이상: 38개 그룹 / 30개 이상: 50개 그룹

# 원본 데이터에서 해당 그룹들만 필터링
atc_group_cutoff = medicine_info[medicine_info['atc_3'].isin(selected_groups)]

# selected_groups 기준으로 필터링된 그룹 빈도 데이터프레임 만들기
filtered_group_counts = atc_group_counts[atc_group_counts['atc_3'].isin(selected_groups)]

"""
상위 10개, 하위 10개 ATC 그룹 추출하여 시각화하기
"""
top_10 = filtered_group_counts.nlargest(10, 'count')
bottom_10 = filtered_group_counts.nsmallest(10, 'count')

combined = pd.concat([top_10, bottom_10])
colors = ['skyblue'] * 10 + ['gray'] * 10

plt.figure(figsize=(12, 6))
plt.bar(combined['atc_3'], combined['count'], color=colors)
plt.title('Top & Bottom 10 ATC groups')
plt.xlabel('ATC group')
plt.ylabel('OTC count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

### 상위, 하위 10개씩 별도로 시각화
# max_count = filtered_group_counts['count'].max()
#
# plt.figure(figsize=(10, 5))
# plt.bar(top_10['atc_3'], top_10['count'])
# plt.title('Top 10 ATC group')
# plt.xlabel('ATC group')
# plt.ylabel('OTC count')
# plt.ylim(0, max_count)  # y축 고정
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()
#
# plt.figure(figsize=(10, 5))
# plt.bar(bottom_10['atc_3'], bottom_10['count'], color='gray')
# plt.title('Bottom 10 ATC group')
# plt.xlabel('ATC group')
# plt.ylabel('OTC count')
# plt.ylim(0, max_count)  # y축 고정
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

"""
fp-growth 적용 및 각 ATC 그룹 연관 규칙 찾기
"""
# 분석 대상 그룹 리스트 (전체 50개)
target_groups = selected_groups

fp_results = {}

for atc_code in target_groups:
    print(f"\n🔍 ATC 그룹: {atc_code}")

    # 1. 해당 그룹의 데이터만 추출
    group_df = atc_group_cutoff[atc_group_cutoff['atc_3'] == atc_code]

    # 2. 제품별 주성분 리스트로 분리
    transactions = group_df['ing_en'].dropna().apply(
        lambda x: [i.strip().lower() for i in x.split('/') if i.strip()]
    ).tolist()

    if len(transactions) == 0:
        print("⚠️ 트랜잭션 없음, 건너뜀")
        continue

    # 3. 전체 등장 성분 카운트 → 상위 50개만 선택
    all_ingredients = [ingredient for sublist in transactions for ingredient in sublist]
    ingredient_counts = pd.Series(all_ingredients).value_counts()
    top_50_ingredients = ingredient_counts.head(50).index.tolist()

    # 4. TransactionEncoder → 원-핫 인코딩
    te = TransactionEncoder()
    te_result = te.fit_transform(transactions)
    df = pd.DataFrame(te_result, columns=te.columns_)

    # 5. 상위 50개 성분만 컬럼으로 남김
    df_filtered = df[top_50_ingredients]

    # 6. FP-growth 실행 (0.1 이상) + 최대 조합 수 3개로 제한(일반 OTC 조합 주성분 2~3가지)
    frequent_itemsets = fpgrowth(df_filtered, min_support=0.1, use_colnames=True, max_len=3)

    fp_results[atc_code] = frequent_itemsets
    print(frequent_itemsets)


# 연관 규칙 결과 저장 딕셔너리
all_rules_results = {}
single_rules_results = {}  # 단항 규칙 (1:1)
multi_rules_results = {}   # 다항 규칙 (2+:1 or N:M)

for atc_code, freq_items in fp_results.items():
    if freq_items.empty:
        continue

    print(f"\n🔍 ATC 그룹: {atc_code}")

    # 전체 연관 규칙 생성
    rules = association_rules(freq_items, metric='lift', min_threshold=1.0)
    if rules.empty:
        print("⚠️ 연관 규칙 없음")
        continue

    # 전체 저장
    all_rules_results[atc_code] = rules

    # 1:1 단항 규칙
    single_rules = rules[
        (rules['antecedents'].apply(lambda x: len(x) == 1)) &
        (rules['consequents'].apply(lambda x: len(x) == 1))
    ]

    # 2+:1 or N:M 다항 규칙
    multi_rules = rules[
        (rules['antecedents'].apply(lambda x: len(x) > 1)) |
        (rules['consequents'].apply(lambda x: len(x) > 1))
    ]

    single_rules_results[atc_code] = single_rules
    multi_rules_results[atc_code] = multi_rules

    print(f"✅ {atc_code}: 단항 규칙 {len(single_rules)}개, 다항 규칙 {len(multi_rules)}개")

# 단항 규칙 많은 순서로 보기
group_rule_counts = {
    atc: len(rules)
    for atc, rules in single_rules_results.items()
    if not rules.empty
}

sorted_groups = sorted(group_rule_counts.items(), key=lambda x: x[1], reverse=True)

# 상위 5개 ATC 그룹만 시각화
for atc, count in sorted_groups[:5]:
    print(f"{atc} ➜ 단항 규칙 수: {count}")
    draw_rules_for_group(atc, fp_results[atc]) # 네트워크 시각화
    draw_lift_heatmap(atc, single_rules_results[atc]) # 히트맵 시각화
    draw_chord_diagram(atc, single_rules_results[atc]) # chord 다이어그램 시각화

# FP-Growth 룰 저장 (추천 성분 추출에 사용됨)
os.makedirs('data', exist_ok=True) # 룰 저장 폴더 생성
with open('data/fp_rules.pkl', 'wb') as f:
    pickle.dump(single_rules_results, f)

# 전체 의약품 정보 저장 (유사 제품 매칭에 사용됨)
medicine_info.to_csv('data/filtered_medicine_info.csv', index=False)



