import React from "react";
import "../styles/LifeMetricsChanges.css";

/**
 * LifeMetricsChanges - Shows changes in life metrics from a decision
 */
const LifeMetricsChanges = ({ changes }) => {
  if (!changes) return null;

  const hasChanges = changes.energy_change !== 0 || 
                     changes.motivation_change !== 0 || 
                     changes.social_change !== 0 || 
                     changes.knowledge_change !== 0;

  if (!hasChanges) return null;

  const formatChange = (value) => {
    if (value === 0) return null;
    return value > 0 ? `+${value}` : `${value}`;
  };

  const getChangeClass = (value) => {
    if (value > 0) return "positive";
    if (value < 0) return "negative";
    return "neutral";
  };

  const metrics = [
    { label: "⚡ Energy", value: changes.energy_change, icon: "⚡" },
    { label: "🎯 Motivation", value: changes.motivation_change, icon: "🎯" },
    { label: "👥 Social Life", value: changes.social_change, icon: "👥" },
    { label: "📚 Financial Knowledge", value: changes.knowledge_change, icon: "📚" }
  ];

  return (
    <div className="life-metrics-changes">
      <h4 className="metrics-title">📈 Life Balance Changes</h4>
      <div className="metrics-grid">
        {metrics.map((metric, index) => {
          const change = formatChange(metric.value);
          if (!change) return null;
          
          return (
            <div key={index} className="metric-change-item">
              <span className="metric-icon">{metric.icon}</span>
              <span className="metric-label">{metric.label.replace(/[⚡🎯👥📚]\s/, '')}</span>
              <span className={`metric-value ${getChangeClass(metric.value)}`}>
                {change}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LifeMetricsChanges;
