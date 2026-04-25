import React, { useState } from 'react';
import { Send, TerminalSquare } from 'lucide-react';

const ChatPanel = ({ onSend, messages, status, plan }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-history">
        {messages.length === 0 && (
          <div className="chat-message system">
            Welcome to AgenticCoder. What would you like to build?
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You: ' : 'System: '}</strong>
            {msg.content}
          </div>
        ))}
        {plan && plan.length > 0 && (
          <div className="chat-message system" style={{fontSize: '11px', color: '#a0a0a0'}}>
            <strong>Current Plan:</strong>
            <ul style={{margin: '5px 0', paddingLeft: '15px'}}>
              {plan.map((step, i) => <li key={i}>{step}</li>)}
            </ul>
          </div>
        )}
      </div>
      
      <div style={{display: 'flex', flexDirection: 'column'}}>
        <div style={{fontSize: '10px', color: '#888', marginBottom: '5px', textTransform: 'uppercase'}}>
          <TerminalSquare size={10} style={{marginRight: '5px', display: 'inline'}} />
          Status: <span style={{color: status === 'idle' || status === 'completed' ? '#4caf50' : '#ffa500'}}>{status}</span>
        </div>
        <textarea 
          className="input-box" 
          placeholder="Ask AgenticCoder to write some code..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button className="send-btn" onClick={handleSend}>
          <Send size={14} style={{verticalAlign: 'middle', marginRight: '5px'}}/> SEND TASK
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
