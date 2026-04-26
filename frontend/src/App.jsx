import React, { useState, useEffect } from 'react';
import './App.css';
import ChatPanel from './components/ChatPanel';
import CodeEditor from './components/Editor';
import AgentMind from './components/AgentMind';
import FileExplorer from './components/FileExplorer';
import UploadZone from './components/UploadZone';

function App() {
  const [socket, setSocket] = useState(null);
  const [state, setState] = useState({
    status: 'idle',
    plan: [],
    code_artifacts: {},
    test_results: '',
    errors: [],
    thought: ''
  });
  const [messages, setMessages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [ollamaModel, setOllamaModel] = useState('llama3:8b');

  useEffect(() => {
    // Fetch initial config
    fetch('http://localhost:8000/api/config')
      .then(res => res.json())
      .then(data => {
        setLlmProvider(data.llm_provider);
        setOllamaModel(data.ollama_model);
      })
      .catch(err => console.error("Failed to fetch config", err));

    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/chat');
      ws.onopen = () => { setSocket(ws); setWsConnected(true); };
      ws.onclose = () => { setWsConnected(false); setTimeout(connect, 3000); };
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'state_update') {
          setState(msg.data);
        } else if (msg.type === 'status') {
          setState(prev => ({ ...prev, status: msg.data }));
        } else if (msg.type === 'error') {
          setMessages(prev => [...prev, { role: 'system', content: `Error: ${msg.data}` }]);
        } else if (msg.type === 'completed') {
          setState(prev => ({ ...prev, status: 'completed' }));
          setMessages(prev => [...prev, { role: 'system', content: '✓ Task completed.' }]);
        }
      };
      return ws;
    };
    const ws = connect();
    return () => ws.close();
  }, []);

  const handleSendTask = (task) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'user', content: task }]);
      socket.send(JSON.stringify({ task }));
    }
  };

  const handleSelectFile = (path, name) => {
    setSelectedFile({ path, name });
  };

  const handleUploadSuccess = (data) => {
    setMessages(prev => [...prev, { role: 'system', content: `📁 Project uploaded: ${data.message}` }]);
  };

  const toggleLLM = async () => {
    const nextProvider = llmProvider === 'gemini' ? 'ollama' : 'gemini';
    try {
      const res = await fetch('http://localhost:8000/api/config/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: nextProvider })
      });
      if (res.ok) {
        setLlmProvider(nextProvider);
        setMessages(prev => [...prev, { role: 'system', content: `LLM switched to ${nextProvider === 'gemini' ? 'Online (Gemini)' : 'Local (Ollama)'}` }]);
      }
    } catch (err) {
      console.error("Failed to toggle LLM", err);
    }
  };

  const handleModelChange = async (e) => {
    if (e.key === 'Enter') {
      try {
        const res = await fetch('http://localhost:8000/api/config/llm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: 'ollama', model: ollamaModel })
        });
        if (res.ok) {
          setMessages(prev => [...prev, { role: 'system', content: `Ollama model set to ${ollamaModel}` }]);
          e.target.blur();
        }
      } catch (err) {
        console.error("Failed to update model", err);
      }
    }
  };

  const testResultLines = (state.test_results || '').split('\n');

  return (
    <div className="app-container">
      {/* Left Panel: File Explorer + Upload */}
      <div className="left-panel">
        <UploadZone onUploadSuccess={handleUploadSuccess} />
        <FileExplorer
          onSelectFile={handleSelectFile}
          selectedPath={selectedFile?.path}
          agentFiles={state.code_artifacts}
        />
      </div>

      {/* Center: Editor (takes most space) */}
      <div className="center-panel">
        <div className="panel-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flex: 1 }}>
            <span>EDITOR</span>
            <div className="llm-switch" onClick={toggleLLM}>
              <span className={`switch-label ${llmProvider === 'gemini' ? 'active' : ''}`}>ONLINE</span>
              <div className={`switch-track ${llmProvider === 'ollama' ? 'local' : ''}`}>
                <div className="switch-thumb" />
              </div>
              <span className={`switch-label ${llmProvider === 'ollama' ? 'active' : ''}`}>LOCAL</span>
            </div>
            {llmProvider === 'ollama' && (
              <div className="model-input-container">
                <input
                  className="model-name-input"
                  value={ollamaModel}
                  onChange={(e) => setOllamaModel(e.target.value)}
                  onKeyDown={handleModelChange}
                  placeholder="model name..."
                />
              </div>
            )}
          </div>
          <span className={`conn-badge ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '⬤ LIVE' : '⬤ OFFLINE'}
          </span>
        </div>
        <div className="editor-area">
          <CodeEditor
            selectedFile={selectedFile}
            agentFiles={state.code_artifacts}
          />
        </div>
      </div>

      {/* Right Panel: Chat + Mind + Terminal */}
      <div className="right-panel">
        <div className="chat-section">
          <div className="panel-header">AGENT CHAT</div>
          <ChatPanel
            onSend={handleSendTask}
            messages={messages}
            status={state.status}
            plan={state.plan}
          />
        </div>

        <div className="mind-section">
          <div className="panel-header">AGENT MIND</div>
          <AgentMind status={state.status} plan={state.plan} thought={state.thought} />
        </div>

        <div className="terminal-section">
          <div className="panel-header">
            TERMINAL / TEST RESULTS
            {state.status === 'testing' && <span className="blink-dot">●</span>}
          </div>
          <div className="test-results">
            {state.test_results ? (
              testResultLines.map((line, i) => (
                <div
                  key={i}
                  className={`terminal-line ${line.includes('Error') || line.includes('Traceback') ? 'error-line' : ''} ${line.includes('EXIT CODE: 0') ? 'success-line' : ''}`}
                >
                  {line}
                </div>
              ))
            ) : (
              <span className="waiting-text">{'>'} Waiting for execution...</span>
            )}
            {state.errors?.length > 0 && (
              <div className="terminal-errors">
                {state.errors.join('\n')}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
