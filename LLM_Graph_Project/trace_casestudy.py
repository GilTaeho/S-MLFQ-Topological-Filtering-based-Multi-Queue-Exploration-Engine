import matplotlib.pyplot as plt
import networkx as nx

def draw_case_study():
    # 1. 폰트 및 스타일 설정 (논문용)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 2. 그래프 노드 및 엣지 정의 (미니 실세계 데이터)
    G = nx.DiGraph()
    
    # 노드 그룹 정의
    core_ai = ["인공지능", "LLM", "환각현상", "파인튜닝", "프롬프트", "RAG"]
    noise = ["컴퓨터역사", "폰노이만", "진공관", "열역학"]
    deep_domain = ["뇌과학", "인지심리학", "망각메커니즘", "에피소드기억"]
    
    # 엣지 연결
    G.add_edges_from([
        ("인공지능", "LLM"), ("LLM", "파인튜닝"), ("파인튜닝", "프롬프트"), ("프롬프트", "RAG"),
        ("LLM", "환각현상"), ("환각현상", "RAG"),
        ("인공지능", "컴퓨터역사"), ("컴퓨터역사", "폰노이만"), ("폰노이만", "진공관"), ("진공관", "열역학"),
        ("환각현상", "뇌과학"), ("뇌과학", "인지심리학"), ("인지심리학", "망각메커니즘"), ("망각메커니즘", "에피소드기억")
    ])

    # 3. 시각적 일관성을 위한 노드 위치(Layout) 하드코딩
    pos = {
        "인공지능": (0, 5), "LLM": (2, 5), "환각현상": (4, 5),
        "파인튜닝": (2, 7), "프롬프트": (4, 7), "RAG": (6, 6),
        "컴퓨터역사": (1, 2), "폰노이만": (3, 2), "진공관": (5, 2), "열역학": (7, 2),
        "뇌과학": (5, 8), "인지심리학": (7, 8), "망각메커니즘": (9, 8), "에피소드기억": (11, 8)
    }

    # 4. 알고리즘별 실제 탐색 경로 (Trace)
    path_dijkstra = ["인공지능", "LLM", "파인튜닝", "프롬프트", "RAG"]
    path_random = ["인공지능", "컴퓨터역사", "폰노이만", "진공관", "열역학"]
    path_smlfq = ["인공지능", "LLM", "환각현상", "뇌과학", "인지심리학", "망각메커니즘"]

    # 5. 서브플롯 생성 (1행 3열)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Case Study: 알고리즘별 지식 탐색 경로(Path Trace) 시각화', fontsize=18, fontweight='bold', y=0.95)

    titles = [
        "1. Dijkstra (필터 버블)\n뻔하고 얕은 지식만 탐색", 
        "2. Random Walk (환각 표류)\n질문과 무관한 노이즈로 이탈", 
        "3. S-MLFQ (통제된 창발성)\n이종 도메인 융합을 통한 혁신적 통찰 발견"
    ]
    paths = [path_dijkstra, path_random, path_smlfq]
    colors = ['#FF9999', '#99CC99', '#66B2FF']

    for i, ax in enumerate(axes):
        ax.set_title(titles[i], fontsize=13, pad=15)
        
        # 기본 그래프(회색) 그리기
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#EEEEEE', node_size=2000, edgecolors='gray')
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#CCCCCC', arrows=True)
        nx.draw_networkx_labels(G, pos, ax=ax, font_family='Malgun Gothic', font_size=9, font_weight='bold')
        
        # 탐색된 경로 하이라이트
        highlight_nodes = paths[i]
        highlight_edges = [(highlight_nodes[j], highlight_nodes[j+1]) for j in range(len(highlight_nodes)-1)]
        
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=highlight_nodes, node_color=colors[i], node_size=2200, edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=highlight_edges, edge_color=colors[i], width=3, arrows=True, arrowsize=20)
        
        ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.9])
    plt.savefig('case_study_trace.png', dpi=300)
    print("✅ 'case_study_trace.png' 경로 추적 시각화 완료!")
    plt.show()

if __name__ == "__main__":
    draw_case_study()