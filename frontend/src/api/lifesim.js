/**
 * API Helper for LifeSim Game
 * Mock implementation - will be replaced with real backend calls later
 */

// Mock data for different scenarios
const MOCK_SCENARIOS = [
  {
    narrative: "You've just received your first paycheck from your summer job! €500 has landed in your account. What will you do with it?",
    choices: [
      { id: "save_all", label: "Save it all", description: "Put the entire amount in savings" },
      { id: "save_most", label: "Save 80%, spend 20%", description: "Balance saving with a small treat" },
      { id: "spend_half", label: "Save 50%, spend 50%", description: "Split between savings and fun" },
      { id: "spend_all", label: "Treat yourself!", description: "You earned it, spend it all" }
    ]
  },
  {
    narrative: "Your old bike is breaking down. You need reliable transportation to get to work. What's your move?",
    choices: [
      { id: "fix_bike", label: "Fix the old bike (€50)", description: "Cheap but might break again soon" },
      { id: "new_bike", label: "Buy a new bike (€300)", description: "Reliable and eco-friendly" },
      { id: "old_car", label: "Buy a used car (€2000)", description: "More freedom, but higher costs" },
      { id: "public_transport", label: "Use public transport", description: "Save money, no ownership costs" }
    ]
  },
  {
    narrative: "You're considering moving out of your parents' house. Independence comes with costs. What will you choose?",
    choices: [
      { id: "stay_home", label: "Stay at home longer", description: "Save money but less independence" },
      { id: "roommates", label: "Share apartment with roommates", description: "Split costs, social life" },
      { id: "small_apartment", label: "Get your own small apartment", description: "Full independence, moderate cost" },
      { id: "nice_apartment", label: "Rent a nice apartment", description: "Comfortable but expensive" }
    ]
  },
  {
    narrative: "A friend invites you to an expensive music festival. Tickets are €250. Your friends are all going!",
    choices: [
      { id: "skip_festival", label: "Skip it this year", description: "Save money, but FOMO" },
      { id: "volunteer", label: "Volunteer to get free entry", description: "Work for access, creative solution" },
      { id: "buy_ticket", label: "Buy the ticket", description: "Have fun, worry about money later" },
      { id: "suggest_cheaper", label: "Suggest a cheaper alternative", description: "Keep social life, save money" }
    ]
  },
  {
    narrative: "You have €1000 saved up. You're thinking about investing. What's your strategy?",
    choices: [
      { id: "keep_savings", label: "Keep it in savings account", description: "Safe but low returns" },
      { id: "index_fund", label: "Invest in index funds", description: "Diversified, long-term growth" },
      { id: "crypto", label: "Try cryptocurrency", description: "High risk, high reward?" },
      { id: "education", label: "Invest in education/skills", description: "Invest in yourself" }
    ]
  }
];

let currentScenarioIndex = 0;
let mockPlayerState = {
  id: "player-1",
  name: "Player",
  avatarKey: "avatar_girl_middle_school.png",
  metrics: {
    money: 1000,
    fiScore: 15,
    energy: 80,
    motivation: 75,
    social: 70,
    knowledge: 30
  },
  currentNarrative: MOCK_SCENARIOS[0].narrative,
  currentChoices: MOCK_SCENARIOS[0].choices,
  turn: 1,
  year: 1,
  month: 1,
  assets: [],
  recentDecisions: []
};

/**
 * Simulates network delay
 */
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Login/Start game with player name and avatar
 * @param {string} name - Player name
 * @param {string} avatarKey - Avatar image filename
 * @returns {Promise<Object>} Initial player state
 */
export async function login(name, avatarKey = "avatar_girl_middle_school.png") {
  await delay(300);
  
  mockPlayerState.name = name || "Player";
  mockPlayerState.avatarKey = avatarKey;
  mockPlayerState.metrics = {
    money: 1000,
    fiScore: 15,
    energy: 80,
    motivation: 75,
    social: 70,
    knowledge: 30
  };
  mockPlayerState.turn = 1;
  mockPlayerState.year = 1;
  mockPlayerState.month = 1;
  currentScenarioIndex = 0;
  mockPlayerState.currentNarrative = MOCK_SCENARIOS[0].narrative;
  mockPlayerState.currentChoices = MOCK_SCENARIOS[0].choices;
  mockPlayerState.assets = [];
  mockPlayerState.recentDecisions = [];
  
  return { ...mockPlayerState };
}

/**
 * Get current player state
 * @returns {Promise<Object>} Current player state
 */
export async function getPlayerState() {
  await delay(100);
  return { ...mockPlayerState };
}

/**
 * Submit a choice and get next game state
 * @param {string} choiceId - ID of the chosen option
 * @returns {Promise<Object>} Updated player state
 */
export async function submitChoice(choiceId) {
  await delay(400);
  
  // Find the choice that was made
  const choice = mockPlayerState.currentChoices.find(c => c.id === choiceId);
  const choiceLabel = choice ? choice.label : "Unknown choice";
  
  // Add to recent decisions
  mockPlayerState.recentDecisions.unshift({
    turn: mockPlayerState.turn,
    choice: choiceLabel,
    timestamp: new Date().toISOString()
  });
  if (mockPlayerState.recentDecisions.length > 5) {
    mockPlayerState.recentDecisions.pop();
  }
  
  // Apply effects based on choice
  applyChoiceEffects(choiceId);
  
  // Move to next scenario
  currentScenarioIndex = (currentScenarioIndex + 1) % MOCK_SCENARIOS.length;
  mockPlayerState.currentNarrative = MOCK_SCENARIOS[currentScenarioIndex].narrative;
  mockPlayerState.currentChoices = MOCK_SCENARIOS[currentScenarioIndex].choices;
  
  // Increment turn and time
  mockPlayerState.turn += 1;
  mockPlayerState.month += 3; // Each turn is 3 months
  if (mockPlayerState.month > 12) {
    mockPlayerState.month = mockPlayerState.month % 12 || 12;
    mockPlayerState.year += 1;
  }
  
  return { ...mockPlayerState };
}

