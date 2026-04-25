# AgenticCoder: The Product Bible

## 1. Executive Summary
**AgenticCoder** is an advanced, end-to-end multi-agent AI coding system. Designed as a portfolio-grade application, it moves beyond simple CLI-based LLM wrappers by implementing a state-machine orchestrator, isolated tool-calling execution environments, hybrid knowledge retrieval, and a premium real-time web IDE.

The system is capable of breaking down complex coding tasks, executing code generation autonomously, and critically, verifying its own work through a specialized Tester Agent before presenting the final artifact.

---

## 2. Core Architecture
The system is divided into three distinct layers:

### A. The Agentic Orchestrator (LangGraph)
Instead of linear sequential prompting, AgenticCoder utilizes a cyclic, state-driven directed graph. 
- **State Management**: A global `AgenticCoderState` (TypedDict) acts as the memory bank, passing messages, generated code artifacts, and execution errors between nodes.
- **Conditional Routing**: If the Tester Agent encounters an error, the graph dynamically routes the workflow back to the Coder Agent with the stack trace, creating an autonomous self-healing loop.

### B. The Backend API (FastAPI)
The LangGraph engine is wrapped in an asynchronous FastAPI server.
- **WebSocket Streaming**: By utilizing LangGraph's `.stream()` capabilities, the backend pushes live state updates (what the agent is thinking, what tools it is calling, and what code it is writing) down a WebSocket connection to the client in real-time.

### C. The Web IDE Frontend (React + Vite)
A premium, VS Code-inspired browser interface.
- **Monaco Editor**: Provides a native IDE experience for viewing generated code.
- **React Flow**: Renders the "Agent Mind" visually, allowing the user to watch the state-machine transition between `Planner`, `Coder`, and `Tester` nodes live.

---

## 3. The Multi-Agent Workflow
The workflow relies on three specialized agents, all powered by **Gemini 3.1 Flash Lite Preview**:

1. **Planner Agent**
   - **Role**: The Architect.
   - **Function**: Takes the raw user prompt and breaks it down into a structured JSON array of actionable steps. It does not write code; it scopes the work.
2. **Coder Agent**
   - **Role**: The Developer.
   - **Function**: Reads the plan and has access to Model Context Protocol (MCP) file-writing tools. It translates the plan into Python code and saves it to the disk.
3. **Tester Agent**
   - **Role**: The QA Engineer.
   - **Function**: Reviews the generated code and executes it in an isolated sandbox using the `execute_python_code` tool. It captures `stdout` and `stderr`. If it detects an error, it fails the node, forcing the graph to loop back to the Coder for a fix.

---

## 4. Knowledge Retrieval Strategy (Hybrid RAG)
To ensure the agents have context about the existing codebase, AgenticCoder implements a dual-retrieval system:
1. **Vector RAG (Semantic Search)**: Powered by `ChromaDB`, it embeds codebase snippets so the LLM can find functions based on conceptual similarity.
2. **GraphRAG (Structural Search)**: Powered by `NetworkX` and Python `AST` (Abstract Syntax Trees), it maps the structural dependencies of the codebase (e.g., "Function A calls Function B"), allowing the agent to understand downstream impacts of its code changes.

---

## 5. Technology Stack & Packages

### Backend (Python Orchestration)
| Technology / Package | Purpose |
|----------------------|---------|
| **Python 3.13** | Core language environment. |
| **LangGraph** | Orchestrates the cyclic multi-agent state machine. |
| **LangChain** | Provides the `@tool` wrappers and standardized LLM message interfaces. |
| **langchain-google-genai**| The API bridge to Google's Gemini models. |
| **Gemini 3.1 Flash Lite** | The underlying LLM powering the agents (specifically `gemini-3.1-flash-lite-preview`). |
| **FastAPI & Uvicorn** | Serves the WebSocket endpoint `/ws/chat` for frontend communication. |
| **ChromaDB** | Local vector database for semantic RAG storage. |
| **NetworkX** | Mathematical graph library used to build the AST GraphRAG. |
| **LangSmith** | Full-stack observability and prompt tracing (via environment variables). |

### Frontend (React UI)
| Technology / Package | Purpose |
|----------------------|---------|
| **React 18 & Vite** | Core frontend framework and build tool for blazing-fast HMR. |
| **@monaco-editor/react**| Microsoft's code editor ported to the browser for syntax highlighting. |
| **reactflow** | Visualizes the LangGraph state machine dynamically. |
| **lucide-react** | Premium SVG iconography. |
| **Vanilla CSS** | Custom-built dark mode styling matching VS Code's exact aesthetic without heavy CSS frameworks. |

---

## 6. Future Roadmap
- **Dockerized Sandboxing**: Move the `execute_python_code` tool from a local subprocess to an ephemeral Docker container for total security.
- **Human-in-the-Loop**: Introduce a pause state in LangGraph where the user must click "Approve" in the React UI before the Tester Agent executes potentially dangerous code.
- **Multi-File Context Streaming**: Update the Monaco editor to support a file-tree sidebar, allowing the user to click between multiple files generated by the Coder Agent.
