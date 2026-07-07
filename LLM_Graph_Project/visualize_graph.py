import json
import networkx as nx
import matplotlib.pyplot as plt

def draw_stress_graph():
    print("🎨 지식 그래프 구조를 시각화하는 중입니다...")
    
    # 1. JSON 파일 읽어오기
    try:
        with open('graph_data.json', 'r', encoding='utf-8') as f:
            edges_data = json.load(f)
    except FileNotFoundError:
        print("❌ graph_data.json 파일이 없습니다. auto_benchmark.py를 먼저 실행해주세요.")
        return

    # 2. 방향성 그래프(DiGraph) 객체 생성
    G = nx.DiGraph()
    for edge in edges_data:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

    # 3. 그래프 노드 분류 (색상/크기 지정을 위해)
    golden_nodes = {"인공지능", "머신러닝", "딥러닝", "트랜스포머", "대형언어모델", "환각현상", "RAG기술"}
    
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node in golden_nodes:
            node_colors.append('#FFD700')  # 🟡 황금 경로 (노란색)
            node_sizes.append(2500)
        elif node == "컴퓨터일반":
            node_colors.append('#FF9999')  # 🔴 블랙홀 허브 (빨간색)
            node_sizes.append(4000)
        else:
            node_colors.append('#D3D3D3')  # ⚪ 노이즈 함정 (회색)
            node_sizes.append(1000)

    # 4. 화면 및 폰트 설정 (한글 깨짐 방지)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(14, 10))

    # 노드들이 겹치지 않게 밀어내는 레이아웃 알고리즘 적용
    pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

    # 5. 그리기
    # 엣지(선) 그리기
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, alpha=0.5)
    # 노드(동그라미) 그리기
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, edgecolors='black', linewidths=1.5)
    # 텍스트(이름) 그리기
    nx.draw_networkx_labels(G, pos, font_family='Malgun Gothic', font_size=10, font_weight='bold')

    plt.title("S-MLFQ 스트레스 테스트용 지식 그래프 위상(Topology)", fontsize=18, fontweight='bold')
    plt.axis('off')  # 축 숨기기
    
    # 6. 고화질 이미지로 저장
    plt.tight_layout()
    plt.savefig('graph_topology.png', dpi=300)
    print("🎉 'graph_topology.png' 파일이 성공적으로 저장되었습니다! 이미지를 열어보세요.")

if __name__ == "__main__":
    draw_stress_graph()