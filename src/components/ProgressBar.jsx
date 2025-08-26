import React from 'react';
import { X, CheckCircle, AlertCircle } from 'lucide-react';

const ProgressBar = ({ operation, progress, onClose, error }) => {
  const getOperationText = (op) => {
    switch (op) {
      case 'copy': return 'Copying files...';
      case 'move': return 'Moving files...';
      case 'delete': return 'Deleting files...';
      case 'createDirectory': return 'Creating directory...';
      case 'createFile': return 'Creating file...';
      default: return 'Processing...';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 w-80 bg-card border border-border rounded-lg shadow-lg p-4 z-50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {error ? (
            <AlertCircle className="w-4 h-4 text-destructive" />
          ) : progress === 100 ? (
            <CheckCircle className="w-4 h-4 text-green-500" />
          ) : (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
          )}
          <span className="text-sm font-medium">
            {getOperationText(operation)}
          </span>
        </div>
        
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      
      <div className="progress-bar mb-2">
        <div
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{progress}%</span>
        {error && (
          <span className="text-destructive">{error}</span>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;