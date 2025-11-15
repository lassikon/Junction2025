import React from "react";
import "../styles/SceneView.css";

/**
 * SceneView - Main visual display with FI score, life metrics, and assets
 * Acts as the "scene" with character progression
 */
const SceneView = ({ gameState, onMakeDecision, isCompact = false, showOnlyBottom = false }) => {
  const {
    current_step = 0,
    current_age = 25,
    years_passed = 0,
    fi_score = 0,
    energy = 0,
    motivation = 0,
    social_life = 0,
    financial_knowledge = 0,
    assets = {},
    game_status = "active"
  } = gameState;

  // Determine character image based on age
  const getCharacterImage = (age) => {
    if (age < 14) return "/images/characters/avatar_girl_middle_school.png";
    if (age < 18) return "/images/characters/avatar_boy_highschool.png";
    if (age < 60) return "/images/characters/avatar_adult_male.png";
    return "/images/characters/avatar_senior_male.png";
  };

  // Determine house image based on assets
  const getHouseImage = (assets) => {
    if (!assets.housing) return null;
    const houseType = assets.housing.type || assets.housing;
    if (houseType === "mansion") return "/images/game/house_mansion.png";
    if (houseType === "detached" || houseType === "house") return "/images/game/house_standard_detached.png";
    if (houseType === "old") return "/images/game/house_old_detached.png";
    return "/images/game/house_apartment_block.png";
  };

  // Determine vehicle image based on assets
  const getVehicleImage = (assets) => {
    if (!assets.car && !assets.vehicle) return null;
    const vehicle = assets.car || assets.vehicle;
    const type = typeof vehicle === 'object' ? vehicle.type : vehicle;
    
    if (type?.includes("super") || type === "super_car") return "/images/game/vehicle_car_super.png";
    if (type?.includes("new") && type?.includes("car")) return "/images/game/vehicle_car_new.png";
    if (type?.includes("old") || type?.includes("used")) return "/images/game/vehicle_car_old.png";
    if (type?.includes("bike") && type?.includes("new")) return "/images/game/vehicle_bike_new.png";
    if (type?.includes("bike")) return "/images/game/vehicle_bike_old.png";
    return "/images/game/vehicle_car_old.png"; // default car
  };

  // Background based on FI score and mood
  const getBackground = (fiScore, energy, motivation) => {
    const avgMood = (energy + motivation) / 2;
    
    if (fiScore >= 80 && avgMood >= 70) return "/images/backgrounds/sunset_background.png";
    if (fiScore >= 60 || avgMood >= 70) return "/images/backgrounds/sunny_background.png";
    if (fiScore >= 40 && avgMood >= 50) return "/images/backgrounds/cloudy_background.png";
    if (avgMood < 40) return "/images/backgrounds/rainy_background.png";
    return "/images/backgrounds/cloudy_background.png";
  };

  const characterImg = getCharacterImage(current_age);
  const houseImg = getHouseImage(assets);
  const vehicleImg = getVehicleImage(assets);
  const backgroundImg = getBackground(fi_score, energy, motivation);

  const getStatusColor = (value) => {
    if (value >= 70) return "status-good";
    if (value >= 40) return "status-medium";
    return "status-low";
  };

  const getFIScoreColor = (score) => {
    if (score >= 80) return "fi-excellent";
    if (score >= 60) return "fi-good";
    if (score >= 40) return "fi-medium";
    return "fi-low";
  };

  if (isCompact) {
    return (
      <div className="scene-view compact">
        {/* FI Score - Central Focus */}
        <div className="fi-score-section">
          <div className="fi-score-card">
            <h2>Financial Independence Score</h2>
            <div className={`fi-score ${getFIScoreColor(fi_score)}`}>
              {fi_score.toFixed(1)}%
            </div>
            <p className="fi-score-description">
              {fi_score >= 100
                ? "🎉 You've achieved Financial Independence!"
                : `${(100 - fi_score).toFixed(0)}% to go until FI!`}
            </p>
            <div className="fi-progress-bar">
              <div
                className="fi-progress-fill"
                style={{ width: `${Math.min(fi_score, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (showOnlyBottom) {
    return (
      <div className="scene-view bottom-only" style={{backgroundImage: `url(${backgroundImg})`}}>
        {/* Age & Step Badges */}
        <div className="age-badge">👤 Age {current_age} • {years_passed.toFixed(1)} years</div>
        <div className="step-badge">Step {current_step}</div>

        {/* Visual Game Scene */}
        <div className="game-scene">
        {/* Character Avatar */}
        <div className="character-container">
          <img src={characterImg} alt="Character" className="character-img" />
        </div>

        {/* House (if owned) */}
        {houseImg && (
          <div className="house-container">
            <img src={houseImg} alt="House" className="house-img" />
          </div>
        )}

        {/* Vehicle (if owned) */}
        {vehicleImg && (
          <div className="vehicle-container">
            <img src={vehicleImg} alt="Vehicle" className="vehicle-img" />
          </div>
        )}
      </div>

      {/* Life Balance Metrics */}
      <div className="life-metrics-section">
        <h3>Life Balance</h3>
        <div className="life-metrics-grid">
          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">⚡</span>
              <span className="life-metric-label">Energy</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(energy)}`}
                style={{ width: `${energy}%` }}
              >
                <span className="life-metric-value">{energy}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">🎯</span>
              <span className="life-metric-label">Motivation</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(motivation)}`}
                style={{ width: `${motivation}%` }}
              >
                <span className="life-metric-value">{motivation}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">👥</span>
              <span className="life-metric-label">Social Life</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(social_life)}`}
                style={{ width: `${social_life}%` }}
              >
                <span className="life-metric-value">{social_life}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">📚</span>
              <span className="life-metric-label">Financial Knowledge</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(financial_knowledge)}`}
                style={{ width: `${financial_knowledge}%` }}
              >
                <span className="life-metric-value">{financial_knowledge}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Assets Display */}
      {assets && Object.keys(assets).length > 0 && (
        <div className="assets-section">
          <h3>📦 Your Assets</h3>
          <div className="assets-grid">
            {Object.entries(assets).map(([key, value]) => {
              // Get icon based on asset type
              const getAssetIcon = (key) => {
                if (key.includes('car') || key.includes('vehicle')) return '🚗';
                if (key.includes('house') || key.includes('housing')) return '🏠';
                if (key.includes('pet')) return '🐕';
                if (key.includes('bike')) return '🚲';
                return '📦';
              };

              // Format value nicely
              const formatValue = (value) => {
                if (typeof value === 'boolean') return value ? '✓ Owned' : '✗ Not owned';
                if (typeof value === 'object') {
                  const details = [];
                  if (value.type) details.push(`Type: ${value.type.replace(/_/g, ' ')}`);
                  if (value.value) details.push(`Value: €${value.value}`);
                  if (value.name) details.push(`Name: ${value.name}`);
                  return details.join(', ');
                }
                return value;
              };

              return (
                <div key={key} className="asset-card">
                  <div className="asset-icon">{getAssetIcon(key)}</div>
                  <div className="asset-info">
                    <div className="asset-name">{key.replace(/_/g, ' ').toUpperCase()}</div>
                    <div className="asset-details">{formatValue(value)}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Action Button */}
      {game_status === "active" && (
        <div className="action-section">
          <button className="btn-action" onClick={onMakeDecision}>
            Continue Your Journey →
          </button>
        </div>
      )}

      {game_status === "completed" && (
        <div className="completion-message">
          <h2>🎉 Congratulations!</h2>
          <p>You've completed your journey to financial independence!</p>
        </div>
      )}
    </div>
    );
  }

  return null;
};

export default SceneView;

