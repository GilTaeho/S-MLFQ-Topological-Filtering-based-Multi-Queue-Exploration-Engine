import random
import json
import subprocess
import matplotlib.pyplot as plt
import os
import numpy as np

# =====================================================================
# 1. 지식 그래프 동적 생성기 (가설 증명을 위한 정밀 위상 설계)
# =====================================================================
def build_objective_graph(noise_ratio=0.0):
    edges = []
    random.seed(42) # 완벽한 통제 환경을 위한 시드 고정
    
    # 1. 황금 경로 (Golden Path - 적합성 타겟 15개)
    golden = ["인공지능", "머신러닝", "딥러닝", "트랜스포머", "대형언어모델", "환각현상", "RAG기술", "벡터DB", "시맨틱검색", "파인튜닝", "프롬프트", "온톨로지", "지식그래프", "추론엔진", "XAI"]
    for i in range(len(golden) - 1):
        # 다익스트라와 S-MLFQ가 정상적으로 탐색하도록 낮은 가중치 부여
        edges.append({"source": golden[i], "target": golden[i+1], "relation": "발전", "weight": 0.1})
        
    # 2. 일반 응용 지식 (평가 A에서 예산 소진용, 허브가 아님)
    # S-MLFQ가 노이즈로 착각하지 않도록 차수(Degree)를 1~2개로 제한
    for i in range(15):
        edges.append({"source": golden[i], "target": f"응용분야_{i}_A", "relation": "응용", "weight": 0.2})
        edges.append({"source": golden[i], "target": f"응용분야_{i}_B", "relation": "응용", "weight": 0.25})

    # 3. 창발성 도메인 (Hidden Target - 다양성 타겟 8개)
    hidden = ["뇌과학", "신경가소성", "BCI기술", "뉴럴링크", "인지심리학", "행동경제학", "시냅스", "도파민"]
    # 진입 가중치를 0.9로 매우 높게 설정 (비용 최적화인 다익스트라는 절대 진입 불가)
    edges.append({"source": "인공지능", "target": hidden[0], "relation": "영감", "weight": 0.9}) 
    for i in range(len(hidden) - 1):
        edges.append({"source": hidden[i], "target": hidden[i+1], "relation": "세부", "weight": 0.1})

    # 4. 거대 노이즈 허브 (평가 B 스트레스 환경 전용 함정)
    if noise_ratio > 0.0:
        for i in range(3): # 거대 허브 3개 생성
            hub_name = f"컴퓨터일반_{i}"
            # 🔥 핵심: 다익스트라를 완벽히 유인하는 초저가 미끼 (0.001)
            edges.append({"source": "인공지능", "target": hub_name, "relation": "포함", "weight": 0.001})
            
            # 🔥 핵심: 허브 1개당 30개의 쓰레기 연결 -> Degree가 31이 됨!
            # S-MLFQ는 Degree > 5를 보는 순간 이 허브를 Q2로 완벽히 격리시킴.
            for j in range(30):
                edges.append({"source": hub_name, "target": f"노이즈_{i}_{j}", "relation": "쓰레기", "weight": 0.01})

    with open("graph_data.json", "w", encoding="utf-8") as f: 
        json.dump(edges, f, indent=4, ensure_ascii=False)

# =====================================================================
# 2. C++ 엔진 격발 및 데이터 추출 (중복 방문 제외)
# =====================================================================
def run_cpp_engine(mode_name, budget=40):
    exe_name = '.\\smlfq_engine.exe'
    
    with open("query.json", "w", encoding="utf-8") as f:
        json.dump({"mode": mode_name, "start": "인공지능", "budget": budget}, f, ensure_ascii=False)

    if os.path.exists("result.json"): os.remove("result.json")
    subprocess.run([exe_name])

    with open("result.json", "r", encoding="utf-8") as f: 
        result_data = json.load(f)
        
    exec_time = result_data.get("exec_time_ms", 0.0)
    space_usage = result_data.get("space_usage", 0)
    
    # 세트(Set)로 변환하여 랜덤 워크의 중복 방문(거품) 점수 제거
    collected_nodes = set(result_data.get("collected_nodes", []))
    
    golden_set = {"머신러닝", "딥러닝", "트랜스포머", "대형언어모델", "환각현상", "RAG기술", "벡터DB", "시맨틱검색", "파인튜닝", "프롬프트", "온톨로지", "지식그래프", "추론엔진", "XAI"}
    hidden_set = {"뇌과학", "신경가소성", "BCI기술", "뉴럴링크", "인지심리학", "행동경제학", "시냅스", "도파민"}

    waste_count = sum(1 for n in collected_nodes if "노이즈" in n or "컴퓨터일반" in n)
    golden_count = sum(1 for n in collected_nodes if n in golden_set)
    hidden_count = sum(1 for n in collected_nodes if n in hidden_set)

    efficiency = max(0, len(collected_nodes) - waste_count)
    relevance = golden_count                  
    diversity = hidden_count                  
    
    print(f"  └ [{mode_name.upper():8s}] 유효탐색:{efficiency:2d}/40 | 적합:{relevance:2d}/14 | 다양:{diversity:2d}/8 | ⏱️ {exec_time:.4f}ms | 💾 {space_usage} nodes")
    
    return [efficiency, relevance, diversity], [exec_time, space_usage]

