import optuna
import json
import time
from smlfq_runner import run_smlfq_engine

# 테스트할 대상 개념 리스트
TEST_TARGETS = ["인공지능", "시스템", "논리적 추론"]

def objective(trial):
    # 튜닝할 파라미터 제안
    budget = trial.suggest_int("budget", 10, 50)
    
    total_time = 0
    total_nodes = 0
    
    # 벤치마크 실행
    for target in TEST_TARGETS:
        start = time.time()
        result = run_smlfq_engine(target, budget=budget)
        end = time.time()
        
        if "error" not in result:
            total_time += (end - start)
            total_nodes += len(result.get('collected_nodes', []))
            
    # 목적 함수: 시간당 수집된 노드 수 (높을수록 좋음)
    score = total_nodes / (total_time + 1e-6)
    return score

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)
    
    print(f"🎯 최적 파라미터: {study.best_params}")
    print(f"🚀 최고 점수: {study.best_value}")