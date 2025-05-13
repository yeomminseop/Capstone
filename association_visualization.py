import pandas as pd
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

# ✅ 데이터 불러오기
df = pd.read_csv("atc_rule_summary.csv")
target_atc = "R05X"
df = df[df["ATC 그룹"] == target_atc].sort_values(by="lift", ascending=False).head(20)

# ✅ 엣지 리스트 생성
edges = []
nodes_set = set()
for _, row in df.iterrows():
    ante = row["Antecedents"].split(", ")
    cons = row["Consequents"].split(", ")
    for a in ante:
        for c in cons:
            if a != c:
                edges.append((a, c, row["support"]))
                nodes_set.update([a, c])

# ✅ 노드 리스트 구성
nodes = list(nodes_set)
node_df = pd.DataFrame({'name': nodes})

# ✅ 엣지 DataFrame
edge_df = pd.DataFrame(edges, columns=["source", "target", "value"])

# ✅ Holoviews용 Chord 생성
chord = hv.Chord((edge_df, hv.Dataset(node_df, 'name')))

# ✅ 시각화 설정
chord.opts(
    opts.Chord(
        labels='name',
        node_color='name',
        edge_color='source',
        cmap='Category20',
        edge_cmap='Category20',
        edge_line_width=hv.dim('value') * 5,  # 엣지 두께 조정
        edge_alpha=0.7,
        node_size=15,
        width=800,
        height=800,
        title=f"{target_atc} 주성분 원형 리본형 Chord Diagram",
        tools=['hover']
    )
)

import panel as pn
pn.extension()

hv.save(chord, "r05x_chord_diagram.html", backend="bokeh")