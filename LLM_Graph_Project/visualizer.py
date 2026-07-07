import json
from pyvis.network import Network
import networkx as nx
import os

def visualize_graph(json_file_path):
    print(f"🔍 '{json_file_path}' 데이터를 읽어오는 중...")
    
    if not os.path.exists(json_file_path):
        print(f"❌ 오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    G = nx.DiGraph()

    # 1. 노드별 맞춤형 디자인 (크기 및 색상 팔레트)
    node_styles = {
        "LLM": {"color": "#E50914", "size": 45}, # 핵심 노드는 크고 강렬하게
        "Transformer": {"color": "#E5A909", "size": 35},
        "Attention Mechanism": {"color": "#09E537", "size": 30},
        "Hallucination": {"color": "#8009E5", "size": 35},
        "RAG": {"color": "#0980E5", "size": 30}
    }

    # 2. 데이터 주입 및 가중치 시각화 최적화
    for edge in graph_data:
        source = edge["source"]
        target = edge["target"]
        relation = edge["relation"]
        weight = edge["weight"]

        # 노드가 그래프에 없으면 스타일을 적용하여 추가
        for node_name in [source, target]:
            if not G.has_node(node_name):
                style = node_styles.get(node_name, {"color": "#97C2FC", "size": 25})
                G.add_node(node_name, size=style["size"], color=style["color"], title=node_name)

        # 간선 추가 (선의 두께는 적절히 얇게, 텍스트 라벨 추가)
        G.add_edge(source, target, title=f"가중치: {weight}", value=weight * 3, label=relation)

    print("🎨 프리미엄 HTML UI 렌더링 중...")
    
    # 3. 고급 네트워크 객체 생성 (다크 테마 및 선택 메뉴 활성화)
    net = Network(height="800px", width="100%", bgcolor="#1a1a1a", font_color="#ffffff", directed=True, select_menu=True)
    net.from_nx(G)

    # 4. 자바스크립트 물리 엔진 & 렌더링 미세 조정 (핵심!)
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 22,
          "face": "Tahoma",
          "bold": true
        },
        "borderWidth": 2,
        "borderWidthSelected": 6,
        "shadow": {"enabled": true, "color": "rgba(0,0,0,0.5)", "size": 10}
      },
      "edges": {
        "color": {
          "inherit": false,
          "color": "#666666",
          "highlight": "#ffffff"
        },
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.2
        },
        "font": {
          "size": 14,
          "color": "#aaaaaa",
          "strokeWidth": 0,
          "align": "middle"
        },
        "arrows": {
          "to": {"scaleFactor": 0.8}
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -40000,
          "centralGravity": 0.1,
          "springLength": 300,
          "springConstant": 0.04
        },
        "minVelocity": 0.75
      }
    }
    """)

    output_filename = "graph_visualization.html"
    net.save_graph(output_filename)
    
    print(f"✅ 프리미엄 시각화 완료! '{output_filename}'을 다시 열어보세요.")

if __name__ == "__main__":
    visualize_graph("graph_data.json")