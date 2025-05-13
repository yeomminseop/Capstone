import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from PIL import Image
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from wordcloud import WordCloud
from mlxtend.frequent_patterns import association_rules
import pickle, os

# macOS용 한글 폰트 설정 (예: AppleGothic)
mpl.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

"""
전처리된 데이터셋 불러오고, 효능이 같은(ATC 3단계) OTC 그룹화
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

# 그룹별 빈도에서 50개 이상인 그룹만 선택
selected_groups = atc_group_counts[atc_group_counts['count'] >= 50]['atc_3'].tolist()
# print(len(selected_groups)) # 100개 이상: 21개 그룹 / 50개 이상: 38개 그룹 / 30개 이상: 50개 그룹

# 원본 데이터에서 해당 그룹들만 필터링
atc_group_cutoff = medicine_info[medicine_info['atc_3'].isin(selected_groups)]

# selected_groups 기준으로 필터링된 그룹 빈도 데이터프레임 만들기
filtered_group_counts = atc_group_counts[atc_group_counts['atc_3'].isin(selected_groups)]

"""
ATC 그룹별 주성분 빈도 시각화
각 ATC 그룹에서 많이 사용되는 주성분들 확인
"""

if __name__ == "__main__":

    # 그룹 내 OTC 수 상위 10개, 하위 10개 ATC 그룹 추출하여 시각화
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


    # 분석 대상 그룹 리스트 (전체 50개)
    target_groups = selected_groups

    # 분석할 그룹 리스트(38개 그룹)
    groups_to_plot = target_groups
    top_n = 15

    # 폰트 설정
    plt.rc('font', family='AppleGothic')

    # 각 ATC 그룹별 주성분 빈도 시각화
    for atc_code in groups_to_plot:
        group_df = atc_group_cutoff[atc_group_cutoff['atc_3'] == atc_code]

        # 성분 분리
        transactions = group_df['ing_en'].dropna().apply(lambda x: [i.strip().lower() for i in x.split('/')])
        all_ingredients = [i for sublist in transactions for i in sublist]
        ingredient_counts = pd.Series(all_ingredients).value_counts()

        if ingredient_counts.empty:
            print(f"⚠️ {atc_code}: 유효한 성분 없음 → 스킵")
            continue

        # WordCloud
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            colormap='tab10',
            prefer_horizontal=1.0,
            max_words=60,
            min_font_size=10
        ).generate_from_frequencies(ingredient_counts)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'{atc_code} 주요 성분 WordCloud', fontsize=14)
        plt.show()

        # 가로 막대 그래프
        plt.figure(figsize=(8, 6))
        ingredient_counts.head(top_n).sort_values().plot(kind='barh', color='skyblue')
        plt.title(f'{atc_code} 주요 성분 Top {top_n}', fontsize=14)
        plt.xlabel('빈도수')
        plt.tight_layout()
        plt.show()

# fp_results = {}
#
# for atc_code in target_groups:
#     print(f"\n🔍 ATC 그룹: {atc_code}")
#
#     # 해당 그룹의 데이터만 추출
#     group_df = atc_group_cutoff[atc_group_cutoff['atc_3'] == atc_code]
#
#     # 제품별 주성분 리스트로 분리
#     transactions = group_df['ing_en'].dropna().apply(
#         lambda x: [i.strip().lower() for i in x.split('/') if i.strip()]
#     ).tolist()
#
#     if len(transactions) == 0:
#         print("트랜잭션 없음, 건너뜀")
#         continue
#
#     # 전체 등장 성분 카운트 → 상위 50개만 선택
#     all_ingredients = [ingredient for sublist in transactions for ingredient in sublist]
#     ingredient_counts = pd.Series(all_ingredients).value_counts()
#     top_50_ingredients = ingredient_counts.head(50).index.tolist()
#
#     # TransactionEncoder → 원-핫 인코딩
#     te = TransactionEncoder()
#     te_result = te.fit_transform(transactions)
#     df = pd.DataFrame(te_result, columns=te.columns_)
#
#     # 상위 50개 성분만 컬럼으로 남김
#     df_filtered = df[top_50_ingredients]
#
#     # FP-growth 실행 (0.1 이상) + 최대 조합 수 3개로 제한(일반 OTC 조합 주성분 2~3가지)
#     frequent_itemsets = fpgrowth(df_filtered, min_support=0.1, use_colnames=True, max_len=3)
#
#     fp_results[atc_code] = frequent_itemsets
#     print(frequent_itemsets)

