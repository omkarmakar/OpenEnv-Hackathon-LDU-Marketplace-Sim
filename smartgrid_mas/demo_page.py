def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>⚡ GRID OPS COMMAND CENTER</title>
  <style>
    :root {
      --bg-dark: #0a0d12; --bg-panel: #111820; --bg-light: #1a2230;
      --border: #2a3545; --border-glow: #3a4555;
      --text: #c8d4e4; --text-dim: #6b7a8a; --text-bright: #e8f0f8;
      --green: #22c55e; --green-dim: #166534;
      --red: #ef4444; --red-dim: #991b1b;
      --yellow: #eab308; --yellow-dim: #854d0e;
      --blue: #3b82f6; --blue-dim: #1e40af;
      --purple: #a855f7; --cyan: #06b6d4;
      --orange: #f97316; --teal: #14b8a6;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { background: var(--bg-dark); color: var(--text); font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace; overflow-x: hidden; }
    
    /* TOP COMMAND STRIP */
    .command-strip {
      background: linear-gradient(90deg, #0d1117 0%, #1a2332 50%, #0d1117 100%);
      border-bottom: 1px solid var(--border-glow);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 52px;
    }
    .strip-left, .strip-center, .strip-right { display: flex; align-items: center; gap: 20px; }
    .mission-title { font-size: 18px; font-weight: 700; letter-spacing: 1px; }
    .mission-title span { color: var(--green); }
    
    .kpi-pill {
      background: var(--bg-light);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .kpi-pill .label { font-size: 9px; color: var(--text-dim); text-transform: uppercase; }
    .kpi-pill .value { font-size: 14px; font-weight: 700; }
    .kpi-pill .value.green { color: var(--green); }
    .kpi-pill .value.amber { color: var(--yellow); }
    .kpi-pill .value.red { color: var(--red); }
    
    .status-indicator {
      display: flex; align-items: center; gap: 6px;
      font-size: 11px;
    }
    .status-dot {
      width: 8px; height: 8px; border-radius: 50%;
      animation: pulse 1.5s infinite;
    }
    .status-dot.green { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .status-dot.amber { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); }
    .status-dot.red { background: var(--red); box-shadow: 0 0 8px var(--red); }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
    
    /* MAIN LAYOUT */
    .main-grid {
      display: grid;
      grid-template-columns: 1fr 1.2fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 2px;
      padding: 2px;
      height: calc(100vh - 56px);
      background: var(--bg-dark);
    }
    .panel {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      padding: 12px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .panel-red { outline: 2px solid var(--red); }
    .panel-flash { animation: flash 0.5s; }
    @keyframes flash { 0%,100% { outline-color: var(--border); } 50% { outline-color: var(--red); } }
    
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }
    .panel-title {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-dim);
      font-weight: 600;
    }
    .panel-badge {
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 3px;
      background: var(--bg-light);
      color: var(--text-dim);
    }
    
    /* MARKET DYNAMICS - Left Top */
    .order-ladder {
      display: flex;
      gap: 2px;
      flex: 1;
      font-size: 10px;
    }
    .ladder-col {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .ladder-col.supply { border-right: 1px solid var(--border); padding-right: 8px; margin-right: 8px; }
    .ladder-col.demand { }
    .ladder-header {
      font-size: 9px; color: var(--text-dim); text-transform: uppercase;
      padding: 4px; background: var(--bg-light); border-radius: 3px; margin-bottom: 4px;
    }
    .ladder-row {
      display: flex;
      justify-content: space-between;
      padding: 3px 4px;
      border-radius: 2px;
      margin-bottom: 2px;
    }
    .ladder-row .agent { color: var(--text-dim); }
    .ladder-row .mw { font-weight: 600; }
    .ladder-row .price { color: var(--text-dim); }
    .ladder-row.solar { border-left: 2px solid var(--green); }
    .ladder-row.peaker { border-left: 2px solid var(--orange); }
    .ladder-row.demand { border-left: 2px solid var(--blue); }
    
    .clearing-cross {
      text-align: center;
      padding: 8px;
      background: var(--bg-light);
      border-radius: 4px;
      margin-top: 8px;
    }
    .clearing-cross .price { font-size: 20px; font-weight: 700; color: var(--cyan); }
    .clearing-cross .mw { color: var(--text-dim); font-size: 10px; }
    
    /* POWER FLOW - Center */
    .power-flow {
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(180deg, #0d1117 0%, #141e28 100%);
    }
    .flow-svg {
      width: 100%;
      height: 100%;
    }
    .node {
      fill: var(--bg-light);
      stroke: var(--border);
      stroke-width: 2;
    }
    .node-label {
      fill: var(--text);
      font-size: 10px;
      text-anchor: middle;
    }
    .node-value {
      fill: var(--text-bright);
      font-size: 12px;
      font-weight: 700;
      text-anchor: middle;
    }
    .flow-line {
      stroke: var(--green);
      stroke-width: 2;
      stroke-dasharray: none;
      opacity: 0.7;
      animation: flowPulse 1s infinite;
    }
    .flow-line.thick { stroke-width: 4; }
    @keyframes flowPulse { 0%,100% { opacity: 0.7; } 50% { opacity: 0.3; } }
    
    .flow-particle {
      fill: var(--green);
      animation: particleMove 1s linear infinite;
    }
    @keyframes particleMove {
      0% { offset-distance: 0%; }
      100% { offset-distance: 100%; }
    }
    
    /* LDU DISPATCH - Right Top */
    .dispatch-table {
      font-size: 11px;
    }
    .dispatch-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 8px;
      border-bottom: 1px solid var(--border);
    }
    .dispatch-row .label { color: var(--text-dim); }
    .dispatch-row .value { font-weight: 600; }
    .dispatch-row .value.green { color: var(--green); }
    .dispatch-row .value.red { color: var(--red); }
    .dispatch-row .value.yellow { color: var(--yellow); }
    
    .events-log {
      flex: 1;
      overflow-y: auto;
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
    }
    .event-row {
      padding: 4px 6px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 8px;
    }
    .event-row .ts { color: var(--text-dim); min-width: 50px; }
    .event-row .msg { flex: 1; }
    .event-row.error { color: var(--red); }
    .event-row.warn { color: var(--yellow); }
    .event-row.shock { color: var(--orange); }
    
    /* STABILITY - Bottom Left */
    .chart-container {
      flex: 1;
      position: relative;
    }
    .chart-canvas {
      width: 100%;
      height: 100%;
    }
    
    /* SHOCK RISK - Bottom Center */
    .threat-panel {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .gauge-box {
      text-align: center;
      padding: 10px;
      background: var(--bg-light);
      border-radius: 6px;
    }
    .gauge-value {
      font-size: 28px;
      font-weight: 700;
    }
    .gauge-value.green { color: var(--green); }
    .gauge-value.amber { color: var(--yellow); }
    .gauge-value.red { color: var(--red); }
    .gauge-label { font-size: 10px; color: var(--text-dim); margin-top: 4px; }
    
    .threat-list {
      font-size: 10px;
      max-height: 100px;
      overflow-y: auto;
    }
    .threat-item {
      padding: 4px 6px;
      margin-bottom: 4px;
      background: rgba(239, 68, 68, 0.1);
      border-left: 2px solid var(--red);
      border-radius: 0 3px 3px 0;
    }
    
    /* RL DECISION - Bottom Right */
    .brain-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .policy-card {
      background: var(--bg-light);
      border-radius: 6px;
      padding: 10px;
    }
    .policy-name {
      font-size: 12px;
      font-weight: 700;
      color: var(--cyan);
    }
    .policy-reason {
      font-size: 10px;
      color: var(--text-dim);
      margin-top: 4px;
    }
    
    .score-bar {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .score-item {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
    }
    .score-item .label { color: var(--text-dim); }
    .score-item .pos { color: var(--green); }
    .score-item .neg { color: var(--red); }
    .score-total {
      border-top: 1px solid var(--border);
      padding-top: 6px;
      font-size: 14px;
      font-weight: 700;
    }
    
    /* CONTROLS */
    .controls-bar {
      background: var(--bg-panel);
      border-top: 1px solid var(--border);
      padding: 10px 20px;
      display: flex;
      justify-content: center;
      gap: 10px;
    }
    .ctrl-btn {
      background: var(--bg-light);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 20px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }
    .ctrl-btn:hover { background: var(--border); }
    .ctrl-btn.green { background: var(--green-dim); border-color: var(--green); color: var(--green); }
    .ctrl-btn.red { background: var(--red-dim); border-color: var(--red); color: var(--red); }
    .ctrl-btn.active { box-shadow: 0 0 10px var(--green); }
    
    /* GLOW EFFECTS */
    .glow-green { box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
    .glow-red { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
    .glow-amber { box-shadow: 0 0 20px rgba(234, 179, 8, 0.3); }
    
    /* RESPONSIVE */
    @media (max-width: 1200px) {
      .main-grid { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; }
      .panel:nth-child(3) { grid-column: span 2; }
    }
    @media (max-width: 800px) {
      .main-grid { grid-template-columns: 1fr; }
      .panel { min-height: 250px; }
    }
  </style>
</head>
<body>
  <!-- TOP STRIP -->
  <div class="command-strip">
    <div class="strip-left">
      <div class="mission-title">⚡ <span>GRID OPS</span> COMMAND CENTER</div>
    </div>
    <div class="strip-center">
      <div class="kpi-pill">
        <span class="label">Timestep</span>
        <span class="value" id="tsCurrent">0</span>
        <span class="value" style="color:#6b7a8a">/</span>
        <span class="value" id="tsMax">0</span>
      </div>
      <div class="kpi-pill">
        <span class="label">Scenario</span>
        <span class="value" id="scenarioName">-</span>
      </div>
      <div class="kpi-pill">
        <span class="label">Status</span>
        <span class="value green" id="simStatus">READY</span>
      </div>
      <div class="kpi-pill">
        <span class="label">Shock</span>
        <span class="value" id="shockProb">Low</span>
      </div>
    </div>
    <div class="strip-right">
      <div class="status-indicator">
        <div class="status-dot green" id="globalStatus"></div>
        <span>LIVE</span>
      </div>
      <div class="kpi-pill">
        <span class="label">Reward</span>
        <span class="value green" id="globalReward">0.00</span>
      </div>
    </div>
  </div>
  
  <!-- MAIN GRID -->
  <div class="main-grid">
    <!-- MARKET DYNAMICS -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Market Intelligence</span>
        <span class="panel-badge">LIVE</span>
      </div>
      <div class="order-ladder">
        <div class="ladder-col supply">
          <div class="ladder-header">SUPPLY</div>
          <div id="supplyBids"></div>
        </div>
        <div class="ladder-col demand">
          <div class="ladder-header">DEMAND</div>
          <div id="demandBids"></div>
        </div>
      </div>
      <div class="clearing-cross">
        <div class="price" id="clearingPrice">$0</div>
        <div class="mw" id="clearingMW">0 MW @</div>
      </div>
    </div>
    
    <!-- POWER FLOW DIGITAL TWIN -->
    <div class="panel" id="powerPanel">
      <div class="panel-header">
        <span class="panel-title">Physical Grid Control</span>
        <span class="panel-badge">DIGITAL TWIN</span>
      </div>
      <svg class="flow-svg" viewBox="0 0 400 200">
        <!-- Solar Node -->
        <g transform="translate(40, 40)">
          <circle cx="0" cy="0" r="20" class="node"/>
          <text x="0" y="-28" class="node-label">☀️ RENEWABLE</text>
          <text x="0" y="5" class="node-value" id="nodeRenew">0</text>
          <text x="0" y="35" class="node-label">MW</text>
        </g>
        <!-- Flow lines -->
        <path d="M60,40 L120,40" class="flow-line thick" id="flow1"/>
        <!-- Peaker Node -->
        <g transform="translate(140, 40)">
          <circle cx="0" cy="0" r="20" class="node"/>
          <text x="0" y="-28" class="node-label">🏭 PEAKER</text>
          <text x="0" y="5" class="node-value" id="nodePeaker">0</text>
          <text x="0" y="35" class="node-label">MW</text>
        </g>
        <path d="M160,40 L200,40" class="flow-line" id="flow2"/>
        <!-- EV Node -->
        <g transform="translate(40, 160)">
          <circle cx="0" cy="0" r="18" class="node"/>
          <text x="0" y="-25" class="node-label">🔋 EV</text>
          <text x="0" y="5" class="node-value" id="nodeEV">0%</text>
        </g>
        <path d="M50,145 L50,100 L200,100" class="flow-line" id="flow3"/>
        <!-- LDU Node (Center) -->
        <g transform="translate(200, 100)">
          <rect x="-25" y="-25" width="50" height="50" rx="4" class="node"/>
          <text x="0" y="-35" class="node-label">LDU UNIT</text>
          <text x="0" y="8" class="node-value" id="nodeLDU">0</text>
          <text x="0" y="40" class="node-label">MW Out</text>
        </g>
        <!-- Industrial Node -->
        <g transform="translate(360, 100)">
          <circle cx="0" cy="0" r="22" class="node"/>
          <text x="0" y="-30" class="node-label">🏭 LOAD</text>
          <text x="0" y="5" class="node-value" id="nodeLoad">0</text>
          <text x="0" y="40" class="node-label">MW Demand</text>
        </g>
        <path d="M250,100 L338,100" class="flow-line thick" id="flow4"/>
        <!-- Loss indicator -->
        <g transform="translate(230, 70)">
          <text x="0" y="0" class="node-label" style="fill:#ef4444;font-size:9px">⚡ LOSS: <tspan id="nodeLoss">0</tspan> MW (3%)</text>
        </g>
      </svg>
    </div>
    
    <!-- LDU DISPATCH -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">LDU Dispatch Control</span>
        <span class="panel-badge" id="correctionBadge">0 CORR</span>
      </div>
      <div class="dispatch-table">
        <div class="dispatch-row"><span class="label">Renewables Dispatch</span><span class="value green" id="dispRenew">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">Peaker Dispatch</span><span class="value green" id="dispPeaker">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">EV Discharge</span><span class="value" id="dispEV">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">Transmission Loss</span><span class="value yellow" id="dispLoss">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">Storage Loss</span><span class="value yellow" id="dispStorLoss">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">Net Delivered</span><span class="value green" id="dispNet">0</span><span class="label">MW</span></div>
        <div class="dispatch-row"><span class="label">Unmet Demand</span><span class="value red" id="dispUnmet">0</span><span class="label">MW</span></div>
      </div>
      <div class="panel-header" style="margin-top:12px">
        <span class="panel-title">Event Log</span>
      </div>
      <div class="events-log" id="eventLog"></div>
    </div>
    
    <!-- STABILITY CHART -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Stability Analytics</span>
        <span class="panel-badge">HISTORY</span>
      </div>
      <div class="chart-container">
        <canvas id="stabilityChart"></canvas>
      </div>
    </div>
    
    <!-- SHOCK RISK -->
    <div class="panel" id="riskPanel">
      <div class="panel-header">
        <span class="panel-title">Shock / Risk Theater</span>
        <span class="panel-badge" id="riskBadge">NORMAL</span>
      </div>
      <div class="threat-panel">
        <div class="gauge-box">
          <div class="gauge-value green" id="blackoutRisk">0%</div>
          <div class="gauge-label">Blackout Risk</div>
        </div>
        <div class="gauge-box">
          <div class="gauge-value green" id="gridStress">0%</div>
          <div class="gauge-label">Grid Stress</div>
        </div>
      </div>
      <div class="threat-list" id="threatList">
        <div class="threat-item">System Nominal</div>
      </div>
    </div>
    
    <!-- RL DECISION -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">RL Decision Intelligence</span>
        <span class="panel-badge">AI THINKING</span>
      </div>
      <div class="brain-panel">
        <div class="policy-card">
          <div class="policy-name" id="policyName">Adaptive Policy</div>
          <div class="policy-reason" id="policyReason">Analyzing grid state...</div>
        </div>
        <div class="score-bar">
          <div class="score-item"><span class="label">Reliability</span><span class="pos" id="sRel">+0.00</span></div>
          <div class="score-item"><span class="label">Economic</span><span class="pos" id="sEcon">+0.00</span></div>
          <div class="score-item"><span class="label">Green</span><span class="pos" id="sGreen">+0.00</span></div>
          <div class="score-item"><span class="label">Penalties</span><span class="neg" id="sPenal">-0.00</span></div>
          <div class="score-item score-total"><span class="label">TOTAL</span><span class="value" id="sTotal">0.00</span></div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- CONTROLS -->
  <div class="controls-bar">
    <select id="taskSel" class="ctrl-btn">
      <option value="default">Default</option>
      <option value="long_horizon">Long Horizon</option>
      <option value="stress_shock">Stress Shock</option>
    </select>
    <select id="polSel" class="ctrl-btn">
      <option value="adaptive">Smart Policy</option>
      <option value="heuristic">Heuristic</option>
      <option value="random">Random</option>
    </select>
    <button class="ctrl-btn green" id="resetBtn">🔄 NEW RUN</button>
    <button class="ctrl-btn" id="stepBtn">STEP ▶</button>
    <button class="ctrl-btn" id="playBtn">▶▶ RUN</button>
    <button class="ctrl-btn" id="pauseBtn">⏸ PAUSE</button>
    <button class="ctrl-btn red" id="shockBtn">⚡ SHOCK</button>
    <button class="ctrl-btn" id="baselineBtn">📊 Baseline</button>
  </div>

<script>
const API = '';
let sessionId = null, timer = null, obsCache = null;
const historyData = [];

const cvs = document.getElementById('stabilityChart');
const ctx = cvs.getContext('2d');
const dpr = window.devicePixelRatio || 1;

function resize() {
  const r = cvs.parentElement.getBoundingClientRect();
  cvs.width = r.width * dpr; cvs.height = (r.height - 20) * dpr;
  cvs.style.width = r.width + 'px'; cvs.style.height = (r.height - 20) + 'px';
  ctx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();

function log(msg, type='') {
  const el = document.getElementById('eventLog');
  const div = Object.assign(document.createElement('div'), {className: 'event-row ' + type, innerHTML: `<span class="ts">T${document.getElementById('tsCurrent').textContent}</span><span class="msg">${msg}</span>`});
  el.insertBefore(div, el.firstChild);
  while (el.children.length > 30) el.lastChild.remove();
}

function logThreat(msg) {
  const el = document.getElementById('threatList');
  const div = Object.assign(document.createElement('div'), {className: 'threat-item', textContent: msg});
  el.insertBefore(div, el.firstChild);
  while (el.children.length > 5) el.lastChild.remove();
}

async function api(path, body) {
  const opts = {method: body ? 'POST' : 'GET'};
  if (body) { opts.headers = {'Content-Type': 'application/json'}; opts.body = JSON.stringify(body); }
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function updateSupplyBids(ren, peak, price) {
  const html = `
    <div class="ladder-row solar"><span class="agent">Solar</span><span class="mw">${Math.round(ren)}</span><span class="price">$20</span></div>
    <div class="ladder-row peaker"><span class="agent">Gas</span><span class="mw">${Math.round(peak)}</span><span class="price">$${Math.round(price)}</span></div>
  `;
  document.getElementById('supplyBids').innerHTML = html;
}

function updateDemandBids(demand, price) {
  const html = `
    <div class="ladder-row demand"><span class="agent">Factory</span><span class="mw">${Math.round(demand)}</span><span class="price">$${Math.round(price)}</span></div>
  `;
  document.getElementById('demandBids').innerHTML = html;
}

function updatePowerFlow(renew, peak, evDis, delivered, loss) {
  document.getElementById('nodeRenew').textContent = Math.round(renew);
  document.getElementById('nodePeaker').textContent = Math.round(peak);
  document.getElementById('nodeEV').textContent = evDis > 0 ? Math.round(evDis) + '⚡' : '0';
  document.getElementById('nodeLDU').textContent = Math.round(delivered);
  document.getElementById('nodeLoad').textContent = delivered;
  document.getElementById('nodeLoss').textContent = loss.toFixed(1);
}

function updateDispatch(d) {
  document.getElementById('dispRenew').textContent = d.renewable_dispatch_mwh.toFixed(0);
  document.getElementById('dispPeaker').textContent = d.peaker_dispatch_mwh.toFixed(0);
  document.getElementById('dispEV').textContent = d.ev_discharge_mwh.toFixed(1);
  document.getElementById('dispLoss').textContent = d.transmission_loss_mwh.toFixed(1);
  document.getElementById('dispStorLoss').textContent = d.storage_loss_mwh.toFixed(1);
  document.getElementById('dispNet').textContent = d.delivered_supply_mwh.toFixed(0);
  document.getElementById('dispUnmet').textContent = d.unmet_demand_mwh.toFixed(0);
  const corr = d.corrections || [];
  document.getElementById('correctionBadge').textContent = corr.length + ' CORR';
  if (corr.length > 0) {
    const panel = document.getElementById('powerPanel');
    panel.classList.add('panel-flash');
    setTimeout(() => panel.classList.remove('panel-flash'), 500);
    corr.forEach(c => log(c, 'warn'));
  }
}

function updateRisk(supply, demand, blackoutRisk) {
  const stress = Math.max(0, (demand - supply) / demand * 100);
  document.getElementById('gridStress').textContent = stress.toFixed(0) + '%';
  document.getElementById('gridStress').className = 'gauge-value ' + (stress < 20 ? 'green' : stress < 50 ? 'amber' : 'red');
  
  document.getElementById('blackoutRisk').textContent = (blackoutRisk * 100).toFixed(0) + '%';
  document.getElementById('blackoutRisk').className = 'gauge-value ' + (blackoutRisk < 0.1 ? 'green' : blackoutRisk < 0.3 ? 'amber' : 'red');
  
  const badge = document.getElementById('riskBadge');
  badge.textContent = stress > 50 ? 'CRITICAL' : stress > 20 ? 'ELEVATED' : 'NORMAL';
  badge.style.background = stress > 50 ? 'var(--red)' : stress > 20 ? 'var(--yellow)' : 'var(--green-dim)';
}

function drawChart() {
  const w = cvs.width / dpr, h = cvs.height / dpr;
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, w, h);
  if (historyData.length < 2) return;
  const maxD = Math.max(...historyData.map(x => x.demand), ...historyData.map(x => x.supply), 150) * 1.1;
  const step = w / Math.max(1, historyData.length - 1);
  
  // Demand line
  ctx.strokeStyle = '#3b82f6';
  ctx.lineWidth = 2;
  ctx.beginPath();
  historyData.forEach((p, i) => { if (i===0) ctx.moveTo(i*step, h - (p.demand/maxD)*h*0.9); else ctx.lineTo(i*step, h - (p.demand/maxD)*h*0.9); });
  ctx.stroke();
  
  // Supply area
  ctx.beginPath();
  ctx.moveTo(0, h);
  historyData.forEach((p, i) => ctx.lineTo(i*step, h - (p.supply/maxD)*h*0.9));
  ctx.lineTo(w, h);
  ctx.fillStyle = 'rgba(34, 197, 94, 0.2)';
  ctx.fill();
  ctx.strokeStyle = '#22c55e';
  ctx.beginPath();
  historyData.forEach((p, i) => { if (i===0) ctx.moveTo(i*step, h - (p.supply/maxD)*h*0.9); else ctx.lineTo(i*step, h - (p.supply/maxD)*h*0.9); });
  ctx.stroke();
  
  // Price overlay
  const maxP = Math.max(...historyData.map(x => x.price), 200) * 1.1;
  ctx.strokeStyle = '#eab308';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  historyData.forEach((p, i) => { if (i===0) ctx.moveTo(i*step, h - (p.price/maxP)*h*0.9); else ctx.lineTo(i*step, h - (p.price/maxP)*h*0.9); });
  ctx.stroke();
  ctx.setLineDash([]);
}

async function reset() {
  const task = document.getElementById('taskSel').value;
  const data = await api('/reset', {task_id: task, seed: 42});
  sessionId = data.session_id;
  obsCache = data.observation;
  historyData.length = 0;
  
  document.getElementById('tsMax').textContent = obsCache.max_steps;
  document.getElementById('scenarioName').textContent = task.toUpperCase();
  document.getElementById('simStatus').textContent = 'RUNNING';
  document.getElementById('simStatus').className = 'value green';
  document.getElementById('eventLog').innerHTML = '';
  
  document.getElementById('threatList').innerHTML = '<div class="threat-item">System Ready</div>';
  log('Simulation started: ' + task);
  drawChart();
}

async function step() {
  if (!sessionId) { await reset(); return; }
  const st = await api('/state?session_id=' + sessionId);
  if (st.episode_done) {
    document.getElementById('simStatus').textContent = 'COMPLETE';
    document.getElementById('simStatus').className = 'value';
    log('Episode complete!');
    pause();
    return;
  }
  
  const obs = st.observation;
  const pol = document.getElementById('polSel').value;
  const d = obs.demand_mwh, r = obs.renewable_availability_mwh, p = obs.peaker_capacity_mwh;
  const leader = obs.leader_price_signal, scarcity = obs.scarcity_index || 0;
  const storage = obs.ev_storage_mwh, cap = obs.ev_storage_capacity_mwh;
  
  const soc = storage / cap;
  let renQt, peakQt, peakPr, evC, evD;
  
  if (pol === 'adaptive') {
    renQt = Math.min(r, d * (0.52 + 0.18 * (1 - scarcity)));
    peakQt = Math.min(p, (d - renQt) * (1 + 0.25 * scarcity));
    peakPr = leader * 1.1;
    const minS = cap * 0.2, maxS = cap * 0.8;
    if (soc <= 0.35) { evC = Math.min(maxS - storage, 5); evD = 0; }
    else if (soc <= 0.5) { evC = scarcity > 0.4 ? 0 : Math.min(maxS - storage, 3); evD = scarcity > 0.4 ? Math.min(storage - minS, 2 + 4 * scarcity) : 0; }
    else { evC = 0; evD = scarcity > 0.2 ? Math.min(storage - minS, 4 + 5 * scarcity) : 0; }
    evC = Math.max(0, evC); evD = Math.max(0, evD);
  } else if (pol === 'heuristic') {
    renQt = Math.min(r, d * 0.55); peakQt = Math.min(p, d - renQt); peakPr = leader * 1.02;
    evC = r > d ? 3 : 0; evD = r < d * 0.8 ? 2 : 0;
  } else {
    renQt = Math.min(r, d * 0.5 + Math.random() * 20);
    peakQt = Math.min(p, d * 0.4);
    peakPr = 45 + Math.random() * 20;
    evC = Math.random() > 0.6 ? 2 : 0; evD = Math.random() > 0.6 ? 2 : 0;
  }
  
  const action = {action: {bids: [
    {agent_id:'solar', role:'renewable_prosumer', bid_type:'supply', quantity_mwh:Math.max(0, renQt), price_usd_per_mwh:20},
    {agent_id:'gas', role:'peaker_plant', bid_type:'supply', quantity_mwh:Math.max(0, peakQt), price_usd_per_mwh:peakPr},
    {agent_id:'load', role:'industrial_load', bid_type:'demand', quantity_mwh:d, price_usd_per_mwh:leader * 1.45}
  ], ev_charge_mwh: evC, ev_discharge_mwh: evD}};
  
  const res = await api('/step?session_id=' + sessionId, action);
  const info = res.info, disp = info.dispatch, mkt = info.market;
  const rew = res.reward;
  
  document.getElementById('tsCurrent').textContent = res.observation.step;
  document.getElementById('tsMax').textContent = obs.max_steps;
  document.getElementById('globalReward').textContent = rew.score.toFixed(2);
  
  updateSupplyBids(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, peakPr);
  updateDemandBids(d, leader * 1.45);
  document.getElementById('clearingPrice').textContent = '$' + Math.round(mkt.clearing_price || 0);
  document.getElementById('clearingMW').textContent = (mkt.cleared_mwh || 0).toFixed(0) + ' MW @';
  
  updatePowerFlow(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, disp.ev_discharge_mwh, disp.delivered_supply_mwh, disp.transmission_loss_mwh);
  updateDispatch(disp);
  
  historyData.push({demand: d, supply: disp.delivered_supply_mwh, price: mkt.clearing_price || 0});
  drawChart();
  
  const blackoutRisk = rew.blackout_penalty || 0;
  updateRisk(d, d - (disp.delivered_supply_mwh || 0), blackoutRisk);
  
  if (obs.shock_active) {
    document.getElementById('riskPanel').classList.add('panel-red');
    log('⚡ SHOCK ACTIVE!', 'shock');
    logThreat('⚡ Renewable dropped ' + info.dynamics?.shock_renewable_drop + ' MW');
    setTimeout(() => document.getElementById('riskPanel').classList.remove('panel-red'), 1000);
  }
  
  document.getElementById('policyName').textContent = pol.toUpperCase() + ' POLICY';
  let reason = scarcity > 0.3 ? 'High scarcity detected - Emergency dispatch' : 'Balanced operation';
  document.getElementById('policyReason').textContent = reason;
  
  document.getElementById('sRel').textContent = '+' + rew.demand_satisfaction_score.toFixed(2);
  document.getElementById('sEcon').textContent = '+' + rew.cost_efficiency_score.toFixed(2);
  document.getElementById('sGreen').textContent = '+' + rew.renewable_utilization_score.toFixed(2);
  document.getElementById('sPenal').textContent = '-' + (rew.infeasibility_penalty + rew.blackout_penalty).toFixed(2);
  document.getElementById('sTotal').textContent = rew.score.toFixed(2);
}

function play() { pause(); timer = setInterval(step, 400); }
function pause() { if (timer) clearInterval(timer); timer = null; }
async function shock() {
  if (!sessionId) return;
  await api('/inject-shock', {renewable_drop_mwh: 25});
  log('⚡ MANUAL SHOCK INJECTED', 'shock');
  document.getElementById('shockProb').textContent = 'MANUAL';
  logThreat('⚡ Manual shock: -25 MW');
  document.getElementById('riskPanel').classList.add('panel-red');
  setTimeout(() => document.getElementById('riskPanel').classList.remove('panel-red'), 500);
}

document.getElementById('resetBtn').onclick = () => { pause(); reset(); };
document.getElementById('stepBtn').onclick = () => { pause(); step(); };
document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('shockBtn').onclick = shock;
document.getElementById('baselineBtn').onclick = async () => {
  document.getElementById('polSel').value = 'heuristic';
  log('Switched to Heuristic Baseline');
};

reset();
</script>
</body>
</html>
"""