/**
 * Apply effects to metrics based on choice
 */
function applyChoiceEffects(choiceId) {
  const effects = {
    // First scenario - paycheck
    save_all: { money: 500, fiScore: 5, motivation: -5, social: -3, knowledge: 2 },
    save_most: { money: 400, fiScore: 4, motivation: 0, social: 0, knowledge: 2 },
    spend_half: { money: 250, fiScore: 2, motivation: 5, social: 3, knowledge: 1 },
    spend_all: { money: 0, fiScore: -2, motivation: 10, social: 5, knowledge: 0 },
    
    // Transportation
    fix_bike: { money: -50, fiScore: 1, energy: -5, knowledge: 1 },
    new_bike: { money: -300, fiScore: 3, energy: 5, motivation: 3, knowledge: 2 },
    old_car: { money: -2000, fiScore: -3, energy: 10, social: 3, knowledge: 1 },
    public_transport: { money: 50, fiScore: 4, energy: -10, social: 2, knowledge: 2 },
    
    // Housing
    stay_home: { money: 200, fiScore: 3, motivation: -5, social: -5, knowledge: 1 },
    roommates: { money: -300, fiScore: 1, motivation: 5, social: 10, knowledge: 2 },
    small_apartment: { money: -600, fiScore: 2, motivation: 8, social: 3, knowledge: 3 },
    nice_apartment: { money: -1000, fiScore: -2, motivation: 10, social: 5, knowledge: 2 },
    
    // Festival
    skip_festival: { money: 0, fiScore: 2, motivation: -5, social: -8, knowledge: 1 },
    volunteer: { money: 0, fiScore: 3, motivation: 5, social: 8, energy: -10, knowledge: 3 },
    buy_ticket: { money: -250, fiScore: -1, motivation: 10, social: 10, energy: -5 },
    suggest_cheaper: { money: -50, fiScore: 2, motivation: 3, social: 5, knowledge: 2 },
    
    // Investment
    keep_savings: { money: 20, fiScore: 2, motivation: -3, knowledge: 1 },
    index_fund: { money: 100, fiScore: 5, motivation: 5, knowledge: 5 },
    crypto: { money: Math.random() > 0.5 ? 200 : -300, fiScore: 0, motivation: -5, knowledge: 2 },
    education: { money: -400, fiScore: 3, motivation: 8, knowledge: 15, energy: -5 }
  };
  
  const effect = effects[choiceId] || {};
  
  // Apply effects with bounds
  mockPlayerState.metrics.money = Math.max(0, mockPlayerState.metrics.money + (effect.money || 0));
  mockPlayerState.metrics.fiScore = clamp(mockPlayerState.metrics.fiScore + (effect.fiScore || 0), 0, 100);
  mockPlayerState.metrics.energy = clamp(mockPlayerState.metrics.energy + (effect.energy || 0), 0, 100);
  mockPlayerState.metrics.motivation = clamp(mockPlayerState.metrics.motivation + (effect.motivation || 0), 0, 100);
  mockPlayerState.metrics.social = clamp(mockPlayerState.metrics.social + (effect.social || 0), 0, 100);
  mockPlayerState.metrics.knowledge = clamp(mockPlayerState.metrics.knowledge + (effect.knowledge || 0), 0, 100);
  
  // Add assets based on choices
  if (choiceId === 'new_bike') mockPlayerState.assets.push({ name: 'New Bike', image: 'vehicle_bike_new.png' });
  if (choiceId === 'old_car') mockPlayerState.assets.push({ name: 'Used Car', image: 'vehicle_car_old.png' });
  if (choiceId === 'small_apartment') mockPlayerState.assets.push({ name: 'Small Apartment', image: 'house_apartment_block.png' });
  if (choiceId === 'nice_apartment') mockPlayerState.assets.push({ name: 'Nice Apartment', image: 'house_standard_detached.png' });
}

/**
 * Clamp a value between min and max
 */
function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Update game settings
 * @param {Object} settings - Settings object
 * @returns {Promise<void>}
 */
export async function updateSettings(settings) {
  await delay(200);
  // Store in localStorage
  localStorage.setItem('lifesim-settings', JSON.stringify(settings));
}

/**
 * Get game settings
 * @returns {Promise<Object>} Settings object
 */
export async function getSettings() {
  await delay(100);
  const stored = localStorage.getItem('lifesim-settings');
  return stored ? JSON.parse(stored) : {
    soundEffects: true,
    showTooltips: true,
    language: 'English',
    theme: 'Light',
    sessionLength: 'Medium'
  };
}

/**
 * Reset game progress
 * @returns {Promise<void>}
 */
export async function resetGame() {
  await delay(300);
  currentScenarioIndex = 0;
  mockPlayerState = {
    id: "player-1",
    name: "Player",
    avatarKey: "avatar_girl_middle_school.png",
    metrics: {
      money: 1000,
      fiScore: 15,
      energy: 80,
      motivation: 75,
      social: 70,
      knowledge: 30
    },
    currentNarrative: MOCK_SCENARIOS[0].narrative,
    currentChoices: MOCK_SCENARIOS[0].choices,
    turn: 1,
    year: 1,
    month: 1,
    assets: [],
    recentDecisions: []
  };
}

