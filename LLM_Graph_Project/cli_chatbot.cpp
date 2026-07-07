#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <chrono> // 🔥 실행 시간 측정을 위해 새로 추가된 라이브러리
#include "json.hpp"
#include "graph_models.hpp"
#include "smlfq_engine.hpp"

using json = nlohmann::json;

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
};

int main() {
    // 1. 파이썬이 넘겨준 검색 설정(query.json) 읽기
    std::ifstream q_file("query.json");
    if (!q_file.is_open()) return 1;
    json query_json;
    q_file >> query_json;
    
    std::string start_concept = query_json["start"];
    int search_budget = query_json["budget"];
    std::string mode = query_json.value("mode", "smlfq"); 

    // 2. 파이썬이 생성한 지식 그래프(graph_data.json) 읽기 및 메모리 적재
    KnowledgeGraph kg;
    std::ifstream file("graph_data.json");
    json j_array;
    file >> j_array;

    for (const auto& item : j_array) {
        int source_id = kg.get_or_add_node(item["source"]);
        int target_id = kg.get_or_add_node(item["target"]);
        kg.nodes[source_id].add_edge(target_id, item["relation"], item["weight"]);
    }

    if (kg.name_to_id.find(start_concept) == kg.name_to_id.end()) return 1;

    int start_id = kg.name_to_id[start_concept];
    SemanticMlfqEngine engine(kg.nodes);
    SearchResult result;

    // =========================================================
    // ⏱️ [성능 측정 구간 시작]
    // 데이터 로딩에 걸린 시간은 제외하고, 순수 알고리즘 탐색 시간만 잽니다.
    // =========================================================
    auto start_time = std::chrono::high_resolution_clock::now();

    if (mode == "dijkstra") {
        result = engine.SearchDijkstra(start_id, search_budget);
    } else if (mode == "random") {
        result = engine.SearchRandomWalk(start_id, search_budget);
    } else {
        result = engine.Search(start_id, search_budget);
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    // =========================================================
    // ⏱️ [성능 측정 구간 종료]
    // =========================================================

    // 📊 실행 시간(밀리초) 및 공간 복잡도(사용된 큐/로그 노드 수) 계산
    double exec_time_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
    int space_usage = result.collected_concepts.size() + result.xai_logs.size();

    // 3. 파이썬으로 돌려줄 결과(result.json) 포장
    json output_json;
    output_json["collected_nodes"] = result.collected_concepts;
    output_json["xai_logs"] = result.xai_logs;
    output_json["exec_time_ms"] = exec_time_ms; // 파이썬 차트용 시간 데이터 추가
    output_json["space_usage"] = space_usage;   // 파이썬 차트용 공간 데이터 추가

    std::ofstream r_file("result.json");
    r_file << output_json.dump(4);
    
    return 0;
}