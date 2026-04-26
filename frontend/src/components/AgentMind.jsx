import React from 'react';
import { 
  Search, Code, Activity, CheckCircle, AlertCircle, 
  Cpu, Zap, Target 
} from 'lucide-react';

const AgentMind = ({ status, plan }) => {
  const steps = [
    { id: 'planning', label: 'PLANNING', icon: <Search size={16} />, color: '#00d2ff' },
    { id: 'coding', label: 'CODING', icon: <Code size={16} />, color: '#7f00ff' },
    { id: 'testing', label: 'TESTING', icon: <Activity size={16} />, color: '#ff0055' },
    { id: 'completed', label: 'FINISHED', icon: <CheckCircle size={16} />, color: '#39ff14' },
  ];

  const getStepStatus = (stepId) => {
    const statusMap = {
      'planning': 0,
      'coding': 1,
      'testing': 2,
      'completed': 3,
      'idle': -1
    };
    
    const currentIdx = statusMap[status] ?? -1;
    const stepIdx = statusMap[stepId];
    
    if (currentIdx === stepIdx) return 'active';
    if (currentIdx > stepIdx) return 'done';
    return 'pending';
  };

  return (
    <div className="mind-container-v2">
      {/* Current Phase Indicator */}
      <div className="mind-phases">
        {steps.map((step, i) => {
          const s = getStepStatus(step.id);
          return (
            <div key={step.id} className={`mind-phase-item ${s}`}>
              <div className="phase-icon" style={{ borderColor: s !== 'pending' ? step.color : '#333' }}>
                {s === 'done' ? <CheckCircle size={16} style={{ color: '#39ff14' }} /> : step.icon}
                {s === 'active' && <div className="pulse-ring" style={{ backgroundColor: step.color }} />}
              </div>
              <div className="phase-label">{step.label}</div>
              {i < steps.length - 1 && <div className={`phase-line ${s === 'done' ? 'done' : ''}`} />}
            </div>
          );
        })}
      </div>

      {/* Execution Mindset */}
      <div className="mind-details">
        <div className="mind-details-header">
          <Target size={16} /> <span>EXECUTION PLAN</span>
        </div>
        <div className="mind-plan-list">
          {plan && plan.length > 0 ? (
            plan.map((p, i) => (
              <div key={i} className="mind-plan-step">
                <div className="step-num">{i + 1}</div>
                <div className="step-text">{p}</div>
              </div>
            ))
          ) : (
            <div className="mind-idle-text">Waiting for task analysis...</div>
          )}
        </div>
      </div>

      {/* Real-time Thought Stream */}
      <div className="thought-stream">
        <div className="stream-header">
          <Cpu size={16} /> <span>SYSTEM THOUGHTS</span>
        </div>
        <div className="stream-content">
          <div className="thought-item">
             <Zap size={14} className="zap-icon" />
             {status === 'planning' && "Reasoning about codebase architecture..."}
             {status === 'coding' && "Generating code artifacts and wiring modules..."}
             {status === 'testing' && "Verifying implementation in sandbox..."}
             {status === 'completed' && "All systems green. Deployment ready."}
             {status === 'idle' && "Standing by for instructions."}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentMind;
