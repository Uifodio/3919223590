import React from 'react'
import './StatusBar.css'

const StatusBar: React.FC = () => {
  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-label">Status:</span>
        <span className="status-value">Ready</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Line:</span>
        <span className="status-value">1</span>
        <span className="status-label">Col:</span>
        <span className="status-value">1</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Encoding:</span>
        <span className="status-value">UTF-8</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Indent:</span>
        <span className="status-value">Spaces: 2</span>
      </div>
    </div>
  )
}

export default StatusBar