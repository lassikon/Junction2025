import React from 'react';
import './MetricsBar.css';

function MetricsBar({ metrics }) {
  if (!metrics) return null;

  const metricsConfig = [
    { key: 'money', label: 'Money', color: '#10b981', format: (v) => `€${v.toLocaleString()}`, max: null },
    { key: 'fiScore', label: 'FI Score', color: '#3b82f6', format: (v) => `${v}%`, max: 100 },
    { key: 'energy', label: 'Energy', color: '#f59e0b', format: (v) => v, max: 100 },
    { key: 'motivation', label: 'Motivation', color: '#8b5cf6', format: (v) => v, max: 100 },
    { key: 'social', label: 'Social Life', color: '#ec4899', format: (v) => v, max: 100 },
    { key: 'knowledge', label: 'Financial Knowledge', color: '#06b6d4', format: (v) => v, max: 100 }
  ];

  return (
    <div className="metrics-bar">
      {metricsConfig.map(({ key, label, color, format, max }) => {
        const value = metrics[key] || 0;
        const percentage = max ? (value / max) * 100 : 100;
        
        return (
          <div key={key} className="metric-item">
            <div className="metric-header">
              <span className="metric-label">{label}</span>
              <span className="metric-value">{format(value)}</span>
            </div>
            {max && (
              <div className="metric-bar-container">
                <div 
                  className="metric-bar-fill" 
                  style={{ 
                    width: `${Math.min(percentage, 100)}%`,
                    backgroundColor: color
                  }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default MetricsBar;

