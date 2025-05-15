"""
연관규칙 중복을 허용하여 규칙마다 여러 edge 생성
A > B
A, C > B
A, D > B
이라면 A > B 규칙이 3개인데, 이때 한 node에서 같은 node로 가는 edge가 3개 생성됨
"""
# import pandas as pd
# import holoviews as hv
# from holoviews import opts
# hv.extension('bokeh')
#
# from bokeh.palettes import Category20
# from bokeh.models import Div
# from bokeh.layouts import row
# from bokeh.io import output_file, save
#
# # 1. 데이터 불러오기
# df = pd.read_csv("atc_rule_summary.csv")
# target_atc = "R05X"
# df = df[df["ATC 그룹"] == target_atc].sort_values(by="lift", ascending=False).head(20)
#
# # 2. 엣지/노드 구성
# edges = []
# nodes_set = set()
# for _, r in df.iterrows():
#     ante = r["Antecedents"].split(", ")
#     cons = r["Consequents"].split(", ")
#     for a in ante:
#         for c in cons:
#             if a != c:
#                 edges.append((a, c, r["lift"]))
#                 nodes_set.update([a, c])
#
# nodes = sorted(list(nodes_set))
# node_df = pd.DataFrame({'name': nodes})
# edge_df = pd.DataFrame(edges, columns=["source", "target", "value"])
#
# # 색상 매핑
# palette = Category20[20]
# color_map = {name: palette[i % len(palette)] for i, name in enumerate(nodes)}
#
# # 3. Chord 생성
# chord = hv.Chord((edge_df, hv.Dataset(node_df, 'name'))).opts(
#     opts.Chord(
#         labels=None,
#         node_color=hv.dim('name').categorize(color_map),
#         edge_color=hv.dim('source').categorize(color_map),
#         cmap='Category20',
#         edge_cmap='Category20',
#         edge_line_width=hv.dim('value') * 3,
#         edge_alpha=0.7,
#         node_size=15,
#         width=800,
#         height=800,
#         title=f"{target_atc} 주성분 Chord Diagram",
#         tools=['hover']
#     )
# )
#
# # 4. 범례 생성
# legend_html = "<h3 style='font-family:sans-serif;'> RO5X 주성분 </h3><ul style='list-style:none;padding-left:0;'>"
# for name in nodes:
#     color = color_map[name]
#     legend_html += f"<li style='margin-bottom:4px;'><span style='display:inline-block;width:14px;height:14px;background:{color};margin-right:6px;border-radius:50%;'></span>{name}</li>"
# legend_html += "</ul>"
#
# legend_div = Div(text=legend_html, width=300, height=800)
#
# # 5. chord를 bokeh object로 렌더링
# bokeh_plot = hv.render(chord, backend='bokeh')
#
# # 6. 다이어그램 + 범례를 하나의 layout으로 구성
# layout = row(bokeh_plot, legend_div)
#
# # 7. 저장
# output_file("r05x_chord_with_legend.html")
# save(layout)

# import pandas as pd
# import holoviews as hv
# from holoviews import opts
# hv.extension('bokeh')
#
# from bokeh.palettes import Category20
# from bokeh.models import Div
# from bokeh.layouts import row
# from bokeh.io import output_file, save
#
# # 연관 규칙 데이터 불러오기
# df = pd.read_csv("data/atc_rule_summary.csv")
#
# # ATC 그룹 목록 추출
# atc_groups = df["ATC 그룹"].unique()
#
# # 각 ATC 그룹별로 Chord Diagram 생성
# for target_atc in atc_groups:
#     # head()를 통해서 각 그룹별 상위 몇 개 연관 규칙을 시각화할 지 설정할 것
#     sub_df = df[df["ATC 그룹"] == target_atc].sort_values(by="lift", ascending=False).head(20)
#
#     if sub_df.empty:
#         continue  # 해당 ATC 그룹에 유효한 규칙이 없는 경우 건너뜀
#
#     # 엣지/노드 구성
#     edges = []
#     nodes_set = set()
#     for _, r in sub_df.iterrows():
#         ante = r["Antecedents"].split(", ")
#         cons = r["Consequents"].split(", ")
#         for a in ante:
#             for c in cons:
#                 if a != c:
#                     edges.append((a, c, r["lift"]))
#                     nodes_set.update([a, c])
#
#     if not edges:
#         continue  # 시각화할 유의미한 연결이 없으면 건너뜀
#
#     nodes = sorted(list(nodes_set))
#     node_df = pd.DataFrame({'name': nodes})
#     edge_df = pd.DataFrame(edges, columns=["source", "target", "lift"])
#     edge_df["value"] = edge_df["lift"]  # edge 굵기용
#
#     # 색상 매핑
#     palette = Category20[20]
#     color_map = {name: palette[i % len(palette)] for i, name in enumerate(nodes)}
#
#     # Chord 생성
#     chord = hv.Chord((edge_df, hv.Dataset(node_df, 'name'))).opts(
#         opts.Chord(
#             labels=None,
#             node_color=hv.dim('name').categorize(color_map),
#             edge_color=hv.dim('source').categorize(color_map),
#             cmap='Category20',
#             edge_cmap='Category20',
#             edge_line_width=hv.dim('value') * 3,
#             edge_alpha=0.7,
#             node_size=15,
#             width=800,
#             height=800,
#             title=f"{target_atc} 주성분 Chord Diagram",
#             tools=['hover'],
#             inspection_policy='edges'
#         )
#     )
#
#     # 주성분 범례 생성
#     legend_html = f"<h3 style='font-family:sans-serif;'>{target_atc} 주성분</h3><ul style='list-style:none;padding-left:0;'>"
#     for name in nodes:
#         color = color_map[name]
#         legend_html += f"<li style='margin-bottom:4px;'><span style='display:inline-block;width:14px;height:14px;background:{color};margin-right:6px;border-radius:50%;'></span>{name}</li>"
#     legend_html += "</ul>"
#
#     legend_div = Div(text=legend_html, width=300, height=800)
#
#     # bokeh object로 변환
#     bokeh_plot = hv.render(chord, backend='bokeh')
#
#     # layout 구성
#     layout = row(bokeh_plot, legend_div)
#
#     # 생성된 chord diagram 저장(.html)
#     safe_atc = target_atc.replace("/", "_")  # 파일 이름에 문제가 없도록 변환
#     output_file(f"chord_diagrams/{safe_atc}_chord_with_legend.html")
#     save(layout)
#
#     print(f"{target_atc} 저장 완료.")

