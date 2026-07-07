#pragma once
#include <string>
#include <vector>

struct Edge {
    int target_index;
    std::string relation;
    float weight;
};

struct Node {
    int id;
    std::string concept_text;
    std::vector<Edge> edges;
    int degree = 0;
    float cc_score = 0.0f;

    Node(int id, std::string text) : id(id), concept_text(text) {}

    void add_edge(int target, std::string relation, float weight) {
        edges.push_back({target, relation, weight});
        degree++; // 엣지가 추가될 때마다 차수(degree) 증가
    }
};

struct PathState {
    int node_id;
    float cumulative_cost;
    int current_hop_run;
    std::string audit_trail;

    // 우선순위 큐(S-MLFQ) 정렬을 위한 비교 연산자 오버로딩 (비용이 낮을수록 우선순위 높음)
    bool operator>(const PathState& other) const {
        return cumulative_cost > other.cumulative_cost;
    }
};

// 🔥 방금 추가된 핵심 조각! (엔진의 탐색 결과를 파이썬에게 전달하기 위한 바구니)
struct SearchResult {
    std::vector<std::string> collected_concepts;
    std::vector<std::string> xai_logs;
};