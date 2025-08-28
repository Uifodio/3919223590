import React from 'react';
import './BreadcrumbNav.css';

const BreadcrumbNav = ({ filePath, onNavigate }) => {
  if (!filePath) return null;

  const pathParts = filePath.split(/[/\\]/);
  const breadcrumbs = pathParts.map((part, index) => ({
    name: part,
    path: pathParts.slice(0, index + 1).join('/'),
    isLast: index === pathParts.length - 1
  }));

  const handleClick = (path) => {
    if (onNavigate) {
      onNavigate(path);
    }
  };

  return (
    <div className="breadcrumb-nav">
      {breadcrumbs.map((crumb, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="breadcrumb-separator">/</span>}
          <span
            className={`breadcrumb-item ${crumb.isLast ? 'active' : ''}`}
            onClick={() => !crumb.isLast && handleClick(crumb.path)}
            title={crumb.path}
          >
            {crumb.name}
          </span>
        </React.Fragment>
      ))}
    </div>
  );
};

export default BreadcrumbNav;