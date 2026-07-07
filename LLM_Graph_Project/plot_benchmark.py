import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# 1. C++가 생성한 CSV 파일 읽기 (자동화의 핵심)
dijkstra_data = []
smlfq_data = []

csv_file = 'benchmark_results.csv'
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} 파일이 없습니다. C++ 엔진을 먼저 실행하세요!")
    exit(1)

with open(csv_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = [float(row['Steps']), float(row['Relevance']), float(row['Diversity'])]
        if row['Algorithm'] == 'Dijkstra':
            dijkstra_data = data
        elif row['Algorithm'] == 'S-MLFQ':
            smlfq_data = data

# 2. 깔끔한 논문용 영문 스타일
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'

color_baseline = '#B0BEC5' 
color_proposed = '#2962FF'

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.suptitle('Graph Search Algorithm Performance (Dynamic CSV Load)', fontsize=16, fontweight='bold', y=0.98)

x = np.arange(1)
width = 0.35

# --- [그래프 1] 탐색 효율성 ---
ax1 = axes[0]
ax1.bar(x - width/2, dijkstra_data[0], width, label='Dijkstra (Baseline)', color=color_baseline)
ax1.bar(x + width/2, smlfq_data[0], width, label='S-MLFQ (Proposed)', color=color_proposed)
ax1.set_title('Search Efficiency', fontsize=13)
ax1.set_ylabel('Steps', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(['Efficiency'])
ax1.set_ylim(0, max(dijkstra_data[0], smlfq_data[0]) * 1.2)
ax1.text(x[0] - width/2, dijkstra_data[0] + 5, f'{int(dijkstra_data[0])}', ha='center', fontweight='bold')
ax1.text(x[0] + width/2, smlfq_data[0] + 5, f'{int(smlfq_data[0])}', ha='center', fontweight='bold')

# --- [그래프 2] 의미론적 적합성 ---
ax2 = axes[1]
ax2.bar(x - width/2, dijkstra_data[1], width, color=color_baseline)
ax2.bar(x + width/2, smlfq_data[1], width, color=color_proposed)
ax2.set_title('Semantic Relevance', fontsize=13)
ax2.set_ylabel('Target Class Ratio (%)', fontsize=12)
ax2.set_xticks(x)
ax2.set_xticklabels(['Relevance'])
ax2.set_ylim(0, 100)
ax2.text(x[0] - width/2, dijkstra_data[1] + 2, f'{dijkstra_data[1]:.1f}%', ha='center', fontweight='bold')
ax2.text(x[0] + width/2, smlfq_data[1] + 2, f'{smlfq_data[1]:.1f}%', ha='center', color=color_proposed, fontweight='bold')

# --- [그래프 3] 탐색 다양성 ---
ax3 = axes[2]
ax3.bar(x - width/2, dijkstra_data[2], width, color=color_baseline)
ax3.bar(x + width/2, smlfq_data[2], width, color=color_proposed)
ax3.set_title('Search Diversity', fontsize=13)
ax3.set_ylabel('Unique Domains Explored', fontsize=12)
ax3.set_xticks(x)
ax3.set_xticklabels(['Diversity'])
ax3.set_ylim(0, max(dijkstra_data[2], smlfq_data[2]) + 2)
ax3.text(x[0] - width/2, dijkstra_data[2] + 0.2, f'{int(dijkstra_data[2])}', ha='center', color='red', fontweight='bold')
ax3.text(x[0] + width/2, smlfq_data[2] + 0.2, f'{int(smlfq_data[2])}', ha='center', color=color_proposed, fontweight='bold')

fig.legend(loc='upper right', bbox_to_anchor=(0.95, 0.95), fontsize=11)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('benchmark_result_dynamic.png', dpi=300, bbox_inches='tight')
print("✅ C++ CSV 데이터를 기반으로 benchmark_result_dynamic.png 렌더링 완료!")
plt.show()