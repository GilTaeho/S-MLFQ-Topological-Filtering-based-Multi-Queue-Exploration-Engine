#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <unordered_map>
#include <queue>     // 다익스트라의 핵심: 우선순위 큐
#include <limits>    // 무한대(INF) 값을 쓰기 위함
#include <algorithm> // 경로를 역추적하고 뒤집기(reverse) 위함
#include "json.hpp"

// 윈도우 환경에서 한글 깨짐을 영구적으로 방지하는 헤더
#ifdef _WIN32
#include <windows.h>
#endif

using json = nlohmann::json;

// 1. 간선(Edge) 구조체
struct Edge {
    int target_index;       
    std::string relation;   
    float weight;           
};

// 2. 노드(Node) 클래스
class Node {
public:
    int id;                         
    std::string concept_text;       
    std::vector<Edge> edges;        

    Node(int node_id, std::string text) : id(node_id), concept_text(text) {}

    void add_edge(int target_id, std::string rel, float w) {
        edges.push_back({target_id, rel, w});
    }
};

// --- [추가됨] 다익스트라 탐색을 위한 보조 구조체 ---
// 큐 안에서 '어떤 노드가 가장 거리가 짧은가'를 비교하기 위해 만듭니다.
struct PqNode {
    int node_id;
    float current_total_weight; // 지금까지 걸린 총 가중치 거리

    // 우선순위 큐를 '최소 힙(Min-Heap)'으로 만들기 위한 연산자 오버로딩
    // 거리가 큰 녀석이 뒤로 밀려나게 (작은 게 위로 올라오게) 설정합니다.
    bool operator>(const PqNode& other) const {
        return current_total_weight > other.current_total_weight;
    }
};

// 3. 지식 그래프 코어 클래스
class KnowledgeGraph {
public:
    std::vector<Node> nodes;
    std::unordered_map<std::string, int> name_to_id;

    int get_or_add_node(std::string concept) {
        if (name_to_id.find(concept) == name_to_id.end()) {
            int new_id = nodes.size(); 
            nodes.push_back(Node(new_id, concept));
            name_to_id[concept] = new_id;
            return new_id;
        }
        return name_to_id[concept];
    }

    // --- [핵심 엔진] 다익스트라 경로 탐색 함수 ---
    void find_and_print_explanation(std::string start_name, std::string target_name) {
        // 1. 출발지와 목적지가 우리 아파트(해시 테이블)에 있는지 확인
        if (name_to_id.find(start_name) == name_to_id.end() || name_to_id.find(target_name) == name_to_id.end()) {
            std::cout << "오류: 해당 개념을 지식 그래프에서 찾을 수 없습니다.\n";
            return;
        }

        int start_id = name_to_id[start_name];
        int target_id = name_to_id[target_name];

        // 2. 최단 거리 배열과, 경로를 역추적하기 위한 '이전 노드' 배열 준비
        std::vector<float> dist(nodes.size(), std::numeric_limits<float>::max());
        std::vector<int> prev_node(nodes.size(), -1);
        std::vector<std::string> prev_relation(nodes.size(), ""); // 어떤 관계로 넘어왔는지 기억

        // 3. 최소 힙 우선순위 큐 생성 및 출발점 세팅
        std::priority_queue<PqNode, std::vector<PqNode>, std::greater<PqNode>> pq;
        
        dist[start_id] = 0.0f;
        pq.push({start_id, 0.0f});

        // 4. 다익스트라 탐색 시작!
        while (!pq.empty()) {
            int current_id = pq.top().node_id;
            float current_weight = pq.top().current_total_weight;
            pq.pop();

            // 목표 방에 도착했다면 탐색 종료 (최단 경로 확정)
            if (current_id == target_id) break;

            // 이미 더 빠른 길을 찾았다면 스킵 (최적화)
            if (current_weight > dist[current_id]) continue;

            // 현재 방과 연결된 모든 이웃 방들을 검사
            for (const auto& edge : nodes[current_id].edges) {
                int next_id = edge.target_index;
                float next_weight = current_weight + edge.weight;

                // 더 빠르고 논리적인(가중치가 낮은) 길을 발견했다면 업데이트!
                if (next_weight < dist[next_id]) {
                    dist[next_id] = next_weight;
                    prev_node[next_id] = current_id;           // 어디서 왔는지 기록
                    prev_relation[next_id] = edge.relation;    // 무슨 관계로 왔는지 기록
                    pq.push({next_id, next_weight});
                }
            }
        }

        // 5. 목적지부터 출발지까지 경로 역추적
        if (dist[target_id] == std::numeric_limits<float>::max()) {
            std::cout << start_name << "에서 " << target_name << "(으)로 가는 논리적 경로가 없습니다.\n";
            return;
        }

        std::vector<std::string> path_explanation;
        int curr = target_id;
        while (curr != start_id) {
            int p = prev_node[curr];
            std::string rel = prev_relation[curr];
            // "RAG <-(RAG 기술로 완화할 수 있음)- Hallucination" 형태로 저장
            path_explanation.push_back("[" + nodes[curr].concept_text + "]");
            path_explanation.push_back("  <--(" + rel + ")--  ");
            curr = p;
        }
        path_explanation.push_back("[" + nodes[start_id].concept_text + "]");

        // 역순으로 저장되었으므로 뒤집기
        std::reverse(path_explanation.begin(), path_explanation.end());

        // 6. 결과 출력
        std::cout << "\n======================================================\n";
        std::cout << "🔍 [XAI 분석] LLM이 답변을 도출한 논리적 근거 경로\n";
        std::cout << "======================================================\n";
        for (const auto& step : path_explanation) {
            std::cout << step;
        }
        std::cout << "\n\n(총 가중치 합산 비용: " << dist[target_id] << ")\n";
    }
};

int main() {
    // [핵심] 윈도우 환경 한글 깨짐 강제 해결!
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
#endif

    KnowledgeGraph kg;

    std::ifstream file("graph_data.json");
    if (!file.is_open()) {
        std::cerr << "오류: graph_data.json 파일을 찾을 수 없습니다!\n";
        return 1;
    }

    json j_array;
    file >> j_array;

    for (const auto& item : j_array) {
        int source_id = kg.get_or_add_node(item["source"]);
        int target_id = kg.get_or_add_node(item["target"]);
        kg.nodes[source_id].add_edge(target_id, item["relation"], item["weight"]);
    }

    // --- 우리가 만든 다익스트라 엔진 테스트 ---
    // 질문: "LLM이 왜 RAG를 필요로 해?" 에 대한 XAI 근거 추적
    kg.find_and_print_explanation("LLM", "RAG");

    return 0;
}