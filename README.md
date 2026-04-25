# AgenticCoder: Multi-Agent AI Coding System 🚀

An end-to-end coding agent portfolio project demonstrating state-of-the-art (SOTA) agentic AI concepts.

## 🌟 Market Trending Concepts Showcased
- **Multi-Agent Orchestration (LangGraph)**: A state-machine based workflow where specialized agents (Planner, Coder, Tester) collaborate iteratively.
- **Hybrid Retrieval (RAG + GraphRAG)**: Combines semantic vector search (ChromaDB) with codebase AST mapping (NetworkX) to provide the Coder Agent with deep context.
- **Model Context Protocol (MCP) Tools**: Standardized, secure tool schemas for file manipulation and isolated code execution sandboxing.
- **Observability (LangSmith)**: Built-in tracing for visualizing the agent's internal thought processes, LangGraph node transitions, and tool calls.

## 🏗️ Architecture
1. **Planner Agent**: Analyzes the user's task and generates a step-by-step execution plan using Gemini 1.5 Pro.
2. **Coder Agent**: Uses the Hybrid Retriever and MCP file tools to generate and write Python scripts based on the plan.
3. **Tester Agent**: Uses MCP execution tools to safely run the generated code locally. If it fails, it returns the STDOUT/STDERR to the Coder for revisions.

## 🚀 Getting Started

1. Clone the repository: `git clone https://github.com/vishnubv89/agentic_coder.git`
2. Set up the Python Backend:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set up the React Frontend:
   ```bash
   cd frontend
   npm install
   ```
4. Copy `.env.example` to `.env` and add your API keys:
   - `GEMINI_API_KEY`: Required for the LLM agents.
   - `LANGCHAIN_API_KEY`: Required for LangSmith tracing.
5. Run the Application:
   - Terminal 1 (Backend): `uvicorn api.server:app --reload`
   - Terminal 2 (Frontend): `cd frontend && npm run dev`
   
   Then open the provided `localhost:5173` URL to view the AgenticCoder IDE!

## 🔍 Observability with LangSmith
This project comes pre-configured with LangSmith. As long as `LANGCHAIN_TRACING_V2=true` is in your `.env` file, all graph executions, tool calls, and LLM prompts will be logged to your LangSmith dashboard under the project `agentic-coder-portfolio`.
