import json
import os
import zipfile
import shutil
import tempfile
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.graph import build_graph
from core.config import config
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

class WorkspaceConfig(BaseModel):
    path: str

class FileCreateRequest(BaseModel):
    path: str
    type: str # "file" or "directory"

class LLMConfigRequest(BaseModel):
    provider: str # "gemini" or "ollama"
    model: str = None # Optional model name

@app.get("/api/config")
async def get_config():
    from core.config import config
    return JSONResponse({
        "llm_provider": config.LLM_PROVIDER,
        "ollama_model": config.OLLAMA_MODEL
    })

@app.post("/api/config/llm")
async def set_llm_provider(req: LLMConfigRequest):
    from core.config import config
    if req.provider not in ["gemini", "ollama"]:
        raise HTTPException(status_code=400, detail="Provider must be 'gemini' or 'ollama'")
    
    config.LLM_PROVIDER = req.provider
    if req.model:
        config.OLLAMA_MODEL = req.model
        print(f"Ollama model switched to: {config.OLLAMA_MODEL}")
    
    config.save_state()
    print(f"LLM Provider switched to: {config.LLM_PROVIDER}")
    return JSONResponse({"message": f"LLM provider switched to {req.provider}"})

@app.post("/api/config/workspace")
async def set_workspace(req: WorkspaceConfig):
    new_path = os.path.abspath(req.path)
    if not os.path.exists(new_path):
        raise HTTPException(status_code=404, detail="Path does not exist.")
    config.PROJECT_ROOT = new_path
    
    # Re-index for RAG
    from rag.indexer import index_codebase
    index_codebase(config.PROJECT_ROOT)
    
    config.save_state()
    return JSONResponse({"message": f"Workspace root changed to {config.PROJECT_ROOT}", "root": os.path.basename(config.PROJECT_ROOT)})

@app.post("/api/files/create")
async def create_file(req: FileCreateRequest):
    safe_path = os.path.normpath(os.path.join(config.PROJECT_ROOT, req.path))
    if not safe_path.startswith(config.PROJECT_ROOT):
        raise HTTPException(status_code=403, detail="Access denied.")
    
    try:
        if req.type == "directory":
            os.makedirs(safe_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            with open(safe_path, "w") as f:
                f.write("")
        return JSONResponse({"message": f"Successfully created {req.type} at {req.path}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

IGNORE_DIRS = {".git", "venv", "__pycache__", "chroma_db", "node_modules", ".gemini", ".ruff_cache"}
IGNORE_FILES = {".DS_Store", "*.pyc", "link_lists.bin", "data_level0.bin", "header.bin", "length.bin"}

def build_file_tree(root_path: str, base_path: str) -> list:
    """Recursively build a file tree structure."""
    items = []
    try:
        entries = sorted(os.scandir(root_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        for entry in entries:
            if entry.name in IGNORE_DIRS:
                continue
            if entry.name.startswith('.') and entry.name not in ['.env', '.env.example', '.gitignore']:
                continue
            rel_path = os.path.relpath(entry.path, base_path)
            if entry.is_dir():
                children = build_file_tree(entry.path, base_path)
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "directory",
                    "children": children
                })
            else:
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "file",
                    "extension": Path(entry.name).suffix
                })
    except PermissionError:
        pass
    return items


@app.get("/api/files")
async def get_file_tree():
    """Return the full project file tree."""
    tree = build_file_tree(config.PROJECT_ROOT, config.PROJECT_ROOT)
    return JSONResponse({"tree": tree, "root": os.path.basename(config.PROJECT_ROOT)})


@app.get("/api/file")
async def get_file_content(path: str):
    """Return the content of a specific file."""
    # Sanitize path to prevent directory traversal
    safe_path = os.path.normpath(os.path.join(config.PROJECT_ROOT, path))
    if not safe_path.startswith(config.PROJECT_ROOT):
        raise HTTPException(status_code=403, detail="Access denied.")
    
    if not os.path.isfile(safe_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    # Check file size (max 500KB for display)
    if os.path.getsize(safe_path) > 500_000:
        return JSONResponse({"content": "# File too large to display (> 500KB)", "path": path})
    
    try:
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return JSONResponse({"content": content, "path": path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_project(file: UploadFile = File(...)):
    """Upload a zip file and extract it, then re-index for RAG."""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")
    
    upload_dir = os.path.join(config.PROJECT_ROOT, "uploaded_project")
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded zip
    tmp_zip = os.path.join(config.PROJECT_ROOT, "uploaded.zip")
    with open(tmp_zip, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extract zip
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        zf.extractall(upload_dir)
    
    os.remove(tmp_zip)
    
    # Re-index the uploaded project into RAG
    from rag.indexer import index_codebase
    index_codebase(upload_dir)
    
    # Return the new file tree
    tree = build_file_tree(upload_dir, upload_dir)
    return JSONResponse({
        "message": f"Project uploaded and indexed successfully.",
        "tree": tree,
        "root": file.filename.replace(".zip", "")
    })


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            task = payload.get("task", "")
            
            if not task:
                continue
                
            initial_state = {
                "messages": [("user", task)],
                "task_description": task,
                "plan": [],
                "current_step": 0,
                "code_artifacts": {},
                "test_results": "",
                "errors": [],
                "status": "planning",
                "retry_count": 0
            }
            
            await websocket.send_json({"type": "status", "data": "planning"})
            
            async for event in graph.astream(initial_state, stream_mode="values"):
                status = event.get("status", "")
                thought = event.get("thought", "Thinking...")
                await websocket.send_json({
                    "type": "state_update",
                    "data": {
                        "status": status,
                        "plan": event.get("plan", []),
                        "code_artifacts": event.get("code_artifacts", {}),
                        "test_results": event.get("test_results", ""),
                        "errors": event.get("errors", []),
                        "retry_count": event.get("retry_count", 0),
                        "thought": thought
                    }
                })
                # Yield control to allow websocket to flush
                await asyncio.sleep(0.1)
                
            await websocket.send_json({"type": "completed", "data": "Task finished."})
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket: {e}")
        try:
            await websocket.send_json({"type": "error", "data": str(e)})
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
