import React from 'react';
import Editor from '@monaco-editor/react';

const CodeEditor = ({ code, language = 'python' }) => {
  return (
    <div className="editor-container">
      <Editor
        height="100%"
        defaultLanguage={language}
        theme="vs-dark"
        value={code}
        options={{
          minimap: { enabled: false },
          fontSize: 13,
          wordWrap: 'on',
          readOnly: true,
          padding: { top: 15 },
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
};

export default CodeEditor;
