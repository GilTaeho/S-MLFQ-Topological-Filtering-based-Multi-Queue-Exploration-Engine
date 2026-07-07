import json
import requests
import re
import collections

def clean_json_string(raw_text):
    """AI가 뱉은 텍스트에서 ```json ... ``` 마크다운 태그를 제거하는 방어 함수"""
    text = raw_text.strip()
    # ```json 또는 ```로 시작하는 부품 제거
    text = re.sub(re.compile(r'^```json\s*', re.IGNORECASE), '', text)
    text = re.sub(re.compile(r'^```\s*', re.IGNORECASE), '', text)
    text = re.sub(re.compile(r'\s*```$', re.IGNORECASE), '', text)
    return text.strip()

def ensure_global_connectivity(edges):
    """
    LLM이 생성한 엣지들을 분석하여 끊어진 그래프(Islands)가 있다면,
    가장 많이 등장한 중심 노드(Main Hub)와 강제로 연결하여 하나의 그래프로 만듭니다.
    """
    if not edges:
        return edges

    # 1. 그래프 인접 리스트 생성 및 중심 노드(Hub) 찾기
    adj = collections.defaultdict(list)
    node_counts = collections.Counter()
    
    for edge in edges:
        u, v = edge['source'], edge['target']
        adj[u].append(v)
        adj[v].append(u)
        node_counts[u] += 1
        node_counts[v] += 1

    if not adj:
        return edges

    # 전체 그래프에서 가장 많이 언급된 노드를 '메인 허브'로 선정
    main_hub = node_counts.most_common(1)[0][0]
    
    # 2. BFS 탐색으로 찢어진 컴포넌트(조각) 덩어리 찾기
    visited = set()
    components = []

    for node in adj.keys():
        if node not in visited:
            # 새로운 조각 발견! BFS로 이 조각에 속한 모든 노드 탐색
            queue = collections.deque([node])
            comp = set()
            while queue:
                curr = queue.popleft()
                if curr not in visited:
                    visited.add(curr)
                    comp.add(curr)
                    queue.extend(adj[curr])
            components.append(comp)

    # 3. 끊어진 조각이 2개 이상이라면 강제 다리(Bridge) 건설
    if len(components) > 1:
        print(f"⚠️ LLM이 {len(components)}개의 끊어진 그래프를 생성했습니다. 강제 병합 알고리즘을 가동합니다.")
        
        # 메인 허브가 속한 컴포넌트 찾기
        main_comp = next((c for c in components if main_hub in c), components[0])
        
        for comp in components:
            if comp != main_comp:
                # 외딴섬(끊어진 조각)에서 임의의 노드를 하나 골라 메인 허브와 연결
                orphan_node = list(comp)[0]
                edges.append({
                    "source": main_hub,
                    "target": orphan_node,
                    "relation": "문맥적 연관(병합)",
                    "weight": 0.5
                })
                print(f"🔗 강제 브릿지 생성: [{main_hub}] ──(연결)──> [{orphan_node}]")
                
    return edges

def extract_with_local_ai(text):
    print("🧠 [로컬 AI] 입력을 분석하고 정형 지식 구조를 생성 중입니다...")
    url = "[http://127.0.0.1:11434/api/generate](http://127.0.0.1:11434/api/generate)"
    
    # 🔥 중요: 입력 텍스트의 언어에 맞춰 결과 언어를 일치시키도록 프롬프트 고도화
    prompt = f"""
    You are a Knowledge Graph extraction expert. Analyze the given text and extract entities (nodes) and their relations (edges).
    
    CRITICAL RULES:
    1. CENTRAL HUB: Identify the primary subject of the input text as the "ROOT_HUB". Every other concept MUST be directly or indirectly connected to this ROOT_HUB.
    2. NO ISOLATION: No concept is allowed to be independent. If a concept seems isolated, connect it to the ROOT_HUB or its nearest parent concept using the relation "associated_with".
    3. HIERARCHY: Structure relations as [ROOT_HUB] -> [Sub-Concept] -> [Details].
    4. NO SENTENCES: Only keywords for entities, short verbs for relations.
    5. JSON FORMAT ONLY: Respond with a valid JSON object.

    [Schema Format]
    {{
        "edges": [
            {{"source": "Entity A", "target": "Entity B", "relation": "Description of relationship", "weight": 0.5}}
        ]
    }}

    [Input Text]
    {text}
    """

    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "format": "json", 
        "stream": False
    }

    try:
        # UTF-8 헤더를 명시적으로 지정하여 요청
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Ollama로부터 받은 결과 가공
        ai_raw_text = response.json().get("response", "{}")
        
        # 🛡️ 방어 로직 1: 마크다운 문법 스트리핑
        cleaned_text = clean_json_string(ai_raw_text)
        
        # JSON 데이터 객체로 변환
        json_data = json.loads(cleaned_text)
        extracted_edges = json_data.get("edges", [])
        
        if isinstance(json_data, list):
            extracted_edges = json_data
            
        # 🔥 [추가된 부분] LLM이 만든 데이터를 알고리즘으로 검사하고 강제 병합!
        extracted_edges = ensure_global_connectivity(extracted_edges)
        

        print(f"✅ 파이프라인 정제 완료: 총 {len(extracted_edges)}개의 관계 추출 성공.")
        return extracted_edges
        
    except Exception as e:
        print(f"❌ 파이프라인 치명적 오류 발생: {e}")
        print("🚨 AI 원본 응답 데이터 확인용:", ai_raw_text if 'ai_raw_text' in locals() else "없음")
        return []

if __name__ == "__main__":
    # 🧪 영어 테스트 문장 예시 (원하시면 한국어 문장으로 바꾸셔도 완벽 작동합니다)
    sample_text = """A man of genius makes no mistakes. His errors are volitional and are the portals of discovery."""
    
    edges = extract_with_local_ai(sample_text)
    
    if edges:
        # 모든 노드 중 가장 많이 등장하는(혹은 첫 번째) 노드를 중심 노드로 설정
        main_node = edges[0]['source'] 
        # 연결되지 않은 노드들이 있다면, 그 노드들을 main_node와 '연결' 엣지로 강제 병합
        # (이후, 이 데이터를 graph_data.json으로 저장)
        # 🛡️ 방어 로직 2: 파일 저장 시 utf-8을 명시하고 ensure_ascii=False로 글자 깨짐 완전 방지
        with open("graph_data.json", "w", encoding="utf-8") as f:
            json.dump(edges, f, indent=4, ensure_ascii=False)
        print("💾 'graph_data.json' 파일이 완벽한 UTF-8 표준 배열 규격으로 갱신되었습니다.")
    else:
        print("⚠️ 데이터가 추출되지 않아 파일이 갱신되지 않았습니다. 프롬프트나 Ollama 상태를 확인하세요.")