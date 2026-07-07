#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <chrono>

// 1. 노드 메타데이터 구조체 (총 12바이트로 캐시 라인에 쏙 들어감)
struct CoraNode {
    uint32_t id;
    uint8_t ground_truth_class;  // 0~6: 채점용 정답지
    uint64_t semantic_signature; // 64비트 양자화 서명
};

class CsrGraph {
public:
    std::vector<CoraNode> nodes;
    
    // CSR 포맷의 핵심 배열 2개
    std::vector<uint32_t> row_ptr; 
    std::vector<uint32_t> col_ind; 

    bool LoadFromFiles(const std::string& nodes_file, const std::string& edges_file, uint32_t num_nodes) {
        auto start_time = std::chrono::high_resolution_clock::now();

        // 메모리 초기화
        nodes.resize(num_nodes);
        row_ptr.assign(num_nodes + 1, 0);

        // ---------------------------------------------------------
        // Step A: 노드 메타데이터 파싱 (nodes.txt)
        // ---------------------------------------------------------
        std::ifstream nf(nodes_file);
        if (!nf.is_open()) {
            std::cerr << "Error: Cannot open " << nodes_file << "\n";
            return false;
        }

        uint32_t id;
        int gt_class;
        uint64_t signature;
        while (nf >> id >> gt_class >> signature) {
            nodes[id] = { id, static_cast<uint8_t>(gt_class), signature };
        }
        nf.close();

        // ---------------------------------------------------------
        // Step B: 임시 인접 리스트로 간선 수집 (edges.txt)
        // ---------------------------------------------------------
        // 파일을 한 번만 읽어 CSR로 바로 변환하기 위해 임시 버퍼 사용
        std::vector<std::vector<uint32_t>> temp_adj(num_nodes);
        std::ifstream ef(edges_file);
        if (!ef.is_open()) {
            std::cerr << "Error: Cannot open " << edges_file << "\n";
            return false;
        }

        uint32_t src, dst;
        uint32_t num_edges = 0;
        while (ef >> src >> dst) {
            temp_adj[src].push_back(dst);
            num_edges++;
        }
        ef.close();

        // ---------------------------------------------------------
        // Step C: 완전 평탄화 (Flattening to CSR)
        // ---------------------------------------------------------
        col_ind.reserve(num_edges); // 재할당 방지
        for (uint32_t i = 0; i < num_nodes; ++i) {
            row_ptr[i] = static_cast<uint32_t>(col_ind.size()); // 현재 노드의 간선 시작 인덱스 기록
            
            for (uint32_t neighbor : temp_adj[i]) {
                col_ind.push_back(neighbor);
            }
        }
        // 마지막 인덱스 닫기 (탐색 루프 계산을 위함)
        row_ptr[num_nodes] = static_cast<uint32_t>(col_ind.size());

        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> ms_double = end_time - start_time;

        std::cout << "[Graph Loaded] Nodes: " << num_nodes 
                  << " | Edges: " << num_edges 
                  << " | Time: " << ms_double.count() << " ms\n";
        
        return true;
    }

    // 💡 핵심: 특정 노드의 이웃을 순회하는 CSR 인터페이스
    // 포인터 점프 없이 col_ind 배열의 연속된 메모리를 긁어옴
    void PrintNeighbors(uint32_t node_id) {
        uint32_t start_idx = row_ptr[node_id];
        uint32_t end_idx = row_ptr[node_id + 1];

        std::cout << "Node " << node_id << "'s neighbors: ";
        for (uint32_t i = start_idx; i < end_idx; ++i) {
            std::cout << col_ind[i] << " ";
        }
        std::cout << "\n";
    }
};

#include <queue>
#include <unordered_set>
#include <bitset>
#include <map>

// 탐색 상태 구조체 (큐에 저장될 객체)
struct PathState {
    uint32_t node_id;
    float cost;
    uint32_t hop_run;

    bool operator<(const PathState& other) const {
        return cost > other.cost; // 최소 힙 (Cost가 작은 것이 Top)
    }
};

