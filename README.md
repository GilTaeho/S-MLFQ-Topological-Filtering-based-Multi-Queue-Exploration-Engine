# 🚀 S-MLFQ: Topological Filtering-based Multi-Queue Exploration Engine
> **Next-Generation Exploration Scheduling Architecture for Mitigating LLM Hallucinations in Knowledge Graph RAG Environments**

## 📖 Overview
As Knowledge Graph-based Retrieval-Augmented Generation (Graph RAG) emerges to overcome the hallucination phenomenon in Large Language Models (LLMs), existing exploration algorithms reveal critical limitations. Dijkstra's algorithm is vulnerable to "filter bubbles" trapped in noise hubs, while Random Walk often causes "semantic drift."

This project proposes and implements **S-MLFQ (Semantic Multi-Level Feedback Queue)**, an innovative engine that integrates Operating System (OS) Multi-Level Feedback Queue scheduling theories into graph exploration for the first time.

## ✨ Key Features
* **Topological Filtering:** Identifies nodes exceeding a certain degree threshold as noise hubs and isolates them into the lowest-priority queue (Q2), performing filtering in $O(1)$ constant time.
* **Controlled Serendipity:** Utilizes an aging mechanism to execute intentional context switching to other domains when exploration stagnates, fusing innovative knowledge while maintaining a safe trajectory.
* **Two-Track Architecture:** Provides both a Web-based real-time exploration service (Track 1) and an S-MLFQ performance evaluation benchmark system (Track 2) simultaneously.
* **eXplainable AI (XAI):** Transparently visualizes the previously black-box RAG exploration process, outputting the causal relationships of node collection and filtering in the form of XAI logs.

## 🛠 Tech Stack
* **Core Engine:** C++
* **Backend:** Python, Flask
* **Frontend:** HTML, JavaScript (Vis.js)
* **LLM & Knowledge Extraction:** Ollama API (Llama 3.1)
* **Data Visualization:** NetworkX

## ⚙️ Getting Started
We recommend running this project in a Linux environment (WSL2) or a Docker container for seamless building and execution.

### Prerequisites
* G++ compiler
* Python 3.8+
* Docker (Optional)

### Installation & Execution
```bash

# 1. Clone the repository
git clone [https://github.com/YourUsername/S-MLFQ.git](https://github.com/YourUsername/S-MLFQ.git)
cd S-MLFQ

# 2. Compile the C++ Core Engine
g++ -o smlfq_engine.exe smlfq_engine.cpp

# (Optional) Build an isolated environment using Docker
docker build -t s-mlfq-env .

# 3. Run the LLM knowledge extraction pipeline and Web Server (Track 1)
python app.py
```
## 📊 Performance Evaluation
In controlled benchmark experiments with a 30% adversarial noise injection, S-MLFQ demonstrated overwhelming performance compared to existing algorithms:Exploration Efficiency & Relevance: Perfectly bypassed decoy noise, securing the highest exploration efficiency and semantic relevance against Dijkstra and Random Walk.Space Complexity: Maintained a stable, linear space complexity of $O(V)$ proportional to the total number of nodes without memory bloat, despite the introduction of multiple queues.

### 👨‍💻 Author
Taeho Gil/
Department of Software, Sungkyunkwan University

