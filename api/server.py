import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from core.graph import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

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
                "status": "planning"
            }
            
            await websocket.send_json({"type": "status", "data": "planning"})
            
            # Stream the graph execution
            for event in graph.stream(initial_state, stream_mode="values"):
                status = event.get("status", "")
                
                # Sanitize messages if any to avoid serialization issues, but we don't send messages
                await websocket.send_json({
                    "type": "state_update",
                    "data": {
                        "status": status,
                        "plan": event.get("plan", []),
                        "code_artifacts": event.get("code_artifacts", {}),
                        "test_results": event.get("test_results", ""),
                        "errors": event.get("errors", [])
                    }
                })
                
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
