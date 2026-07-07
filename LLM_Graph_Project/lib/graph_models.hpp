#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>

// 1. 간선(Edge) 구조체
struct Edge {
    int target_index;       
    std::string relation;   
    float weight;           
};

// 2. 노드(Node) 메타데이터 구조체 (S-MLFQ용 메타데이터 추가)
class Node {
public:
    int id;                                 
    std::string concept_text;               
    std::vector<Edge> edges;                
    
    // [추가] S-MLFQ 강등 판단용 메타데이터
    int degree = 0; 
    float cc_score = 0.0f; // 군집 계수 (Clustering Coefficient)

    Node(int node_id, std::string text) : id(node_id), concept_text(text) {}

    void add_edge(int target_id, std::string rel, float w) {
        edges.push_back({target_id, rel, w});
        degree = edges.size(); // 간선이 추가될 때마다 차수 업데이트
    }
};

// 3. 탐색 상태(Path State) 구조체
struct PathState {
    int node_id;
    float cumulative_cost;
    int current_hop_run;      // 현재 큐 연속 홉 수 (Time Quantum)
    std::string audit_trail;  // XAI용 추론 기록

    // Min-Heap을 위한 연산자 오버로딩 (비용이 작을수록 우선순위 높음)
    bool operator>(const PathState& other) const {
        return cumulative_cost > other.cumulative_cost;
    }
};

// 4. 최종 반환용 구조체
struct SearchResult {
    std::vector<std::string> collected_concepts; // 수집된 지식 노드 텍스트들
    std::vector<std::string> xai_logs;           // XAI 추론 로그
};