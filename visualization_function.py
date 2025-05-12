import matplotlib as mpl
from mlxtend.frequent_patterns import association_rules
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# macOS용 한글 폰트 설정 (예: AppleGothic)
mpl.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

def draw_rules_for_group(atc_code, fp_result, top_n=10):

    if fp_result.empty:
        print(f"⚠️ {atc_code}: FP 항목 없음")
        return

    rules = association_rules(fp_result, metric='lift', min_threshold=1.0)
    rules = rules[
        (rules['antecedents'].apply(lambda x: len(x) == 1)) &
        (rules['consequents'].apply(lambda x: len(x) == 1)) &
        (rules['confidence'] >= 0.1)
    ].sort_values(by='lift', ascending=False).head(top_n)

    if rules.empty:
        print(f"⚠️ {atc_code}: 시각화할 규칙 없음")
        return

    G = nx.DiGraph()
    for _, row in rules.iterrows():
        ant = list(row['antecedents'])[0]
        con = list(row['consequents'])[0]
        lift = row['lift']
        G.add_edge(ant, con, weight=lift)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            edge_color='gray', node_size=1500, arrows=True, font_size=10)

    # 엣지 라벨
    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # 제목을 suptitle로 출력
    plt.suptitle(f"ATC 그룹: {atc_code} - 주성분 간 연관성 (Top {top_n})", fontsize=14)

    plt.axis('off')
    plt.tight_layout()
    plt.show()

def draw_lift_heatmap(atc_code, rules_df):
    if rules_df.empty:
        print(f"⚠️ {atc_code}: 규칙 없음")
        return

    # 조건(신뢰도 >= 0.1 / 향상도 >= 1.0)
    filtered_rules = rules_df[
        (rules_df['confidence'] >= 0.1) &
        (rules_df['lift'] >= 1.0)
    ]

    if filtered_rules.empty:
        print(f"⚠️ {atc_code}: 히트맵에 쓸 규칙 없음")
        return

    # 1:1 규칙으로부터 성분 이름 추출
    filtered_rules['antecedent'] = filtered_rules['antecedents'].apply(lambda x: list(x)[0])
    filtered_rules['consequent'] = filtered_rules['consequents'].apply(lambda x: list(x)[0])

    # 피벗 테이블로 lift matrix 구성
    lift_matrix = filtered_rules.pivot(index='antecedent', columns='consequent', values='lift').fillna(0)

    # 히트맵 시각화
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        lift_matrix,
        cmap="Blues",  # 색상만 표현
        linewidths=0.5,
        cbar_kws={'label': 'Lift'}
    )
    plt.title(f"ATC 그룹: {atc_code} - 주성분 간 Lift Heatmap", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

def draw_chord_diagram(atc_code, rules_df, top_n=15):
    if rules_df.empty:
        print(f"⚠️ {atc_code}: 규칙 없음")
        return

    # 조건(신뢰도 >= 0.1 / 향상도 >= 1.0) 및 정렬
    rules = rules_df[
        (rules_df['confidence'] >= 0.1) &
        (rules_df['lift'] >= 1.0)
    ].sort_values(by='lift', ascending=False).head(top_n)

    rules['antecedent'] = rules['antecedents'].apply(lambda x: list(x)[0])
    rules['consequent'] = rules['consequents'].apply(lambda x: list(x)[0])

    all_ingredients = list(set(rules['antecedent']).union(set(rules['consequent'])))
    label_map = {name: i for i, name in enumerate(all_ingredients)}

    source = rules['antecedent'].map(label_map)
    target = rules['consequent'].map(label_map)
    value = rules['lift']

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_ingredients
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color="rgba(173,216,230,0.4)",
            hovertemplate='From %{source.label} to %{target.label}<br>Lift: %{value:.2f}<extra></extra>'
        )
    )])

    # 범례 역할 annotation 추가
    fig.add_annotation(
        x=0.5, y=-0.15,
        showarrow=False,
        text="※ 선 두께는 Lift 값에 비례합니다. (1.0 이상 필터링)",
        font=dict(size=14),
        xref="paper", yref="paper"
    )

    fig.update_layout(
        title_text=f"ATC 그룹 {atc_code} - 주성분 간 Chord diagram",
        font_size=15,
        margin=dict(t=80, b=100)
    )

    fig.show()