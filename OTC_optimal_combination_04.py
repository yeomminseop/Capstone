import pandas as pd

# 파일 불러오기
rules_df = pd.read_csv("data/atc_rule_summary.csv")
medicine_df = pd.read_csv("data/filtered_medicine_info.csv")

# 기준 설정
min_support = 0.1
min_confidence = 0.6
min_lift = 1.5
top_n = 5  # 각 그룹당 최대 5개

results = []

# 그룹별로 수행
for atc_group in rules_df["ATC 그룹"].unique():
    group_rules = rules_df[rules_df["ATC 그룹"] == atc_group]

    # 조건 필터링
    filtered = group_rules[
        (group_rules["support"] >= min_support) &
        (group_rules["confidence"] >= min_confidence) &
        (group_rules["lift"] >= min_lift)
    ].sort_values(by="lift", ascending=False)

    seen_combos = set()
    count = 0

    for _, row in filtered.iterrows():
        antecedents = set(row["Antecedents"].split(", "))
        consequents = set(row["Consequents"].split(", "))
        combo_set = frozenset(antecedents.union(consequents))

        if combo_set in seen_combos:
            continue

        seen_combos.add(combo_set)

        # 조합 포함 제품 검색
        matched = []
        for _, prod in medicine_df.iterrows():
            if pd.isna(prod["ing_en"]):
                continue
            prod_ings = set(i.strip().lower() for i in prod["ing_en"].split("/"))
            if combo_set.issubset(prod_ings):
                matched.append(prod["product_name"])

        results.append({
            "ATC 그룹": atc_group,
            "조합": " + ".join(sorted(combo_set)),
            "Lift": round(row["lift"], 3),
            "Support": round(row["support"], 3),
            "Confidence": round(row["confidence"], 3),
            "사용 OTC 수": len(matched),
            "사용 OTC 예시": ", ".join(matched[:10]) + (" ..." if len(matched) > 10 else "")
        })

        count += 1
        if count >= top_n:
            break

# 결과 저장
final_df = pd.DataFrame(results)
final_df.to_csv("final_optimal_combinations_groupwise.csv", index=False)
print(final_df.head(10))