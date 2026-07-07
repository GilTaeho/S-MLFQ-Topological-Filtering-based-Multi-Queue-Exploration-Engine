import torch
import numpy as np
from torch_geometric.datasets import Planetoid
from sklearn.decomposition import PCA
import os

def main():
    print("[1/5] Loading Cora dataset...")
    # 처음 실행 시 자동으로 데이터를 다운로드합니다.
    dataset = Planetoid(root='./data', name='Cora')
    data = dataset[0]

    # features: [2708, 1433] 크기의 노드 특성 벡터 (논문에 쓰인 단어 유무)
    # labels: [2708] 크기의 정답 클래스 (0~6, 연구 분야)
    # edge_index: [2, 10556] 크기의 간선 리스트
    features = data.x.numpy()
    labels = data.y.numpy()
    edge_index = data.edge_index.numpy()
    num_nodes = features.shape[0]

    print(f"[2/5] Reducing dimensions (1433 -> 64) via PCA...")
    pca = PCA(n_components=64, random_state=42)
    features_64 = pca.fit_transform(features)

    print("[3/5] Quantizing to 64-bit Semantic Signatures...")
    # 각 차원별 중앙값을 기준으로 0 또는 1 할당 (해싱)
    medians = np.median(features_64, axis=0)
    binary_features = (features_64 > medians).astype(np.uint64)

    # 64개의 비트를 하나의 64비트 정수(uint64)로 패킹
    semantic_signatures = np.zeros(num_nodes, dtype=np.uint64)
    for i in range(64):
        semantic_signatures |= (binary_features[:, i] << i)

    print("[4/5] Exporting nodes.txt...")
    # 포맷: [노드ID] [정답클래스] [64비트_서명]
    with open('nodes.txt', 'w') as f:
        for i in range(num_nodes):
            f.write(f"{i} {labels[i]} {semantic_signatures[i]}\n")

    print("[5/5] Exporting edges.txt...")
    # 포맷: [출발노드ID] [도착노드ID]
    with open('edges.txt', 'w') as f:
        for i in range(edge_index.shape[1]):
            src = edge_index[0, i]
            dst = edge_index[1, i]
            f.write(f"{src} {dst}\n")

    print("✅ Pipeline complete! 'nodes.txt' and 'edges.txt' are ready for the C++ engine.")

if __name__ == "__main__":
    main()