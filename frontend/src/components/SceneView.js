import React from 'react';
import './SceneView.css';

function SceneView({ background, character, assets = [] }) {
  // Map of available backgrounds
  const backgrounds = {
    sunny: '/images/backgrounds/sunny_background.png',
    rainy: '/images/backgrounds/rainy_background.png',
    sunset: '/images/backgrounds/sunset_background.png',
    indoor: '/images/backgrounds/indoor_background.png',
    cloudy: '/images/backgrounds/cloudy_background.png'
  };

  const backgroundImage = backgrounds[background] || backgrounds.sunny;
  const characterImage = character ? `/images/characters/${character}` : null;

  return (
    <div className="scene-view">
      <div 
        className="scene-background"
        style={{ backgroundImage: `url(${backgroundImage})` }}
      >
        <div className="scene-content">
          {/* Assets (vehicles, houses) */}
          {assets && assets.length > 0 && (
            <div className="scene-assets">
              {assets.slice(0, 2).map((asset, index) => (
                <img
                  key={index}
                  src={`/images/game/${asset.image}`}
                  alt={asset.name}
                  className="scene-asset"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              ))}
            </div>
          )}
          
          {/* Character */}
          {characterImage && (
            <div className="scene-character-container">
              <img
                src={characterImage}
                alt="Character"
                className="scene-character"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SceneView;

