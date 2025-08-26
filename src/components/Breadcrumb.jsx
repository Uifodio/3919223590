import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '../utils/cn';

const Breadcrumb = ({ currentPath, onPathClick }) => {
  const pathParts = currentPath.split('/').filter(part => part.length > 0);
  
  const handlePathClick = (index) => {
    const path = '/' + pathParts.slice(0, index + 1).join('/');
    onPathClick(path);
  };

  const copyPath = () => {
    navigator.clipboard.writeText(currentPath);
  };

  return (
    <div className="breadcrumb p-2 border-b border-border bg-card">
      <div className="flex items-center gap-1 flex-1 min-w-0">
        <button
          className="breadcrumb-item p-1 hover:bg-accent rounded"
          onClick={() => onPathClick('/')}
          title="Home"
        >
          <Home className="w-4 h-4" />
        </button>
        
        {pathParts.map((part, index) => (
          <React.Fragment key={index}>
            <ChevronRight className="breadcrumb-separator w-4 h-4" />
            <button
              className="breadcrumb-item px-2 py-1 hover:bg-accent rounded truncate"
              onClick={() => handlePathClick(index)}
              title={part}
            >
              {part}
            </button>
          </React.Fragment>
        ))}
      </div>
      
      <button
        className="text-xs text-muted-foreground hover:text-foreground px-2 py-1 hover:bg-accent rounded"
        onClick={copyPath}
        title="Copy path"
      >
        Copy Path
      </button>
    </div>
  );
};

export default Breadcrumb;