// 벤치마크 결과를 담을 구조체
struct BenchmarkResult {
    uint32_t visited_nodes;       // 효율성 (작을수록 좋음)
    float relevance_score;        // 적합성 (정답 클래스 비율)
    uint32_t diversity_score;     // 창발성 (탐색된 고유 클래스 개수)
};

class SemanticEngine {
private:
    CsrGraph* graph;
    
    // 💡 [수정된 파라미터 셋팅]
    const uint32_t HOP_QUANTUM = 2;       // 깊어지면 바로 Q1로 양보해서 다양성 확보
    const float DRIFT_THRESHOLD = 0.65f;  // 엄격한 환각 통제 (64비트 중 42비트 이상 일치 요구)
    const uint32_t MAX_RESULTS = 250;     // 그래프를 더 깊게 파헤치도록 강제

public:
    SemanticEngine(CsrGraph* g) : graph(g) {}

    // 64비트 서명을 이용한 O(1) 코사인 유사도 근사 계산 (해밍 거리)
    float CalculateSimilarity(uint64_t sig1, uint64_t sig2) {
        int hamming_distance = __builtin_popcountll(sig1 ^ sig2);
        return 1.0f - (static_cast<float>(hamming_distance) / 64.0f);
    }

    // 🚀 [실험군] S-MLFQ 하이브리드 라우팅 (에이징 & 환각 격리 적용)
    BenchmarkResult RunSMLFQ(uint32_t start_node) {
        std::priority_queue<PathState> q0, q1, q2;
        std::unordered_set<uint32_t> visited;
        std::vector<uint32_t> collected_nodes;
        
        uint64_t query_signature = graph->nodes[start_node].semantic_signature;
        uint8_t target_class = graph->nodes[start_node].ground_truth_class;

        q0.push({start_node, 0.0f, 0});
        uint32_t search_steps = 0;
        const uint32_t MAX_STEPS_BUDGET = 350; // 💡 공평한 연산 예산 350번 제한

        while ((!q0.empty() || !q1.empty() || !q2.empty()) && search_steps < MAX_STEPS_BUDGET) {
            search_steps++;
            
            // 💡 [핵심 1] 에이징(Aging) 메커니즘: 50스텝마다 Q2에 갇힌 최고 유망주 1명을 Q1으로 구출 (창발성 부여)
            if (search_steps % 50 == 0 && !q2.empty()) {
                PathState aging_node = q2.top();
                q2.pop();
                aging_node.hop_run = 0; // 새 출발
                q1.push(aging_node);
            }

            PathState current;
            int active_q = 0;
            if (!q0.empty())      { current = q0.top(); q0.pop(); }
            else if (!q1.empty()) { current = q1.top(); q1.pop(); active_q = 1; }
            else                  { current = q2.top(); q2.pop(); active_q = 2; }

            if (visited.count(current.node_id)) continue;
            visited.insert(current.node_id);

            // 💡 [핵심 2] 환각 격리: Q2(유배지)에서 나온 노드는 '징검다리'로만 쓰고 LLM 문맥으로는 수집하지 않음!
            if (active_q != 2) {
                collected_nodes.push_back(current.node_id);
            }

            uint32_t start_idx = graph->row_ptr[current.node_id];
            uint32_t end_idx = graph->row_ptr[current.node_id + 1];

            for (uint32_t i = start_idx; i < end_idx; ++i) {
                uint32_t neighbor = graph->col_ind[i];
                if (visited.count(neighbor)) continue;

                float sim = CalculateSimilarity(query_signature, graph->nodes[neighbor].semantic_signature);
                float next_cost = current.cost + (1.0f - sim);
                PathState next_state = {neighbor, next_cost, current.hop_run + 1};

                if (sim < DRIFT_THRESHOLD) {
                    next_state.hop_run = 0;
                    q2.push(next_state); 
                } else if (active_q == 0 && next_state.hop_run >= HOP_QUANTUM) {
                    next_state.hop_run = 0;
                    q1.push(next_state); 
                } else {
                    if (active_q == 0) q0.push(next_state);
                    else if (active_q == 1) q1.push(next_state);
                    else q2.push(next_state);
                }
            }
        }
        return EvaluateMetrics(collected_nodes, search_steps, target_class);
    }

