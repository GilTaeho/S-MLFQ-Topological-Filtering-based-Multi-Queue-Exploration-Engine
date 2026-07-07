import subprocess

print("🚀 파이썬에서 C++ S-MLFQ 엔진을 직접 호출합니다...")

# subprocess를 통해 C++ 실행 파일에 파라미터를 완벽한 UTF-8로 전달
result = subprocess.run(
    ["./smlfq_engine.exe", "법", "15"], 
    capture_output=True, 
    text=True, 
    encoding='utf-8'
)

print("\n[C++ 디버그 로그]")
print(result.stderr)

print("\n[최종 JSON 결과]")
print(result.stdout)