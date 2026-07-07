from flask import Flask, render_template, request, jsonify
import json
import subprocess
import requests
import re
import time

# 🚀 우리가 만든 S-MLFQ 실행 모듈 임포트
from smlfq_runner import run_smlfq_engine

app = Flask(__name__)

def clean_json_string(raw_text):
    """AI가 응답에 섞어 넣은 마크다운(```json) 부품을 완벽히 제거하는 함수"""
    text = raw_text.strip()
    text = re.sub(re.compile(r'^```json\s*', re.IGNORECASE), '', text)
    text = re.sub(re.compile(r'^```\s*', re.IGNORECASE), '', text)
    text = re.sub(re.compile(r'\s*```$', re.IGNORECASE), '', text)
    return text.strip()

def extract_knowledge(text):
    print("\n🧠 [Ollama] 로컬 AI 모델 분석 시작...")
    url = "http://127.0.0.1:11434/api/generate"
    
    prompt = f"""
    You are a Knowledge Graph extraction expert. Analyze the given text and extract entities (nodes) and their relations (edges).
    
    CRITICAL RULES:
    1. Respond ONLY with a valid JSON object matching the schema below. No conversational text, no explanations.
    2. Match the language of the 'relation', 'source', and 'target' to the input text.
    3. Extract as many relations as possible (at least 3-5 edges).
    4. 반드시 문장 간 연결성을 고려하십시오. 이전 문장의 주요 개념을 다음 문장의 개념과 'context_flow' 관계로 연결하십시오.
    5. 매우 중요: 이전 문장의 핵심 개념과 현재 문장의 핵심 개념 사이에 2개 이상의 'context_flow' 엣지를 생성하여, 전체 그래프가 하나의 거대한 연결 그래프(Connected Graph)가 되도록 하십시오.
    
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
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        ai_raw_text = response.json().get("response", "{}")
        
        # 🛡️ 마크다운 제거 및 JSON 파싱
        cleaned_text = clean_json_string(ai_raw_text)
        json_data = json.loads(cleaned_text)
        
        extracted_edges = json_data.get("edges", [])
        if isinstance(json_data, list):
            extracted_edges = json_data
            
        print(f"🎯 [Ollama] 정제 완료! 총 {len(extracted_edges)}개의 관계성을 찾았습니다.")
        return extracted_edges
        
    except Exception as e:
        print(f"❌ [Ollama] 데이터 정제 실패: {e}")
        return []

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/process', methods=['POST'])
def process():
    user_text = request.json.get('text')
    
    edges = extract_knowledge(user_text)
    
    # 추출 성공 시 C++ 엔진이 읽을 수 있도록 로컬 파일(graph_data.json)로 저장
    if edges:
        with open("graph_data.json", "w", encoding="utf-8") as f:
            json.dump(edges, f, indent=4, ensure_ascii=False)
        print("💾 'graph_data.json' 파일이 동적으로 갱신되었습니다.")
            
    return jsonify({"edges": edges})

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.json
    source = data.get('source')
    # 기존 타겟(target)은 목적지 도달 다익스트라용이므로, S-MLFQ 예산 탐색에서는 예산(budget) 파라미터를 추가 사용
    budget = data.get('budget', 15) 

    # ⏱️ 시간 측정 시작
    start_time = time.time()
    
    try:
        # 🚀 [핵심 변경] 파일 IPC 기반 S-MLFQ 엔진 호출
        # 기존의 복잡한 subprocess(stdin/stdout 파싱)를 걷어내고 파이썬 딕셔너리로 바로 받습니다.
        engine_result = run_smlfq_engine(source, budget=budget)
        
        if "error" in engine_result:
            chat_response = f"❌ 오류: {engine_result['error']}"
        else:
            collected_nodes = engine_result.get('collected_nodes', [])
            xai_logs = engine_result.get('xai_logs', [])
            
            # 대시보드 화면에 출력하기 좋게 문자열로 예쁘게 조립합니다
            nodes_text = ", ".join(collected_nodes)
            logs_text = "\n".join(xai_logs)
            
            chat_response = f"✅ [S-MLFQ 지식 탐색 완료]\n\n"
            chat_response += f"📌 [수집된 핵심 문맥]\n{nodes_text}\n\n"
            chat_response += f"🔍 [XAI 엔진 스케줄링 과정]\n{logs_text}"
            
    except Exception as e:
        chat_response = f"❌ 탐색 중 파이썬 서버 에러 발생: {e}"

    # ⏱️ 시간 측정 종료
    end_time = time.time()
    elapsed_ms = round((end_time - start_time) * 1000, 2)

    return jsonify({
        "response": chat_response,
        "elapsed_time": f"{elapsed_ms}ms"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)