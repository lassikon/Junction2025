# LifeSim Component Architecture

## Component Hierarchy

```
App (with GameProvider)
│
├── Router
    │
    ├── Route: "/" → LoginPage
    │   ├── Avatar Selection Grid
    │   ├── Name Input
    │   └── Start Button
    │
    ├── Route: "/game" → GamePage
    │   ├── TopBar
    │   │   ├── Game Title
    │   │   ├── Navigation Links
    │   │   └── Player Info (name, money, FI score, stats button)
    │   │
    │   ├── Game Time Display
    │   │   ├── Year/Month
    │   │   └── Turn Counter
    │   │
    │   ├── Game Layout (Grid)
    │   │   │
    │   │   ├── Left Side
    │   │   │   ├── SceneView
    │   │   │   │   ├── Background Image
    │   │   │   │   ├── Character Avatar
    │   │   │   │   └── Asset Images
    │   │   │   │
    │   │   │   └── MetricsBar
    │   │   │       └── 6 Metric Items (with progress bars)
    │   │   │
    │   │   └── Right Side
    │   │       └── ChoiceList
    │   │           ├── Narrative Box
    │   │           └── Choice Buttons (4 buttons)
    │   │
    │   └── StatsDrawer (conditional)
    │       ├── Drawer Overlay
    │       ├── Drawer Panel
    │       │   ├── Header with Close Button
    │       │   ├── Player Profile
    │       │   ├── Detailed Metrics
    │       │   ├── Current Assets
    │       │   └── Recent Decisions
    │
    ├── Route: "/settings" → SettingsPage
    │   ├── TopBar
    │   ├── Settings Sections
    │   │   ├── General Settings (toggles)
    │   │   ├── Display Settings (selects)
    │   │   └── Gameplay Settings (reset button)
    │   └── Navigation Buttons
    │
    ├── Route: "/chat" → Chat (preserved)
    └── Route: "/old-home" → MockHome (preserved)
```

## Data Flow

```
GameProvider (Context)
    │
    ├── State:
    │   ├── playerState (from API)
    │   ├── loading
    │   └── error
    │
    ├── Methods:
    │   ├── startGame(name, avatar)
    │   ├── makeChoice(choiceId)
    │   ├── refreshState()
    │   └── resetGameState()
    │
    └── Consumed by:
        ├── LoginPage (startGame)
        ├── GamePage (playerState, makeChoice)
        └── SettingsPage (resetGameState)
```

## API Layer

```
lifesim.js (Mock API)
    │
    ├── Mock Data:
    │   ├── MOCK_SCENARIOS (5 scenarios)
    │   └── mockPlayerState (current state)
    │
    ├── Functions:
    │   ├── login(name, avatarKey)
    │   ├── getPlayerState()
    │   ├── submitChoice(choiceId)
    │   ├── updateSettings(settings)
    │   ├── getSettings()
    │   └── resetGame()
    │
    └── Internal:
        ├── applyChoiceEffects(choiceId)
        ├── delay(ms)
        └── clamp(value, min, max)
```

## Component Props Interface

### TopBar
```javascript
{
  playerName: string,
  money: number,
  fiScore: number,
  onViewStats: function (optional)
}
```

### MetricsBar
```javascript
{
  metrics: {
    money: number,
    fiScore: number,
    energy: number,
    motivation: number,
    social: number,
    knowledge: number
  }
}
```

### SceneView
```javascript
{
  background: string,      // 'sunny', 'rainy', 'sunset', 'cloudy', 'indoor'
  character: string,        // avatar filename
  assets: Array<{
    name: string,
    image: string
  }>
}
```

### ChoiceList
```javascript
{
  narrative: string,
  choices: Array<{
    id: string,
    label: string,
    description: string
  }>,
  onChoiceClick: function,
  disabled: boolean
}
```

### StatsDrawer
```javascript
{
  isOpen: boolean,
  onClose: function,
  playerState: {
    name: string,
    avatarKey: string,
    metrics: object,
    assets: array,
    recentDecisions: array,
    year: number,
    month: number
  }
}
```

## State Management Pattern

### GameContext Pattern
```javascript
// Provider wraps entire app
<GameProvider>
  <App />
</GameProvider>

// Components consume via hook
const { playerState, makeChoice, loading } = useGame();
```

### Local State Examples
```javascript
// LoginPage
const [name, setName] = useState('');
const [selectedAvatar, setSelectedAvatar] = useState('...');

// GamePage
const [isStatsOpen, setIsStatsOpen] = useState(false);
const [background, setBackground] = useState('sunny');

// SettingsPage
const [settings, setSettings] = useState({ ... });
const [saving, setSaving] = useState(false);
const [resetConfirm, setResetConfirm] = useState(false);
```