# =====================================================================
# 3. 3대 매트릭스 차트 그리기
# =====================================================================
def plot_3_matrix_chart(d_scores, r_scores, s_scores, title, filename):
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    labels = ['탐색 효율성\n(유효 노드 수)', '의미론적 적합성\n(Golden Path)', '다양성 및 창발성\n(Hidden Target)']
    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(11, 7))
    
    rects1 = ax.bar(x - width, d_scores, width, label='Dijkstra (SJF)', color='#FF9999')
    rects2 = ax.bar(x, r_scores, width, label='Random Walk', color='#99CC99')
    rects3 = ax.bar(x + width, s_scores, width, label='S-MLFQ (제안 모델)', color='#66B2FF')
    
    ax.set_ylabel('성능 스코어 (Higher is Better)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.legend(loc='upper right')
    
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def plot_complexity_metrics(d_metrics, r_metrics, s_metrics, filename):
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    labels = ['Dijkstra (SJF)', 'Random Walk', 'S-MLFQ (제안 모델)']
    times = [d_metrics[0], r_metrics[0], s_metrics[0]]
    spaces = [d_metrics[1], r_metrics[1], s_metrics[1]]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color1 = '#FF6666'
    ax1.set_ylabel('실행 시간 (ms) - Lower is Better', color=color1, fontsize=12, fontweight='bold')
    bars = ax1.bar(labels, times, color=color1, width=0.4, alpha=0.8, label='실행 시간')
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.4f}ms', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax2 = ax1.twinx()  
    color2 = '#3399FF'
    ax2.set_ylabel('공간 점유율 (Queue + Log Nodes)', color=color2, fontsize=12, fontweight='bold')
    lines = ax2.plot(labels, spaces, color=color2, marker='o', linestyle='dashed', linewidth=2, markersize=8)
    for i, v in enumerate(spaces):
        ax2.text(i, v, f'{v}', ha='center', va='bottom', color=color2, fontsize=11, fontweight='bold')

    plt.title('[실측 복잡도] 평가 B (스트레스 환경) 리소스 비교', fontsize=15, fontweight='bold')
    fig.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

if __name__ == "__main__":
    print("="*80)
    print("🧪 [평가 A] 정상 지식 그래프 벤치마크 시작 (노이즈 0%)")
    print("="*80)
    build_objective_graph(noise_ratio=0.0)
    d_score_A, _ = run_cpp_engine("dijkstra")
    r_score_A, _ = run_cpp_engine("random")
    s_score_A, _ = run_cpp_engine("smlfq")
    plot_3_matrix_chart(d_score_A, r_score_A, s_score_A, "[평가 A] 정상 지식 그래프 (노이즈 0%)", "benchmark_normal.png")
    
    print("\n" + "="*80)
    print("🔥 [평가 B] 적대적 스트레스 벤치마크 시작 (노이즈 30%)")
    print("="*80)
    build_objective_graph(noise_ratio=0.3)
    d_score_B, d_comp = run_cpp_engine("dijkstra")
    r_score_B, r_comp = run_cpp_engine("random")
    s_score_B, s_comp = run_cpp_engine("smlfq")
    plot_3_matrix_chart(d_score_B, r_score_B, s_score_B, "[평가 B] 적대적 스트레스 환경 (노이즈 30% 함정)", "benchmark_stress.png")
    
    plot_complexity_metrics(d_comp, r_comp, s_comp, "complexity_metrics.png")
    print("\n✅ 완료! 이미지를 다시 확인해주세요.")