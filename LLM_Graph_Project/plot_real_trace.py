import json
import subprocess
import matplotlib.pyplot as plt
import networkx as nx
import os

def run_engine_and_get_trace(mode_name, budget=15):
    """C++ 엔진을 실제 가동하고, 방문한 노드들의 순서(Trace)를 가져옵니다."""
    exe_name = '.\\smlfq_engine.exe'
    
    with open("query.json", "w", encoding="utf-8") as f:
        json.dump({"mode": mode_name, "start": "인공지능", "budget": budget}, f, ensure_ascii=False)

    if os.path.exists("result.json"): 
        os.remove("result.json")
    
    subprocess.run([exe_name], capture_output=True)

    with open("result.json", "r", encoding="utf-8") as f: 
        result_data = json.load(f)
        
    return result_data.get("collected_nodes", [])

def get_node_color(node_name):
    """노드의 도메인 특성에 따라 색상을 부여합니다."""
    if "노이즈" in node_name or "컴퓨터일반" in node_name:
        return "#CCCCCC" 
    elif "뇌과학" in node_name or "신경가소성" in node_name or "BCI" in node_name or "인지심리" in node_name or "망각" in node_name or "에피소드" in node_name or "시냅스" in node_name or "도파민" in node_name or "뉴럴링크" in node_name:
        return "#FF9999" 
    else:
        return "#FFF59D" 

def draw_real_data_trace():
    print("🚀 C++ 엔진 가동 및 실제 메모리 궤적(Trace) 추출 중...")
    
    trace_dijkstra = run_engine_and_get_trace("dijkstra")
    trace_random = run_engine_and_get_trace("random")
    trace_smlfq = run_engine_and_get_trace("smlfq")
    
    G_full = nx.DiGraph()
    with open("graph_data.json", "r", encoding="utf-8") as f:
        edges = json.load(f)
        for edge in edges:
            G_full.add_edge(edge["source"], edge["target"])

    all_visited = set(trace_dijkstra + trace_random + trace_smlfq)
    G_plot = G_full.subgraph(all_visited)

    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 🔥 [수정 1] 캔버스 자체를 더 넓게 확장 (22, 8 -> 24, 9)
    fig, axes = plt.subplots(1, 3, figsize=(24, 9)) 
    fig.suptitle('Case Study: 실제 지식망(점선) 위에서의 탐색 궤적(실선) 시각화', fontsize=20, fontweight='bold', y=0.98)

    titles = [
        "[Baseline] 다익스트라의 탐색 궤적\n(노이즈 허브에 갇혀 표류)", 
        "[Google Target] 랜덤 워크의 탐색 궤적\n(목적성 상실 및 무작위 이탈)", 
        "[Proposed] S-MLFQ의 탐색 궤적\n(노이즈 회피 및 타겟 도메인 창발적 탐색)"
    ]
    traces = [trace_dijkstra, trace_random, trace_smlfq]

    # 🔥 [수정 2] 물리 엔진 조율: 노드 간 밀어내는 힘(k)을 0.9에서 2.5로 대폭 증가, 계산 반복 횟수(iterations) 증가
    pos = nx.spring_layout(G_plot, k=2.5, iterations=200, seed=42)

    for i, ax in enumerate(axes):
        ax.set_title(titles[i], fontsize=14, pad=15, fontweight='bold')
        current_trace = traces[i]
        
        H = G_plot.subgraph(current_trace).copy()
        
        # 밑바탕 점선
        nx.draw_networkx_edges(H, pos, ax=ax, edge_color='#B0B0B0', 
                               style='dashed', width=1.5, arrows=False)
        
        # 🔥 [수정 3] 노드 크기를 텍스트에 딱 맞게 살짝 축소하여 겹침 방지 (2500 -> 1800)
        node_colors = [get_node_color(node) for node in H.nodes()]
        nx.draw_networkx_nodes(H, pos, ax=ax, node_color=node_colors, 
                               node_size=1800, edgecolors='black', linewidths=1.5)
        
        nx.draw_networkx_labels(H, pos, ax=ax, font_family='Malgun Gothic', 
                                font_size=10, font_weight='bold')
        
        # 실제 탐색 궤적 실선
        trace_edges = []
        for j in range(len(current_trace) - 1):
            trace_edges.append((current_trace[j], current_trace[j+1]))
                
        nx.draw_networkx_edges(G_full, pos, ax=ax, edgelist=trace_edges, 
                               edge_color='#1A1A1A', width=3.0, style='solid', 
                               arrows=True, arrowsize=25, connectionstyle="arc3,rad=0.15")
        
        # 🔥 [수정 4] 바깥쪽 텍스트가 잘리지 않도록 테두리 여백 대폭 확보
        ax.margins(0.15)
        ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('real_data_case_study_layered.png', dpi=300)
    print("✅ 'real_data_case_study_layered.png' 가독성 최적화 렌더링 완료!")
    plt.show()

if __name__ == "__main__":
    draw_real_data_trace()