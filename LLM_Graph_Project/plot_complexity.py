import numpy as np
import matplotlib.pyplot as plt

# 1. 가상의 노드(V) 범위 설정 및 희소 그래프(E=10V) 가정
V = np.linspace(10, 1000, 100)
E = 10 * V  

# 2. 공간 복잡도(Space Complexity) 함수
space_traditional = V**2
space_ours = V + E

# 3. 시간 복잡도(Time Complexity) 함수
time_traditional = V**2
time_ours = E * np.log2(V)
time_optimal = E + V * np.log2(V)

# 4. 시각화 세팅 (다크 테마)
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# [그래프 1] 공간 복잡도 비교
ax1.plot(V, space_traditional, label='Traditional: Adjacency Matrix ($O(V^2)$)', color='#ff6b6b', linewidth=2)
ax1.plot(V, space_ours, label='Ours / Optimal: Adjacency List ($O(V+E)$)', color='#4ecdc4', linewidth=3, linestyle='--')
ax1.set_title('Space Complexity Comparison', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Nodes (V)', fontsize=12)
ax1.set_ylabel('Memory Requirements', fontsize=12)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

# [그래프 2] 시간 복잡도 비교
ax2.plot(V, time_traditional, label='Traditional: Array Dijkstra ($O(V^2)$)', color='#ff6b6b', linewidth=2)
ax2.plot(V, time_ours, label='Ours: Min-Heap Dijkstra ($O(E \log V)$)', color='#4ecdc4', linewidth=2)
ax2.plot(V, time_optimal, label='Theoretical Optimal: Fib-Heap ($O(E + V \log V)$)', color='#ffe66d', linewidth=2, linestyle=':')
ax2.set_title('Time Complexity Comparison', fontsize=14, fontweight='bold')
ax2.set_xlabel('Number of Nodes (V)', fontsize=12)
ax2.set_ylabel('Computational Operations', fontsize=12)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)

# 파일로 저장
plt.tight_layout()
plt.savefig('complexity_comparison.png', dpi=300)
print("✅ 보고서 첨부용 'complexity_comparison.png' 이미지가 생성되었습니다!")