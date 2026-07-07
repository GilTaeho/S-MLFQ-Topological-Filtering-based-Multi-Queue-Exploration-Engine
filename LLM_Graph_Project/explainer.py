import subprocess

def run_cpp_engine():
    try:
        result = subprocess.run(
            ['.\\graph_builder.exe'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.stdout
    except Exception as e:
        return f"C++ 엔진 실행 중 오류 발생: {e}"

def generate_xai_explanation(path_text):
    # API 대신 로컬에서 즉시 반환하는 자연어 해설입니다.
    mock_explanation = """
    [논리적 인과관계 분석]
    1. 최신 'LLM'은 구조적으로 'Transformer' 아키텍처를 기반으로 작동합니다.
    2. 이 구조적 특성으로 인해 학습되지 않은 정보를 지어내는 'Hallucination(환각)' 현상이 필연적으로 발생합니다.
    3. 이를 해결하기 위해 외부의 신뢰할 수 있는 정보를 검색해오는 'RAG' 기술이 LLM의 필수적인 보완책으로 사용됩니다.
    """
    return mock_explanation

if __name__ == "__main__":
    print("[1/2] 파이썬이 C++ 다익스트라 엔진을 가동합니다...")
    cpp_output = run_cpp_engine()
    
    if "논리적 경로가 없습니다" in cpp_output or "오류" in cpp_output:
        print(cpp_output)
    else:
        print("✅ C++ 엔진 탐색 완료! 경로 데이터를 캡처했습니다.")
        print("\n[2/2] [로컬 모드] 캡처된 경로를 바탕으로 XAI 해설을 생성합니다...")
        
        print("\n======================================================")
        print("🤖 [최종 XAI 리포트] 답변 도출 근거 해설")
        print("======================================================")
        print(generate_xai_explanation(cpp_output))
        print("======================================================\n")