"""
연관규칙 중복을 제거하고, rule_count를 통해 몇개 규칙에서 유래했는지 표시
A → B
A, C → B
A, D → B
이라면 A → B 규칙이 3개인데, 이때 한 node에서 같은 node로 가는 edge는 1개이지만 rule_count = 3
이때, edge의 lift는 평균값
만약, edge가 2개가 나온다면 양방향 관계
A → B
B → A
"""
import pandas as pd
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

from bokeh.palettes import Category20
from bokeh.models import Div
from bokeh.layouts import row
from bokeh.io import output_file, save

# 연관 규칙 데이터 불러오기
df = pd.read_csv("data/atc_rule_summary.csv")

# ATC 그룹 목록 추출
atc_groups = df["ATC 그룹"].unique()

# 각 ATC 그룹별로 Chord Diagram 생성
for target_atc in atc_groups:
    sub_df = df[df["ATC 그룹"] == target_atc].sort_values(by="lift", ascending=False).head(5)

    if sub_df.empty:
        continue

    # 엣지 생성
    edges = []
    nodes_set = set()
    for _, r in sub_df.iterrows():
        ante = r["Antecedents"].split(", ")
        cons = r["Consequents"].split(", ")
        for a in ante:
            for c in cons:
                if a != c:
                    edges.append((a, c, r["lift"]))
                    nodes_set.update([a, c])

    if not edges:
        continue

    nodes = sorted(list(nodes_set))
    node_df = pd.DataFrame({'name': nodes})

    # DataFrame 생성 및 중복 관계 요약
    edge_df = pd.DataFrame(edges, columns=["source", "target", "lift"])
    edge_df["rule_count"] = 1
    edge_df = edge_df.groupby(["source", "target"], as_index=False).agg({
        "lift": "mean", # lift는 평균값으로 대체
        "rule_count": "sum" # 관여된 규칙 수 합산
    })
    min_lift = edge_df["lift"].min()
    max_lift = edge_df["lift"].max()
    edge_df["value"] = 1 + 5 * (edge_df["lift"] - min_lift) / (max_lift - min_lift)


    # 색상 매핑
    palette = Category20[20]
    color_map = {name: palette[i % len(palette)] for i, name in enumerate(nodes)}

    # Chord 생성
    chord = hv.Chord((edge_df, hv.Dataset(node_df, 'name'))).opts(
        opts.Chord(
            labels=None,
            node_color=hv.dim('name').categorize(color_map),
            edge_color=hv.dim('source').categorize(color_map),
            cmap='Category20',
            edge_cmap='Category20',
            edge_line_width=hv.dim('value') * 2,
            edge_alpha=0.7,
            node_size=15,
            width=800,
            height=800,
            title=f"{target_atc} 주성분 Chord Diagram",
            tools=['hover'],
            inspection_policy='edges',
            edge_hover_line_color='black',
            edge_hover_line_width=5,
            edge_hover_alpha=1.0
        )
    )

    # 주성분 범례 생성
    legend_html = f"<h3 style='font-family:sans-serif;'>{target_atc} 주성분</h3><ul style='list-style:none;padding-left:0;'>"
    for name in nodes:
        color = color_map[name]
        legend_html += f"<li style='margin-bottom:4px;'><span style='display:inline-block;width:14px;height:14px;background:{color};margin-right:6px;border-radius:50%;'></span>{name}</li>"
    legend_html += "</ul>"

    legend_div = Div(text=legend_html, width=300, height=800)

    # bokeh object로 변환
    bokeh_plot = hv.render(chord, backend='bokeh')

    # layout 구성
    layout = row(bokeh_plot, legend_div)

    # 저장
    safe_atc = target_atc.replace("/", "_")
    output_file(f"chord_diagrams/{safe_atc}_chord_with_legend.html")
    save(layout)

    print(f"{target_atc} 저장 완료.")