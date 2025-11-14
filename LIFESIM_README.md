# LifeSim: Financial Independence Quest

A narrative, choice-based life simulator game where young people make financial decisions and see long-term consequences. Built with React for the Junction 2025 Hackathon.

## 🎮 Game Overview

LifeSim is an educational game that teaches financial literacy through interactive storytelling. Players make real-life financial decisions like:
- Managing their first paycheck
- Choosing transportation options (bike, car, public transport)
- Deciding on housing (living at home vs. renting)
- Balancing social life with savings
- Learning about investment strategies

### Key Features

- **6 Core Metrics**: Money, FI Score, Energy, Motivation, Social Life, and Financial Knowledge
- **Visual Assets**: Character avatars, backgrounds, and game items (vehicles, houses)
- **Dynamic Scenarios**: 5+ different scenarios with multiple choice options
- **Consequence System**: Every choice affects multiple metrics
- **Asset Tracking**: Players accumulate assets like bikes, cars, and apartments
- **Decision History**: Track recent choices and their outcomes

## 📁 Project Structure

```
frontend/
├── public/
│   └── images/
│       ├── backgrounds/         # Scene backgrounds
│       ├── characters/          # Player avatars
│       └── game/               # Assets (vehicles, houses)
├── src/
│   ├── api/
│   │   └── lifesim.js          # API helper with mock data
│   ├── components/
│   │   ├── TopBar.js           # Navigation and quick stats
│   │   ├── MetricsBar.js       # Metrics display
│   │   ├── SceneView.js        # Visual game scene
│   │   ├── ChoiceList.js       # Choice buttons and narrative
│   │   └── StatsDrawer.js      # Detailed stats panel
│   ├── context/
│   │   └── GameContext.js      # Global game state management
│   ├── routes/
│   │   ├── LoginPage.js        # Game start/login
│   │   ├── GamePage.js         # Main gameplay
│   │   └── SettingsPage.js     # Game settings
│   ├── App.js                  # Main app router
│   └── index.js                # Entry point
```

## 🚀 Getting Started

### Prerequisites

- Node.js 14+ installed
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Running the Game

```bash
npm start
```

The game will open at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

## 🎯 Game Flow

1. **Login/Start Page** (`/`)
   - Enter player name
   - Choose starting avatar
   - Begin the game

2. **Game Page** (`/game`)
   - Main gameplay interface
   - View narrative scenarios
   - Make choices that affect metrics
   - Track progress over time

3. **Stats Drawer** (accessible from game page)
   - View detailed metrics
   - See acquired assets
   - Review recent decisions

4. **Settings Page** (`/settings`)
   - Toggle sound effects
   - Change theme (Light/Dark/High Contrast)
   - Select language
   - Reset game progress

## 🎨 Available Assets

### Character Avatars
- `avatar_girl_middle_school.png`
- `avatar_boy_middle_school.png`
- `avatar_girl_highschool-removebg-preview.png`
- `avatar_boy_highschool.png`
- `avatar_adult_female.png`
- `avatar_adult_male.png`
- `avatar_senior_female.png`
- `avatar_senior_male.png`

### Backgrounds
- `sunny_background.png`
- `rainy_background.png`
- `sunset_background.png`
- `cloudy_background.png`
- `indoor_background.png`

### Game Assets
- Vehicles: `vehicle_bike_old.png`, `vehicle_bike_new.png`, `vehicle_car_old.png`, `vehicle_car_new.png`, `vehicle_car_super.png`
- Houses: `house_old_detached.png`, `house_standard_detached.png`, `house_mansion.png`, `house_apartment_block.png`

## 📊 Metrics System

### Money
- Tracks current cash and net worth
- Affected by income, spending, and investments
- No upper limit

### FI Score (Financial Independence Score)
- Range: 0-100%
- Measures progress toward financial independence
- Increases with good financial decisions

### Energy
- Range: 0-100
- Represents physical and mental stamina
- Affected by lifestyle choices

### Motivation
- Range: 0-100
- Player's drive and ambition
- Important for long-term success

### Social Life
- Range: 0-100
- Quality of relationships and social connections
- Balances against financial focus

### Financial Knowledge
- Range: 0-100
- Understanding of financial concepts
- Unlocks better decision-making

## 🔧 API Structure

The game uses a mock API (`src/api/lifesim.js`) with these main functions:

### `login(name, avatarKey)`
Start a new game session with player name and avatar.

### `submitChoice(choiceId)`
Submit a player's choice and receive updated game state.

### `getPlayerState()`
Get current player state including metrics and scenario.

### `updateSettings(settings)`
Save game settings to localStorage.

### `getSettings()`
Retrieve saved settings.

### `resetGame()`
Reset all game progress.

## 🎮 Game Scenarios

The game includes 5 main scenarios:

1. **First Paycheck** - Learning to balance saving vs. spending
2. **Transportation Decision** - Evaluating cost vs. convenience
3. **Housing Independence** - Understanding living costs
4. **Social Expenses** - Managing FOMO and budgeting
5. **Investment Strategy** - Introduction to wealth building

Each scenario has 4 different choice options with varying consequences.

## 🎨 Customization

### Adding New Scenarios

Edit `src/api/lifesim.js` and add to the `MOCK_SCENARIOS` array:

```javascript
{
  narrative: "Your scenario description...",
  choices: [
    { 
      id: "choice_id", 
      label: "Choice text", 
      description: "Consequence hint" 
    },
    // ... more choices
  ]
}
```

### Modifying Metrics Effects

Update the `applyChoiceEffects()` function in `src/api/lifesim.js`:

```javascript
choice_id: { 
  money: 100, 
  fiScore: 5, 
  energy: -10,
  motivation: 5,
  social: 0,
  knowledge: 3
}
```

## 🌐 Backend Integration

Currently using mock data. To connect to a real backend:

1. Replace mock functions in `src/api/lifesim.js` with actual API calls
2. Update endpoints to match your backend
3. Ensure CORS is properly configured
4. Keep the same data structure for compatibility

Example real API call:
```javascript
export async function login(name, avatarKey) {
  const response = await fetch('http://your-backend/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, avatarKey })
  });
  return await response.json();
}
```

## 🎨 Theming

The game supports three themes:
- **Light** - Default bright theme
- **Dark** - Dark mode for low-light environments
- **High Contrast** - Enhanced contrast for accessibility

Themes are applied via CSS classes on the `<body>` element.

## 📱 Responsive Design

The game is optimized for:
- Desktop (1920x1080 and above)
- Tablet (768px - 1024px)
- Mobile (up to 768px)

Key breakpoints are at 768px and 1024px.

## 🚧 Future Enhancements

Potential additions:
- [ ] Sound effects and background music
- [ ] More scenarios (20+ total)
- [ ] Multiplayer comparison mode
- [ ] Achievement system
- [ ] Save/load game progress to backend
- [ ] Localization (Finnish, Swedish)
- [ ] Tutorial mode for first-time players
- [ ] Advanced metrics (credit score, investment portfolio)
- [ ] Mini-games for financial concepts

## 🐛 Known Issues

- None currently! 🎉

## 📝 License

Built for Junction 2025 Hackathon

## 👥 Credits

- Game Design: Junction 2025 Team
- Development: AI-Assisted Development
- Assets: Custom game graphics

## 🆘 Support

For issues or questions, please check:
1. This README
2. Code comments in source files
3. Browser console for errors

---

**Enjoy playing LifeSim and learning about financial independence!** 🎮💰📈

