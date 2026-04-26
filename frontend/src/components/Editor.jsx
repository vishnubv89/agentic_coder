import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

const LANGUAGE_MAP = {
  '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
  '.ts': 'typescript', '.tsx': 'typescript',
  '.html': 'html', '.css': 'css', '.scss': 'scss',
  '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
  '.md': 'markdown', '.sh': 'shell', '.toml': 'toml',
};

function getLanguage(filename) {
  if (!filename) return 'plaintext';
  const ext = '.' + filename.split('.').pop().toLowerCase();
  return LANGUAGE_MAP[ext] || 'plaintext';
}

export default function CodeEditor({ selectedFile, agentFiles }) {
  const [content, setContent] = useState('// Select a file from the explorer or run an agent task...');
  const [activeFile, setActiveFile] = useState(null);
  const [tabs, setTabs] = useState([]);

  // When agent generates new files, open them as tabs automatically
  useEffect(() => {
    if (!agentFiles || Object.keys(agentFiles).length === 0) return;
    const newTabs = Object.keys(agentFiles);
    setTabs(prev => {
      const merged = [...new Set([...prev, ...newTabs])];
      return merged;
    });
    // Open the first agent file
    const firstFile = newTabs[0];
    setActiveFile(firstFile);
    setContent(agentFiles[firstFile]);
  }, [agentFiles]);

  // When user clicks a file in the explorer, fetch and display it
  useEffect(() => {
    if (!selectedFile) return;
    const { path, name } = selectedFile;

    // Check if agent generated this file
    if (agentFiles && agentFiles[name]) {
      setActiveFile(name);
      setContent(agentFiles[name]);
      setTabs(prev => [...new Set([...prev, name])]);
      return;
    }

    // Fetch from backend
    fetch(`http://localhost:8000/api/file?path=${encodeURIComponent(path)}`)
      .then(r => r.json())
      .then(data => {
        setContent(data.content || '');
        setActiveFile(path);
        setTabs(prev => [...new Set([...prev, path])]);
      })
      .catch(() => setContent('// Error loading file'));
  }, [selectedFile]);

  const switchTab = (tab) => {
    setActiveFile(tab);
    const name = tab.split('/').pop();
    if (agentFiles && agentFiles[name]) {
      setContent(agentFiles[name]);
    } else {
      fetch(`http://localhost:8000/api/file?path=${encodeURIComponent(tab)}`)
        .then(r => r.json())
        .then(data => setContent(data.content || ''))
        .catch(() => setContent('// Error loading file'));
    }
  };

  const closeTab = (e, tab) => {
    e.stopPropagation();
    const remaining = tabs.filter(t => t !== tab);
    setTabs(remaining);
    if (activeFile === tab) {
      setActiveFile(remaining[remaining.length - 1] || null);
    }
  };

  const displayName = activeFile ? activeFile.split('/').pop() : '—';
  const language = getLanguage(displayName);

  return (
    <div className="editor-wrapper">
      {tabs.length > 0 && (
        <div className="editor-tabs">
          {tabs.map(tab => {
            const label = tab.split('/').pop();
            return (
              <div
                key={tab}
                className={`editor-tab ${activeFile === tab ? 'active' : ''}`}
                onClick={() => switchTab(tab)}
              >
                <span>{label}</span>
                <button className="tab-close" onClick={(e) => closeTab(e, tab)}>×</button>
              </div>
            );
          })}
        </div>
      )}
      <div className="editor-body">
        <Editor
          height="100%"
          language={language}
          value={content}
          theme="vs-dark"
          options={{
            readOnly: false,
            fontSize: 13,
            minimap: { enabled: tabs.length > 0 },
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            lineNumbers: 'on',
            renderLineHighlight: 'all',
            smoothScrolling: true,
          }}
        />
      </div>
    </div>
  );
}
