import json
import subprocess
import os

def run_smlfq_engine(start_word, budget=15):
    # 1. C++이 읽을 query.json 파일 생성 (UTF-8 강제)
    query_data = {
        "start": start_word,
        "budget": budget
    }
    with open("query.json", "w", encoding="utf-8") as f:
        json.dump(query_data, f, ensure_ascii=False)

    # 2. C++ 엔진 무식하게 실행 (터미널 출력, argv 다 무시)
    subprocess.run(["./smlfq_engine.exe"])

    # 3. C++이 남겨둔 result.json 읽어오기
    if not os.path.exists("result.json"):
        return {"error": "C++ 엔진이 결과를 만들지 못했습니다."}
        
    with open("result.json", "r", encoding="utf-8") as f:
        result = json.load(f)
        
    return result

# ==== [테스트 실행] ====
if __name__ == "__main__":
    print("🚀 [테스트 1] '법' 탐색")
    res1 = run_smlfq_engine("법", 15)
    print(f"수집된 노드: {res1.get('collected_nodes')}\n")

    print("🚀 [테스트 2] '인공지능' 탐색")
    res2 = run_smlfq_engine("인공지능", 20)
    print(f"수집된 노드: {res2.get('collected_nodes')}")