## Event Flow Examples

### Starting a New Game
```
User clicks "Start Game"
    ↓
LoginPage calls startGame(name, avatar)
    ↓
GameContext.startGame() calls api.login()
    ↓
API returns initial playerState
    ↓
Context updates playerState
    ↓
Navigate to /game
    ↓
GamePage renders with playerState
```

### Making a Choice
```
User clicks choice button
    ↓
ChoiceList calls onChoiceClick(choiceId)
    ↓
GamePage calls makeChoice(choiceId)
    ↓
GameContext.makeChoice() calls api.submitChoice()
    ↓
API updates state (metrics, narrative, choices)
    ↓
Context updates playerState
    ↓
Components re-render with new state
    ↓
MetricsBar shows updated metrics
SceneView may show new assets
ChoiceList shows new narrative
```

### Opening Stats Drawer
```
User clicks "View Stats"
    ↓
TopBar calls onViewStats()
    ↓
GamePage sets isStatsOpen = true
    ↓
StatsDrawer renders with slide-in animation
    ↓
User clicks overlay or close button
    ↓
GamePage sets isStatsOpen = false
    ↓
StatsDrawer unmounts
```

## Styling Architecture

### CSS Organization
```
Global Styles (App.css, index.css)
    ├── CSS Reset
    ├── Theme classes
    ├── Utility classes
    └── Animation keyframes

Component Styles (ComponentName.css)
    ├── Component-specific classes
    ├── Responsive breakpoints
    ├── Hover/active states
    └── Theme variants
```

### Naming Convention
```
.component-name           → Main component wrapper
.component-section        → Section within component
.component-item           → Individual item
.component-item-property  → Property of item

Examples:
.stats-drawer
.stats-drawer-header
.stats-drawer-content
.stat-item
.stat-item-label
```

### Responsive Breakpoints
```css
/* Desktop first approach */
@media (max-width: 1024px) {
  /* Tablet styles */
}

@media (max-width: 768px) {
  /* Mobile styles */
}
```

## File Dependencies

### Import Graph
```
index.js
  └── App.js
      ├── GameContext.js
      │   └── api/lifesim.js
      ├── routes/LoginPage.js
      │   └── GameContext.js
      ├── routes/GamePage.js
      │   ├── GameContext.js
      │   ├── components/TopBar.js
      │   ├── components/SceneView.js
      │   ├── components/ChoiceList.js
      │   ├── components/MetricsBar.js
      │   └── components/StatsDrawer.js
      ├── routes/SettingsPage.js
      │   ├── GameContext.js
      │   ├── api/lifesim.js
      │   └── components/TopBar.js
      ├── MockHome.js (legacy)
      └── Chat.js (legacy)
```

## Extension Points

### Adding New Components
1. Create `ComponentName.js` in `src/components/`
2. Create `ComponentName.css` in same directory
3. Export from `src/components/index.js`
4. Import where needed

### Adding New Pages
1. Create `PageName.js` in `src/routes/`
2. Create `PageName.css` in same directory
3. Add route in `App.js`
4. Add navigation link in `TopBar.js`

### Adding New Scenarios
1. Edit `src/api/lifesim.js`
2. Add to `MOCK_SCENARIOS` array
3. Add effects to `applyChoiceEffects()`
4. Test choice consequences

### Adding New Metrics
1. Update `PlayerMetrics` in API
2. Update `metricsConfig` in `MetricsBar.js`
3. Update `metricsConfig` in `StatsDrawer.js`
4. Add metric effects to choices

## Testing Strategy

### Unit Testing (future)
- Test individual components with React Testing Library
- Test API functions with mock data
- Test utility functions (clamp, etc.)

### Integration Testing (future)
- Test complete user flows
- Test state management
- Test routing

### Manual Testing Checklist
- ✅ Start game flow
- ✅ Make choices and see metric changes
- ✅ View stats drawer
- ✅ Navigate between pages
- ✅ Change settings
- ✅ Reset game
- ✅ Responsive on mobile/tablet
- ✅ Theme changes

## Performance Considerations

### Optimizations Implemented
- Context API for minimal re-renders
- CSS animations (GPU-accelerated)
- Image lazy loading via browser
- Functional components with hooks

### Future Optimizations
- React.memo for expensive components
- useMemo for computed values
- Code splitting with React.lazy
- Service worker for offline support

---

This architecture supports easy extension, maintenance, and testing while keeping the codebase clean and organized.