    // 🧪 [대조군] 순수 다익스트라 (Baseline)
    BenchmarkResult RunDijkstra(uint32_t start_node) {
        std::priority_queue<PathState> q0; 
        std::unordered_set<uint32_t> visited;
        std::vector<uint32_t> collected_nodes;
        
        uint64_t query_signature = graph->nodes[start_node].semantic_signature;
        uint8_t target_class = graph->nodes[start_node].ground_truth_class;

        q0.push({start_node, 0.0f, 0});
        uint32_t search_steps = 0;
        const uint32_t MAX_STEPS_BUDGET = 350; // 💡 동일한 예산 적용

        while (!q0.empty() && search_steps < MAX_STEPS_BUDGET) {
            search_steps++;
            
            PathState current = q0.top(); 
            q0.pop();

            if (visited.count(current.node_id)) continue;
            visited.insert(current.node_id);
            
            // 💡 다익스트라는 필터링 없이 주워지는 대로 100% 문맥에 때려 넣음 (환각 발생의 원인)
            collected_nodes.push_back(current.node_id);

            uint32_t start_idx = graph->row_ptr[current.node_id];
            uint32_t end_idx = graph->row_ptr[current.node_id + 1];

            for (uint32_t i = start_idx; i < end_idx; ++i) {
                uint32_t neighbor = graph->col_ind[i];
                if (visited.count(neighbor)) continue;

                float sim = CalculateSimilarity(query_signature, graph->nodes[neighbor].semantic_signature);
                float next_cost = current.cost + (1.0f - sim);
                
                q0.push({neighbor, next_cost, current.hop_run + 1}); 
            }
        }
        return EvaluateMetrics(collected_nodes, search_steps, target_class);
    }

private:
    BenchmarkResult EvaluateMetrics(const std::vector<uint32_t>& collected, uint32_t steps, uint8_t target_class) {
        uint32_t hit_count = 0;
        std::unordered_set<uint8_t> unique_classes;

        for (uint32_t node_id : collected) {
            uint8_t node_class = graph->nodes[node_id].ground_truth_class;
            if (node_class == target_class) hit_count++;
            unique_classes.insert(node_class);
        }

        return {
            steps, 
            (static_cast<float>(hit_count) / collected.size()) * 100.0f, 
            static_cast<uint32_t>(unique_classes.size())
        };
    }
};

#include <fstream> // 상단에 추가 (파일 입출력용)

int main() {
    // 윈도우 파워셸 한글 깨짐 방지
    system("chcp 65001 > nul");

    CsrGraph graph;
    if (graph.LoadFromFiles("nodes.txt", "edges.txt", 2708)) {
        SemanticEngine engine(&graph);
        uint32_t test_node = 0;

        // 1. 엔진 실행
        BenchmarkResult res_dijkstra = engine.RunDijkstra(test_node);
        BenchmarkResult res_smlfq = engine.RunSMLFQ(test_node);

        // 2. 콘솔 출력
        std::cout << "\n[Dijkstra] Steps: " << res_dijkstra.visited_nodes 
                  << " | Relevance: " << res_dijkstra.relevance_score 
                  << "% | Diversity: " << res_dijkstra.diversity_score << "\n";
                  
        std::cout << "[S-MLFQ]   Steps: " << res_smlfq.visited_nodes 
                  << " | Relevance: " << res_smlfq.relevance_score 
                  << "% | Diversity: " << res_smlfq.diversity_score << "\n\n";

        // 3. 파이썬이 읽을 수 있도록 CSV 파일로 자동 저장 (핵심!)
        std::ofstream out_file("benchmark_results.csv");
        if (out_file.is_open()) {
            out_file << "Algorithm,Steps,Relevance,Diversity\n";
            out_file << "Dijkstra," << res_dijkstra.visited_nodes << "," 
                     << res_dijkstra.relevance_score << "," << res_dijkstra.diversity_score << "\n";
            out_file << "S-MLFQ," << res_smlfq.visited_nodes << "," 
                     << res_smlfq.relevance_score << "," << res_smlfq.diversity_score << "\n";
            out_file.close();
            std::cout << "✅ benchmark_results.csv 파일이 생성되었습니다.\n";
        }
    }
    return 0;
}