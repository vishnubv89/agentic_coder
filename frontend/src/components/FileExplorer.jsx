import React, { useState, useEffect, useCallback } from 'react';
import {
  FolderOpen, Folder, FileCode, FileText, File,
  ChevronDown, ChevronRight, RefreshCw, FilePlus, FolderPlus, Edit3
} from 'lucide-react';

const FILE_ICONS = {
  '.py': { icon: FileCode, color: '#3572A5' },
  '.js': { icon: FileCode, color: '#F7DF1E' },
  '.jsx': { icon: FileCode, color: '#61DAFB' },
  '.ts': { icon: FileCode, color: '#3178C6' },
  '.tsx': { icon: FileCode, color: '#61DAFB' },
  '.html': { icon: FileCode, color: '#E34C26' },
  '.css': { icon: FileCode, color: '#563D7C' },
  '.json': { icon: FileText, color: '#F1A642' },
  '.md': { icon: FileText, color: '#83a598' },
  '.sh': { icon: FileText, color: '#89e051' },
  '.env': { icon: FileText, color: '#ECD53F' },
};

function FileIcon({ name, extension }) {
  const config = FILE_ICONS[extension] || { icon: File, color: '#cccccc' };
  const Icon = config.icon;
  return <Icon size={14} color={config.color} style={{ flexShrink: 0 }} />;
}

function TreeNode({ node, depth, selectedPath, onSelectFile }) {
  const [isOpen, setIsOpen] = useState(depth < 1);

  const handleClick = () => {
    if (node.type === 'directory') {
      setIsOpen(prev => !prev);
    } else {
      onSelectFile(node.path, node.name);
    }
  };

  const isSelected = selectedPath === node.path;

  return (
    <div>
      <div
        className={`tree-node ${isSelected ? 'selected' : ''}`}
        style={{ paddingLeft: `${8 + depth * 12}px` }}
        onClick={handleClick}
        title={node.name}
      >
        {node.type === 'directory' ? (
          <>
            <span className="tree-arrow">
              {isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </span>
            {isOpen ? <FolderOpen size={14} color="#dcb67a" /> : <Folder size={14} color="#dcb67a" />}
          </>
        ) : (
          <>
            <span className="tree-arrow" />
            <FileIcon name={node.name} extension={node.extension} />
          </>
        )}
        <span className="tree-label">{node.name}</span>
      </div>

      {node.type === 'directory' && isOpen && node.children?.map((child, i) => (
        <TreeNode
          key={`${child.path}-${i}`}
          node={child}
          depth={depth + 1}
          selectedPath={selectedPath}
          onSelectFile={onSelectFile}
        />
      ))}
    </div>
  );
}

export default function FileExplorer({ onSelectFile, selectedPath, agentFiles = {} }) {
  const [tree, setTree] = useState([]);
  const [rootName, setRootName] = useState('PROJECT');
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(null); // 'file' or 'directory'
  const [newItemName, setNewItemName] = useState('');
  const [changingPath, setChangingPath] = useState(false);
  const [newPath, setNewPath] = useState('');

  const fetchTree = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/files');
      const data = await res.json();
      setTree(data.tree || []);
      setRootName(data.root || 'PROJECT');
    } catch (e) {
      console.error('Failed to fetch file tree:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTree();
  }, [fetchTree]);

  useEffect(() => {
    if (Object.keys(agentFiles).length > 0) {
      fetchTree();
    }
  }, [agentFiles, fetchTree]);

  const handleCreate = async (e) => {
    if (e.key === 'Enter' && newItemName) {
      try {
        const res = await fetch('http://localhost:8000/api/files/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: newItemName, type: creating })
        });
        if (res.ok) {
          setCreating(null);
          setNewItemName('');
          fetchTree();
        }
      } catch (e) {
        console.error('Failed to create item');
      }
    } else if (e.key === 'Escape') {
      setCreating(null);
    }
  };

  const handleChangeWorkspace = async (e) => {
    if (e.key === 'Enter' && newPath) {
      try {
        const res = await fetch('http://localhost:8000/api/config/workspace', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: newPath })
        });
        if (res.ok) {
          setChangingPath(false);
          setNewPath('');
          fetchTree();
        }
      } catch (e) {
        console.error('Failed to change workspace');
      }
    } else if (e.key === 'Escape') {
      setChangingPath(null);
    }
  };

  return (
    <div className="file-explorer">
      <div className="explorer-header">
        <div className="explorer-title">
          {changingPath ? (
            <input
              autoFocus
              className="path-input"
              value={newPath}
              placeholder="Absolute path..."
              onChange={(e) => setNewPath(e.target.value)}
              onKeyDown={handleChangeWorkspace}
              onBlur={() => setChangingPath(false)}
            />
          ) : (
            <span onClick={() => setChangingPath(true)} style={{cursor: 'pointer'}}>
              {rootName.toUpperCase()}
            </span>
          )}
        </div>
        <div className="explorer-actions">
          <button onClick={() => setCreating('file')} title="New File"><FilePlus size={14} /></button>
          <button onClick={() => setCreating('directory')} title="New Folder"><FolderPlus size={14} /></button>
          <button onClick={fetchTree} title="Refresh"><RefreshCw size={14} className={loading ? 'spinning' : ''} /></button>
        </div>
      </div>

      <div className="tree-scroll">
        {creating && (
          <div className="inline-input-container" style={{ paddingLeft: '20px' }}>
            {creating === 'file' ? <File size={14} /> : <Folder size={14} color="#dcb67a" />}
            <input
              autoFocus
              className="inline-input"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              onKeyDown={handleCreate}
              onBlur={() => setCreating(null)}
              placeholder={`New ${creating}...`}
            />
          </div>
        )}
        {tree.map((node, i) => (
          <TreeNode
            key={`${node.path}-${i}`}
            node={node}
            depth={0}
            selectedPath={selectedPath}
            onSelectFile={onSelectFile}
          />
        ))}
      </div>
    </div>
  );
}
