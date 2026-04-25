# AgenticCoder 🤖💻

[![Built with LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-blue)](https://python.langchain.com/docs/langgraph/)
[![Powered by Gemini](https://img.shields.io/badge/Model-Gemini_3.1_Flash_Lite-orange)](https://deepmind.google/technologies/gemini/)
[![Frontend UI](https://img.shields.io/badge/UI-React_%2B_Vite-61DAFB?logo=react)](https://react.dev)

An advanced, end-to-end multi-agent AI coding system designed to autonomously plan, write, and test software. AgenticCoder replaces standard linear prompting with a cyclic state-machine orchestrator, ensuring code is verified in an execution sandbox before it is finalized.

📖 **For a deep dive into the architecture, tools, and technical decisions, please read the [PRODUCT BIBLE](PRODUCT_BIBLE.md).**

---

## ✨ Features

- **Multi-Agent Orchestration**: Three distinct agents (`Planner`, `Coder`, and `Tester`) working in a LangGraph state machine loop.
- **Hybrid Knowledge Retrieval**: Combines Vector RAG (ChromaDB) for semantic code search with GraphRAG (NetworkX + AST) for structural dependency mapping.
- **MCP Tool Integration**: Secure file system interaction and Python execution sandboxing using `@tool` wrappers.
- **Premium Web IDE**: A real-time, VS Code-inspired React frontend utilizing Monaco Editor and React Flow to visualize the agent's thought process.
- **Self-Healing Loop**: If the Tester Agent detects a syntax error or runtime failure, it feeds the stack trace back to the Coder Agent for automatic bug fixing.
- **Full Observability**: Integrated with LangSmith to trace LLM prompts, token usage, and tool executions.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/vishnubv89/agentic_coder.git
cd agentic_coder
```

### 2. Set Up the Environment
You will need your API keys. Copy the example environment file:
```bash
cp .env.example .env
```
Fill in the `.env` file with your credentials:
- `GEMINI_API_KEY`: Required for the LLM agents.
- `LANGCHAIN_API_KEY`: Required for LangSmith tracing.

### 3. Install Dependencies
```bash
# Backend Dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend Dependencies
cd frontend
npm install
cd ..
```

### 4. Run the Application
You can easily start both the FastAPI backend and the React frontend simultaneously using the provided startup script:
```bash
./run.sh
```

Once running, open your browser to [http://localhost:5173](http://localhost:5173).

---

## 🔍 Observability with LangSmith
This project comes pre-configured with LangSmith. As long as `LANGCHAIN_TRACING_V2=true` is in your `.env` file, all graph executions, tool calls, and LLM prompts will be logged to your LangSmith dashboard under the project `agentic-coder-portfolio`.

---

## 🛠️ Technology Stack
* **Orchestration**: Python, LangGraph, LangChain
* **LLM**: Google Gemini 3.1 Flash Lite Preview
* **Backend**: FastAPI, Uvicorn, WebSockets
* **Frontend**: React, Vite, Monaco Editor, React Flow
* **Databases**: ChromaDB (Vector), NetworkX (Graph)

*(For a full breakdown, see the [Product Bible](PRODUCT_BIBLE.md))*
