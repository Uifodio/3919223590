import React, { useRef, useEffect, useState } from 'react';
import './MiniMap.css';

const MiniMap = ({ content, onScrollToLine, visibleRange }) => {
  const canvasRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartY, setDragStartY] = useState(0);

  // Render mini-map
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !content) return;

    const ctx = canvas.getContext('2d');
    const lines = content.split('\n');
    const totalLines = lines.length;
    
    // Set canvas dimensions
    canvas.width = 120;
    canvas.height = Math.min(200, totalLines * 2);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background
    ctx.fillStyle = '#2d2d30';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw code representation
    ctx.fillStyle = '#4d4d4d';
    lines.forEach((line, index) => {
      const y = (index / totalLines) * canvas.height;
      const height = Math.max(1, canvas.height / totalLines);
      
      // Simple representation: longer lines get darker
      const intensity = Math.min(255, Math.max(50, line.length * 2));
      ctx.fillStyle = `rgb(${intensity}, ${intensity}, ${intensity})`;
      
      ctx.fillRect(0, y, canvas.width, height);
    });
    
    // Draw visible range indicator
    if (visibleRange) {
      const { start, end } = visibleRange;
      const startY = (start / totalLines) * canvas.height;
      const endY = (end / totalLines) * canvas.height;
      const height = endY - startY;
      
      ctx.fillStyle = 'rgba(0, 122, 204, 0.3)';
      ctx.fillRect(0, startY, canvas.width, height);
      
      ctx.strokeStyle = '#007acc';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, startY, canvas.width, height);
    }
  }, [content, visibleRange]);

  // Handle mouse events for navigation
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStartY(e.clientY);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const lines = content.split('\n');
    const totalLines = lines.length;
    
    const lineNumber = Math.floor((y / canvas.height) * totalLines) + 1;
    onScrollToLine(Math.max(1, Math.min(totalLines, lineNumber)));
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const lines = content.split('\n');
    const totalLines = lines.length;
    
    const lineNumber = Math.floor((y / canvas.height) * totalLines) + 1;
    onScrollToLine(Math.max(1, Math.min(totalLines, lineNumber)));
  };

  if (!content) return null;

  return (
    <div className="mini-map">
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onClick={handleClick}
        className="mini-map-canvas"
        title="Click or drag to navigate"
      />
    </div>
  );
};

export default MiniMap;