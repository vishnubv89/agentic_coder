import React, { useState, useEffect, useCallback } from 'react';
import {
  FolderOpen, Folder, FileCode, FileText, File,
  ChevronDown, ChevronRight, RefreshCw
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
  const [isOpen, setIsOpen] = useState(depth < 2);

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
        style={{ paddingLeft: `${8 + depth * 14}px` }}
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

  // Refresh tree whenever agent writes new files
  useEffect(() => {
    if (Object.keys(agentFiles).length > 0) {
      fetchTree();
    }
  }, [agentFiles, fetchTree]);

  return (
    <div className="file-explorer">
      <div className="explorer-header">
        <span>EXPLORER — {rootName.toUpperCase()}</span>
        <button
          className="refresh-btn"
          onClick={fetchTree}
          title="Refresh file tree"
        >
          <RefreshCw size={12} className={loading ? 'spinning' : ''} />
        </button>
      </div>
      <div className="tree-scroll">
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
