# LifeSim - Quick Start Guide

## 🚀 Running the Game

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to play!

## 🗺️ Navigation

- `/` - Login/Start page (choose name and avatar)
- `/game` - Main game page
- `/settings` - Settings page
- `/chat` - Original chat interface (preserved)
- `/old-home` - Original home page (preserved)

## 🎮 How to Play

1. **Start the Game**
   - Enter your name (or skip)
   - Select an avatar
   - Click "Start Game"

2. **Make Decisions**
   - Read the narrative scenario
   - Choose from 4 different options
   - Watch your metrics change
   - Progress through time (3 months per turn)

3. **View Stats**
   - Click "View Stats" button in top bar
   - See detailed metrics
   - Check your assets
   - Review recent decisions

4. **Adjust Settings**
   - Navigate to Settings page
   - Toggle sound effects and tooltips
   - Change theme (Light/Dark/High Contrast)
   - Reset game if needed

## 📊 Understanding Metrics

- **Money** - Your cash and net worth (no limit)
- **FI Score** - Financial Independence progress (0-100%)
- **Energy** - Physical and mental stamina (0-100)
- **Motivation** - Drive and ambition (0-100)
- **Social Life** - Quality of relationships (0-100)
- **Financial Knowledge** - Understanding of finances (0-100)

## 🎯 Tips for Good Gameplay

1. **Balance is Key** - Don't just maximize money; all metrics matter
2. **Read Descriptions** - Choice descriptions hint at consequences
3. **Track Your Progress** - Check stats drawer regularly
4. **Think Long-term** - Some choices have delayed benefits
5. **Learn from Decisions** - Review your decision history

## 🛠️ Development

### File Structure

```
src/
├── api/lifesim.js          # Mock API with game logic
├── context/GameContext.js  # Global state management
├── components/             # Reusable UI components
│   ├── TopBar.js
│   ├── MetricsBar.js
│   ├── SceneView.js
│   ├── ChoiceList.js
│   └── StatsDrawer.js
└── routes/                 # Main pages
    ├── LoginPage.js
    ├── GamePage.js
    └── SettingsPage.js
```

### Adding New Scenarios

Edit `src/api/lifesim.js`:

```javascript
const MOCK_SCENARIOS = [
  // Add your scenario here
  {
    narrative: "Your scenario text...",
    choices: [
      { 
        id: "unique_id", 
        label: "Choice Title", 
        description: "What happens if you choose this" 
      },
      // ... 3-4 more choices
    ]
  }
];
```

### Modifying Choice Effects

In `src/api/lifesim.js`, update `applyChoiceEffects()`:

```javascript
const effects = {
  your_choice_id: { 
    money: 500,        // Add/subtract money
    fiScore: 5,        // Change FI score (-100 to +100)
    energy: -10,       // Modify energy
    motivation: 5,     // Affect motivation
    social: 0,         // Impact social life
    knowledge: 3       // Increase knowledge
  }
};
```

### Adding Assets

When a choice should give the player an asset:

```javascript
if (choiceId === 'buy_car') {
  mockPlayerState.assets.push({ 
    name: 'New Car', 
    image: 'vehicle_car_new.png' 
  });
}
```

## 🎨 Customization

### Changing Colors

Edit component CSS files to change the color scheme. Main colors:
- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (orange)

### Adding New Avatars

1. Add image to `public/images/characters/`
2. Update `AVAILABLE_AVATARS` in `LoginPage.js`

### Adding New Backgrounds

1. Add image to `public/images/backgrounds/`
2. Update `backgrounds` object in `SceneView.js`

## 🔧 Backend Integration (Future)

To connect to a real backend:

1. Replace functions in `src/api/lifesim.js` with fetch/axios calls
2. Keep the same return data structure
3. Update API_URL in environment variables
4. Ensure CORS is configured

Example:
```javascript
export async function submitChoice(choiceId) {
  const response = await fetch(`${API_URL}/game/choice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ choiceId })
  });
  return await response.json();
}
```

## 🐛 Troubleshooting

### Images not loading
- Check file paths in `public/images/`
- Ensure filenames match exactly (case-sensitive)
- Open browser console for 404 errors

### Game state not persisting
- Currently uses in-memory state (resets on refresh)
- To persist: implement localStorage or backend save

### Styles not applying
- Check browser console for CSS errors
- Clear browser cache
- Verify CSS import statements

## 📱 Testing

Test on different screen sizes:
- Desktop: 1920x1080
- Tablet: 768x1024
- Mobile: 375x667

Use browser DevTools responsive mode.

## 🚀 Deployment

### Build for production:
```bash
npm run build
```

Output will be in `build/` directory.

### Deploy to:
- Netlify: Connect GitHub repo
- Vercel: Import project
- AWS S3: Upload build folder
- Docker: Use existing Dockerfile

## 📞 Support

Check these files for more info:
- `LIFESIM_README.md` - Full documentation
- Component files - Inline comments
- `src/api/lifesim.js` - Game logic

---

**Happy coding! 🎮**

