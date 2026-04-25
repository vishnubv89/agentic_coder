import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatPanel from './components/ChatPanel';
import CodeEditor from './components/Editor';
import AgentMind from './components/AgentMind';

function App() {
  const [socket, setSocket] = useState(null);
  const [state, setState] = useState({
    status: 'idle',
    plan: [],
    code_artifacts: {},
    test_results: '',
    errors: []
  });
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/chat');
    
    ws.onopen = () => {
      console.log('Connected to backend');
      setSocket(ws);
    };
    
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
        setMessages(prev => [...prev, { role: 'system', content: msg.data }]);
      }
    };
    
    return () => {
      ws.close();
    };
  }, []);

  const handleSendTask = (task) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'user', content: task }]);
      socket.send(JSON.stringify({ task }));
    }
  };

  // Get the first file content to display
  const currentFile = Object.keys(state.code_artifacts || {})[0] || 'main.py';
  const currentCode = state.code_artifacts?.[currentFile] || '# Waiting for agent to write code...';

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="panel-header">AGENT CHAT</div>
        <ChatPanel 
          onSend={handleSendTask} 
          messages={messages} 
          status={state.status} 
          plan={state.plan} 
        />
      </div>
      
      <div className="main-content">
        <div className="top-panel">
          <div className="panel-header">EXPLORER & EDITOR ({currentFile})</div>
          <CodeEditor code={currentCode} language="python" />
        </div>
        
        <div className="bottom-panel" style={{display: 'flex'}}>
          <div style={{flex: 1, borderRight: '1px solid var(--border-color)'}}>
            <div className="panel-header">AGENT MIND GRAPH</div>
            <AgentMind status={state.status} />
          </div>
          <div style={{flex: 1}}>
            <div className="panel-header">TERMINAL / TEST RESULTS</div>
            <div className="test-results">
              {state.test_results ? state.test_results : '> Waiting for execution...'}
              {state.errors && state.errors.length > 0 && (
                <div style={{color: '#f48771', marginTop: '10px'}}>
                  {state.errors.join('\n')}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
