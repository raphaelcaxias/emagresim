# styles/theme.py

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,700&display=swap');

:root {
  --bg:          #0a0c10;
  --bg2:         #111316;
  --surface:     #1a1d23;
  --border:      #2a2e36;
  --emerald:     #2dce89;
  --emerald-dim: #1a7d52;
  --gold:        #f0b429;
  --text:        #e8edf5;
  --text-muted:  #7e8493;
  --text-dim:    #4a4f5c;
  --danger:      #f85149;
  --radius:      20px;
  --radius-sm:   12px;
}

html, body, [data-testid="stAppViewContainer"], .main {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

.block-container {
  padding: 2rem 1rem 4rem !important;
  max-width: 680px !important;
}

h1, h2, h3, h4 {
  font-family: 'Fraunces', Georgia, serif !important;
  font-weight: 500;
}

/* Hero */
.hero {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px 24px;
  margin-bottom: 24px;
}

.hero-eyebrow {
  font-size: 0.7rem;
  color: var(--emerald);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 4px;
}

.hero-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.3;
  font-style: italic;
}

/* Companion */
.companion-card {
  background: var(--bg2);
  border-left: 3px solid var(--emerald);
  border-radius: var(--radius-sm);
  padding: 18px 20px;
  margin-bottom: 20px;
}

.companion-text {
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text-muted);
  font-style: italic;
}

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px 12px;
  text-align: center;
}

.stat-num {
  font-family: 'Fraunces', serif;
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1.1;
}

.stat-num.green { color: var(--emerald); }
.stat-num.gold  { color: var(--gold); }

.stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: 6px;
}

/* Meals */
.meal-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px 18px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meal-kcal {
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--emerald);
  text-align: right;
}

/* Section */
.section-title {
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 24px 0 14px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-dim);
}

.empty-state .icon { font-size: 2.5rem; margin-bottom: 8px; }

/* Tabs */
div[data-testid="stTabs"] [role="tablist"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  padding: 4px !important;
}

div[data-testid="stTabs"] [role="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  font-size: 0.85rem !important;
  padding: 6px 14px !important;
}

div[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--emerald) !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, var(--emerald), #1f9d6e) !important;
  color: #0a0c10 !important;
  border: none !important;
  border-radius: 40px !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
}

.stButton > button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Form */
div[data-testid="stForm"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 20px !important;
}

/* Inputs */
input, textarea, select {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}

/* Hide defaults */
header, footer, #MainMenu { display: none !important; }
"""
