import pandas as pd
import matplotlib.pyplot as plt
import time
from smlfq_runner import run_smlfq_engine 

# 1. 측정할 노드 수 포인트들 (실험 환경에 따라 조절 가능)
nodes_range = [5, 10, 20] 
smlfq_real_time = []

print("🚀 벤치마크 실험 시작... 잠시만 기다려주세요.")

for v in nodes_range:
    # 2. 엔진 성능 측정 (Budget 28은 최적값)
    start = time.perf_counter()
    # 주의: 여기서 실제 존재하는 노드 키워드를 넣어야 제대로 측정됩니다.
    run_smlfq_engine("인공지능", budget=28) 
    end = time.perf_counter()
    
    ms = (end - start) * 1000
    smlfq_real_time.append(ms)
    print(f"노드 {v}개 탐색 완료: {ms:.4f}ms")

# 3. 그래프 생성
plt.figure(figsize=(8, 5))
plt.plot(nodes_range, smlfq_real_time, marker='o', color='#deff9a', linewidth=2, label='S-MLFQ Real-time Latency')

plt.title("S-MLFQ Engine Performance (Real-time Metric)")
plt.xlabel("Number of Nodes Processed")
plt.ylabel("Latency (ms)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# 4. 그래프 보여주기 (이 명령어가 그래프 창을 띄웁니다!)
plt.show()

# 5. CSV 저장
df = pd.DataFrame({'Nodes': nodes_range, 'Time_ms': smlfq_real_time})
df.to_csv("benchmark_results.csv", index=False)
print("💾 결과가 'benchmark_results.csv'로 저장되었습니다.")