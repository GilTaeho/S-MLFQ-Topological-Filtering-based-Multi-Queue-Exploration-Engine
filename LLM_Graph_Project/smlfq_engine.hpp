#pragma once
#include "graph_models.hpp"
#include <queue>
#include <iostream>
#include <unordered_set>
#include <string>
#include <vector>
#include <functional>
#include <random>

class SemanticMlfqEngine {
private:
    static const int NUM_QUEUES = 3;
    std::priority_queue<PathState, std::vector<PathState>, std::greater<PathState>> mlfq[NUM_QUEUES];
    const int HOP_QUANTUM = 2;         
    const int HUB_THRESHOLD = 5;       
    const float CC_DRIFT_LIMIT = 0.0f; 
    const int AGING_INTERVAL = 10;     
    std::vector<Node>* graph_nodes;

public:
    SemanticMlfqEngine(std::vector<Node>& nodes) { graph_nodes = &nodes; }

    // [1] S-MLFQ 알고리즘 (우리의 제안: MLFQ 대응)
    SearchResult Search(int start_id, int search_budget) {
        SearchResult result;
        std::unordered_set<int> visited;
        int global_tick = 0;
        std::string start_name = (*graph_nodes)[start_id].concept_text;
        mlfq[0].push({start_id, 0.0f, 0, start_name});
        result.xai_logs.push_back("[시작] S-MLFQ 탐색");

        while (HasElements() && search_budget > 0) {
            global_tick++;
            if (global_tick % AGING_INTERVAL == 0) ApplyAging(result.xai_logs);

            int active_idx = GetHighestPriorityQueueIndex();
            PathState current = mlfq[active_idx].top();
            mlfq[active_idx].pop();

            if (visited.find(current.node_id) != visited.end()) continue;
            visited.insert(current.node_id);
            result.collected_concepts.push_back((*graph_nodes)[current.node_id].concept_text);
            search_budget--;
            result.xai_logs.push_back("[수집] " + (*graph_nodes)[current.node_id].concept_text);

            for (const auto& edge : (*graph_nodes)[current.node_id].edges) {
                int next_id = edge.target_index;
                if (visited.find(next_id) != visited.end()) continue;
                int next_hop_run = current.current_hop_run + 1;
                int next_queue_idx = active_idx;
                if ((*graph_nodes)[next_id].degree > HUB_THRESHOLD) { next_queue_idx = 2; next_hop_run = 0; }
                else if (active_idx == 0 && next_hop_run >= HOP_QUANTUM) { next_queue_idx = 1; next_hop_run = 0; }
                mlfq[next_queue_idx].push({next_id, current.cumulative_cost + edge.weight, next_hop_run, ""});
            }
        }
        return result;
    }

    // [2] 다익스트라 알고리즘 (기존 방식: SJF 대응)
    SearchResult SearchDijkstra(int start_id, int search_budget) {
        SearchResult result;
        std::unordered_set<int> visited;
        std::priority_queue<PathState, std::vector<PathState>, std::greater<PathState>> pq;
        pq.push({start_id, 0.0f, 0, ""});
        result.xai_logs.push_back("[시작] 다익스트라(SJF) 탐색");

        while (!pq.empty() && search_budget > 0) {
            PathState current = pq.top(); pq.pop();
            if (visited.find(current.node_id) != visited.end()) continue;
            visited.insert(current.node_id);
            result.collected_concepts.push_back((*graph_nodes)[current.node_id].concept_text);
            search_budget--;
            result.xai_logs.push_back("[수집] " + (*graph_nodes)[current.node_id].concept_text);
            for (const auto& edge : (*graph_nodes)[current.node_id].edges) {
                if (visited.find(edge.target_index) == visited.end()) {
                    pq.push({edge.target_index, current.cumulative_cost + edge.weight, 0, ""});
                }
            }
        }
        return result;
    }

// [3] 랜덤 워크 (Lottery 스케줄링 + 진짜 난수 + Damping Factor)
    SearchResult SearchRandomWalk(int start_id, int search_budget) {
        SearchResult result;
        std::unordered_set<int> visited;
        
        // 🔥 시드 42 고정 해제! 매번 결과가 바뀌는 진짜 난수를 가져옵니다.
        std::random_device rd; 
        std::mt19937 rng(rd()); 
        std::uniform_real_distribution<float> prob(0.0, 1.0); 

        int current_id = start_id;
        result.xai_logs.push_back("[시작] 랜덤 워크(Lottery) 탐색");

        int max_steps = 1000; 
        while (search_budget > 0 && max_steps > 0) {
            max_steps--;
            if (visited.find(current_id) == visited.end()) {
                visited.insert(current_id);
                result.collected_concepts.push_back((*graph_nodes)[current_id].concept_text);
                result.xai_logs.push_back("[수집] " + (*graph_nodes)[current_id].concept_text);
                search_budget--;
            }

            auto& edges = (*graph_nodes)[current_id].edges;
            
            // 구글 페이지랭크의 15% 순간이동(Context Switch) 적용
            if (edges.empty() || prob(rng) < 0.15f) {
                current_id = start_id; 
                continue; 
            }
            
            std::uniform_int_distribution<int> dist(0, edges.size() - 1);
            current_id = edges[dist(rng)].target_index;
        }
        return result;
    }

private:
    bool HasElements() { return !mlfq[0].empty() || !mlfq[1].empty() || !mlfq[2].empty(); }
    int GetHighestPriorityQueueIndex() {
        for (int i = 0; i < NUM_QUEUES; ++i) if (!mlfq[i].empty()) return i; return -1;
    }
    void ApplyAging(std::vector<std::string>& logs) {
        std::vector<PathState> temp_q1; while(!mlfq[1].empty()) { temp_q1.push_back(mlfq[1].top()); mlfq[1].pop(); }
        for(auto& state : temp_q1) { state.current_hop_run = 0; mlfq[0].push(state); }
        std::vector<PathState> temp_q2; while(!mlfq[2].empty()) { temp_q2.push_back(mlfq[2].top()); mlfq[2].pop(); }
        for(auto& state : temp_q2) { state.current_hop_run = 0; mlfq[1].push(state); }
    }
};