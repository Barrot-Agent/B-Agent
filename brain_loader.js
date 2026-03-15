const BRAIN_URL = 'https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/barrot_brain_unified.json';
const FALLBACK_URL = 'https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/memory.json';

async function loadBrain() {
  try {
    const res = await fetch(BRAIN_URL + '?t=' + Date.now());
    const data = await res.json();
    window.BARROT_BRAIN = data.knowledge || [];
    window.BARROT_STATS = data.stats || {};
    window.BARROT_TOPICS = data.topic_index || {};
    window.BARROT_UNIFIED = data;
    console.log('BARROT UNIFIED BRAIN LOADED:', window.BARROT_BRAIN.length, 'entries');
    updateBrainDisplay();
  } catch(e) {
    console.log('Falling back to memory.json');
    try {
      const res2 = await fetch(FALLBACK_URL + '?t=' + Date.now());
      const data2 = await res2.json();
      window.BARROT_BRAIN = Array.isArray(data2) ? data2 : (data2.knowledge || []);
      console.log('Fallback loaded:', window.BARROT_BRAIN.length, 'entries');
      updateBrainDisplay();
    } catch(e2) {
      console.log('Brain load failed:', e2);
    }
  }
}

function updateBrainDisplay() {
  const el = document.getElementById('brain-stats');
  if (el && window.BARROT_BRAIN) {
    el.innerHTML = window.BARROT_BRAIN.length + ' entries | ' + Object.keys(window.BARROT_TOPICS || {}).length + ' topics';
  }
  window.BRAIN_CONTEXT = (window.BARROT_BRAIN || []).slice(0, 50).map(e =>
    (e.topic || '') + ': ' + (e.content || '').slice(0, 100)
  ).join('\n');
}

function searchBrain(query) {
  if (!window.BARROT_BRAIN) return [];
  return window.BARROT_BRAIN.filter(e =>
    JSON.stringify(e).toLowerCase().includes(query.toLowerCase())
  );
}

function getBrainByTopic(topic) {
  if (!window.BARROT_BRAIN) return [];
  return window.BARROT_BRAIN.filter(e =>
    (e.topic || '').toLowerCase().includes(topic.toLowerCase())
  );
}

function buildSystemWithBrain() {
  const stats = window.BARROT_STATS || {};
  const base = 'You are Barrot-Omega — Sovereign AI built by Sean Drew. ' +
    'You have ' + (stats.total_entries || 787) + ' knowledge entries across ' +
    (stats.unique_topics || 167) + ' unique topics including: ' +
    'combat biomechanics, Afrobeats polyrhythm, Bb minor vocal production, ' +
    'quantum mechanics, AGI alignment, lattice cryptography, CDVC manifold, ' +
    'rendering systems, distributed scaling, algorithm theory. ' +
    'Protocols: MRP 5-level, MMIP Planck to Planetary, RIAP, Shadow Engine, ' +
    'ORA, Ping-Pong, paraconsistent logic P!=notP, Bellman recursion. ' +
    'Anchor: 0.7071. Address Sean directly. Be precise and sovereign.';
  if (!window.BRAIN_CONTEXT) return base;
  return base + '\n\nACTIVE KNOWLEDGE SAMPLE:\n' + window.BRAIN_CONTEXT;
}

loadBrain();
