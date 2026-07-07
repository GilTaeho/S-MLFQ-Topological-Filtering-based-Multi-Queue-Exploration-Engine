import json
import random
import time
import subprocess
import matplotlib.pyplot as plt

def generate_dummy_graph(num_nodes):
    """지정된 노드 개수(V)에 맞춰 랜덤 지식 그래프(JSON)를 물리적으로 생성하는 함수"""
    edges = []
    num_edges = num_nodes * 5  # 노드당 평균 5개의 관계를 가지는 희소 그래프
    
    # 노드 이름 리스트 생성 (예: node_1, node_2 ...)
    nodes = [f"concept_{i}" for i in range(num_nodes)]
    
    for _ in range(num_edges):
        source = random.choice(nodes)
        target = random.choice(nodes)
        if source != target:
            edges.append({
                "source": source,
                "target": target,
                "relation": "random_link",
                "weight": round(random.uniform(0.1, 1.0), 2)
            })
            
    # C++ 엔진이 읽을 수 있도록 파일 덮어쓰기
    with open("graph_data.json", "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=4)
        
    return nodes

def run_real_benchmark():
    print("🔥 [하드웨어 스트레스 테스트] 리얼 벤치마크 가동을 시작합니다...")
    
    # 테스트할 데이터 스케일 (노드 100개부터 5,000개까지)
    v_sizes = [100, 500, 1000, 2500, 5000]
    actual_times_ms = []
    
    for V in v_sizes:
        print(f"\n⚙️ [Step {V} 노드] 더미 지식 그래프 생성 중...")
        nodes_list = generate_dummy_graph(V)
        
        # 신뢰도를 높이기 위해 각 스케일마다 3번씩 측정하여 평균을 냅니다.
        trial_times = []
        for _ in range(3):
            source = random.choice(nodes_list)
            target = random.choice(nodes_list)
            
            # ⏱️ [타이머 시작]
            start_time = time.perf_counter()
            
            try:
                # C++ 바이너리 강제 호출 및 결과 대기
                subprocess.run(
                    ['./cli_chatbot.exe'], 
                    input=f"{source}\n{target}\nexit\n", 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    timeout=10 # 10초 넘어가면 에러 처리
                )
            except Exception as e:
                print(f"   ❌ C++ 실행 오류: {e}")
                
            # ⏱️ [타이머 종료]
            end_time = time.perf_counter()
            trial_times.append((end_time - start_time) * 1000) # ms로 변환
            
        # 3번의 평균 시간 기록
        avg_time = sum(trial_times) / len(trial_times)
        actual_times_ms.append(avg_time)
        print(f"   ✅ 측정 완료! 평균 소요 시간: {avg_time:.2f} ms")

    print("\n📊 측정이 완료되었습니다. 결과를 그래프로 렌더링합니다...")

    # --- matplotlib 시각화 ---
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    
    # 실제 측정된 우리 C++ 엔진의 소요 시간 라인
    plt.plot(v_sizes, actual_times_ms, marker='o', markersize=8, color='#deff9a', linewidth=3, label='Real C++ Engine Time (Measured)')
    
    # 그래프 꾸미기
    plt.title('Real Hardware Empirical Benchmark (Min-Heap Dijkstra)', fontsize=15, fontweight='bold', color='white')
    plt.xlabel('Number of Entities (Vertices)', fontsize=12)
    plt.ylabel('Average Total Latency (ms)', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11)
    
    # 데이터 라벨 달기
    for i, txt in enumerate(actual_times_ms):
        plt.annotate(f"{txt:.1f}ms", (v_sizes[i], actual_times_ms[i]), textcoords="offset points", xytext=(0,10), ha='center', color='#deff9a')

    # 파일 저장
    file_name = "real_empirical_result.png"
    plt.tight_layout()
    plt.savefig(file_name, dpi=300)
    print(f"🎯 완벽합니다! 실제 하드웨어 측정 그래프 '{file_name}'이(가) 저장되었습니다.")

if __name__ == "__main__":
    run_real_benchmark()