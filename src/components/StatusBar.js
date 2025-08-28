import React from 'react';
import './StatusBar.css';

const StatusBar = ({ line, column, totalLines }) => {
  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-label">Line:</span>
        <span className="status-value">{line}</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Col:</span>
        <span className="status-value">{column}</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Total:</span>
        <span className="status-value">{totalLines}</span>
      </div>
      
      <div className="status-spacer" />
      
      <div className="status-item">
        <span className="status-text">Nexus Editor - Professional Code Editor</span>
      </div>
    </div>
  );
};

export default StatusBar;