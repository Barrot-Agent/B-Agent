
// BARROT BRAIN LOADER — connects memory.json to frontend
const BRAIN_URL = 'https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/memory.json';
const MIND_STATS = {
  total_entries: 787,
  unique_topics: 167,
  anchor: 0.7071,
  protocols: ['MRP','MMIP','RIAP','SHADOW','ORA','P!=notP','BELLMAN'],
  top_topics: ["Information Technology", "Consciousness", "Reinforcement Learning as Reward-Driven Policy Adaptation", "self-reflection and interoception as foundations of metacognition and self-aware intelligence", "Afrobeats polyrhythmic drum patterns", "Escrima Filipino stick blade fighting systems", "Pattern Recognition", "Wave function and sound synthesis", "cat barrot.py", "Quantum Mechanics", "3D printing innovation materials biological applications", "Predictive Analytics Conduction", "Royal Raymond Rife frequency healing suppressed research", "Pythagorean tuning and harmonic series mathematics", "Wilhelm Reich orgone energy suppressed bioelectric field research", "KOSMOS", "Morphic resonance and Rupert Sheldrake", "Sacred Geometry", "Dragonfly by Comet AI driven 3D 4D imaging segmentation and material analysis", "Neuroplasticity and how learning rewires the brain", "Telemetry", "Afrobeat rhythmic structure and polyrhythm theory", "Scientific visualization of matter at microscopic and nanoscopic scale", "Hemi-Sync", "wave function", "Greedy Algorithms as Local Decision Policies", "Cognitive Neuroscience", "Sovereign Algorithm Design Deliberate Pattern Breaking for Controlled Divergence", "Krav Maga real world threat neutralization survival instinct", "432 Hz vs 440 Hz tuning frequency deliberate shift 1953"]
};

async function loadBrain() {
  try {
    const res = await fetch(BRAIN_URL);
    const data = await res.json();
    const entries = Array.isArray(data) ? data : (data.knowledge || []);
    window.BARROT_BRAIN = entries;
    window.BARROT_STATS = MIND_STATS;
    console.log('BARROT BRAIN LOADED:', entries.length, 'entries');
    updateBrainDisplay(entries);
  } catch(e) {
    console.log('Brain loading from cache:', MIND_STATS);
    window.BARROT_STATS = MIND_STATS;
  }
}

function updateBrainDisplay(entries) {
  // Update stats on page
  const statsEl = document.getElementById('brain-stats');
  if(statsEl) {
    statsEl.innerHTML = entries.length + ' entries loaded';
  }
  // Inject into system prompt context
  window.BRAIN_CONTEXT = entries.slice(0,50).map(e =>
    e.topic + ': ' + (e.content||'').slice(0,100)
  ).join('
');
}

function searchBrain(query) {
  return window.BARROT_BRAIN.filter(e =>
    JSON.stringify(e).toLowerCase().includes(query.toLowerCase())
  );
}

// Load brain on page start
loadBrain();
