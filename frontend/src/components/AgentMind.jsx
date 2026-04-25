import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';

const AgentMind = ({ status }) => {
  const nodes = useMemo(() => [
    { 
      id: 'planner', 
      position: { x: 50, y: 50 }, 
      data: { label: '🧠 Planner' },
      className: status === 'planning' ? 'active' : ''
    },
    { 
      id: 'coder', 
      position: { x: 250, y: 50 }, 
      data: { label: '💻 Coder' },
      className: status === 'coding' ? 'active' : ''
    },
    { 
      id: 'tester', 
      position: { x: 450, y: 50 }, 
      data: { label: '🧪 Tester' },
      className: status === 'testing' ? 'active' : ''
    },
    { 
      id: 'done', 
      position: { x: 450, y: 150 }, 
      data: { label: '✅ Done' },
      className: status === 'completed' ? 'active' : ''
    }
  ], [status]);

  const edges = useMemo(() => [
    { id: 'e1-2', source: 'planner', target: 'coder', animated: status === 'planning' },
    { id: 'e2-3', source: 'coder', target: 'tester', animated: status === 'coding' },
    { id: 'e3-4', source: 'tester', target: 'done', animated: status === 'testing' },
    { id: 'e3-2', source: 'tester', target: 'coder', type: 'step', label: 'Fail', animated: status === 'failed' }
  ], [status]);

  return (
    <div className="mind-container">
      <ReactFlow nodes={nodes} edges={edges} fitView attributionPosition="bottom-left">
        <Background color="#333" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default AgentMind;
