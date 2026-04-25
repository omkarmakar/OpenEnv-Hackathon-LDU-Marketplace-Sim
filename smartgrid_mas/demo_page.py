def build_demo_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ GRID OPS COMMAND CENTER</title>
  <style>
    :root {
      --bg: #0a0e12; --panel: #12181f; --border: #1e2a38;
      --text: #c8d4e4; --dim: #64748b;
      --green: #22c55e; --green-glow: rgba(34, 197, 94, 0.4);
      --red: #ef4444; --yellow: #eab308; --blue: #3b82f6; --purple: #a855f7; --cyan: #06b6d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { background: var(--bg); color: var(--text); font-family: 'Courier New', monospace; overflow: hidden; }
    
    /* TOP BAR */
    .topbar { background: linear-gradient(90deg, #0f1419, #1a2530, #0f1419); padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
    .logo { font-size: 20px; font-weight: bold; }
    .logo span { color: var(--green); }
    .kpi-bar { display: flex; gap: 12px; }
    .kpi { background: var(--panel); padding: 8px 14px; border-radius: 4px; border: 1px solid var(--border); }
    .kpi .lbl { font-size: 9px; color: var(--dim); }
    .kpi .val { font-size: 16px; font-weight: bold; }
    .live-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; display: inline-block; animation: blink 1s infinite; }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    
    /* MAIN GRID */
    .grid { display: grid; grid-template-columns: 1fr 1.2fr 1fr; grid-template-rows: 1fr 1fr; gap: 2px; padding: 2px; height: calc(100vh - 120px); background: var(--bg); }
    .panel { background: var(--panel); border: 1px solid var(--border); padding: 10px; overflow: hidden; }
    .panel-title { font-size: 10px; color: var(--dim); text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
    
    /* CONTROLS */
    .controls { background: var(--panel); padding: 10px 20px; display: flex; gap: 10px; border-top: 1px solid var(--border); align-items: center; }
    .btn { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 10px 16px; border-radius: 4px; cursor: pointer; font-size: 12px; }
    .btn:hover { background: var(--border); }
    .btn.primary { background: var(--green); color: #000; border: none; font-weight: bold; }
    .btn.danger { background: var(--red); color: #fff; border: none; }
    select.btn { padding: 10px 12px; }
    
    /* MARKET PANEL */
    .bid-ladder { display: flex; gap: 10px; font-size: 11px; flex: 1; }
    .ladder-col { flex: 1; }
    .ladder-head { background: var(--bg); padding: 4px 8px; border-radius: 3px; margin-bottom: 4px; font-size: 10px; color: var(--dim); }
    .bid-row { display: flex; justify-content: space-between; padding: 3px 0; border-left: 2px solid var(--border); padding-left: 4px; margin-bottom: 2px; }
    .bid-row.solar { border-color: var(--green); }
    .bid-row.peaker { border-color: var(--yellow); }
    .bid-row.demand { border-color: var(--blue); }
    .clearing-box { text-align: center; background: var(--bg); padding: 10px; border-radius: 4px; margin-top: auto; }
    .clearing-price { font-size: 22px; font-weight: bold; color: var(--cyan); }
    
    /* POWER FLOW */
    .power-svg { width: 100%; height: 100%; min-height: 150px; }
    .node-box { fill: var(--panel); stroke: var(--border); stroke-width: 2; }
    .node-solar { fill: #1a3320; stroke: var(--green); stroke-width: 2; }
    .node-gas { fill: #2a2515; stroke: var(--yellow); stroke-width: 2; }
    .node-ev { fill: #251a33; stroke: var(--purple); stroke-width: 2; }
    .node-ldu { fill: #1a2533; stroke: var(--blue); stroke-width: 2; }
    .node-load { fill: #331a1a; stroke: var(--red); stroke-width: 2; }
    .node-text { fill: var(--text); font-size: 9px; text-anchor: middle; font-weight: bold; }
    .node-label { fill: var(--dim); font-size: 8px; text-anchor: middle; }
    .flow-line { stroke: var(--green); stroke-width: 3; stroke-dasharray: 8,4; animation: dash 1s linear infinite; opacity: 0.7; }
    @keyframes dash { to { stroke-dashoffset: -12; } }
    .flow-loss { fill: var(--red); font-size: 9px; }
    .batt-bar { fill: var(--purple); }
    .batt-bg { fill: var(--border); }
    
    /* INFOGRAPHIC STYLE */
    .info-box { background: var(--bg); border-radius: 6px; padding: 8px; text-align: center; margin: 4px 0; }
    .info-box.solar { border-left: 3px solid var(--green); }
    .info-box.gas { border-left: 3px solid var(--yellow); }
    .info-box.ev { border-left: 3px solid var(--purple); }
    .info-box.ldu { border-left: 3px solid var(--blue); }
    .info-box.load { border-left: 3px solid var(--red); }
    .info-val { font-size: 18px; font-weight: bold; }
    .info-label { font-size: 9px; color: var(--dim); text-transform: uppercase; }
    
    .mini-gauge { width: 100%; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
    .mini-gauge-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
    .mini-gauge-fill.green { background: var(--green); }
    .mini-gauge-fill.yellow { background: var(--yellow); }
    .mini-gauge-fill.red { background: var(--red); }
    
    /* DISPATCH */
    .dispatch-table { font-size: 11px; }
    .dispatch-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); }
    .dispatch-row .val { font-weight: bold; }
    .dispatch-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .disp-card { background: var(--bg); padding: 8px; border-radius: 4px; text-align: center; }
    .disp-card .val { font-size: 16px; font-weight: bold; }
    .disp-card .lbl { font-size: 9px; color: var(--dim); }
    .disp-card.green .val { color: var(--green); }
    .disp-card.red .val { color: var(--red); }
    .disp-card.yellow .val { color: var(--yellow); }
    .disp-card.blue .val { color: var(--blue); }
    .events { max-height: 120px; overflow-y: auto; margin-top: 8px; font-size: 10px; }
    .event { padding: 3px 0; border-bottom: 1px solid var(--border); color: var(--dim); }
    .event.error { color: var(--red); }
    .event.warn { color: var(--yellow); }
    .event.shock { color: var(--red); font-weight: bold; }
    
    /* CHARTS */
    .chart-box { width: 100%; height: 100%; background: var(--bg); border-radius: 4px; }
    
    /* GAUGES */
    .gauge-row { display: flex; gap: 10px; margin-bottom: 10px; }
    .gauge { flex: 1; background: var(--bg); padding: 10px; border-radius: 4px; text-align: center; }
    .gauge-val { font-size: 24px; font-weight: bold; }
    .gauge-val.green { color: var(--green); }
    .gauge-val.yellow { color: var(--yellow); }
    .gauge-val.red { color: var(--red); }
    .gauge-lbl { font-size: 9px; color: var(--dim); }
    .threats { font-size: 10px; }
    .threat { background: rgba(239,68,68,0.1); border-left: 2px solid var(--red); padding: 4px 8px; margin-bottom: 4px; }
    
    /* BRAIN */
    .brain-card { background: var(--bg); padding: 10px; border-radius: 4px; margin-bottom: 10px; }
    .policy-name { font-size: 12px; font-weight: bold; color: var(--cyan); }
    .policy-reason { font-size: 10px; color: var(--dim); margin-top: 4px; }
    .score-breakdown { font-size: 10px; }
    .score-row { display: flex; justify-content: space-between; padding: 2px 0; }
    .score-pos { color: var(--green); }
    .score-neg { color: var(--red); }
    .score-total { border-top: 1px solid var(--border); padding-top: 6px; font-size: 14px; font-weight: bold; }
  </style>
</head>
<body>
  <!-- TOP BAR -->
  <div class="topbar">
    <div class="logo">⚡ <span>GRID OPS</span> COMMAND CENTER</div>
    <div class="kpi-bar">
      <div class="kpi"><div class="lbl">Timestep</div><div class="val" id="kStep">0/0</div></div>
      <div class="kpi"><div class="lbl">Scenario</div><div class="val" id="kScenario">-</div></div>
      <div class="kpi"><div class="lbl">Status</div><div class="val" id="kStatus"><span class="live-dot"></span></div></div>
      <div class="kpi"><div class="lbl">Reward</div><div class="val green" id="kReward">0.00</div></div>
    </div>
  </div>
  
  <!-- MAIN GRID -->
  <div class="grid">
    <!-- MARKET -->
    <div class="panel">
      <div class="panel-title">💰 MARKET INTELLIGENCE</div>
      <div class="bid-ladder">
        <div class="ladder-col">
          <div class="ladder-head">SUPPLY</div>
          <div id="supplyBids"></div>
        </div>
        <div class="ladder-col">
          <div class="ladder-head">DEMAND</div>
          <div id="demandBids"></div>
        </div>
      </div>
      <div class="clearing-box">
        <div class="clearing-price" id="clearingPrice">$0</div>
        <div class="lbl" id="clearingMW">0 MW @</div>
      </div>
    </div>
    
    <!-- POWER FLOW -->
    <div class="panel">
      <div class="panel-title">⚡ POWER FLOW DIGITAL TWIN</div>
      <svg class="power-svg" viewBox="0 0 380 140">
        <!-- Solar -->
        <g transform="translate(30, 25)">
          <rect x="0" y="0" width="50" height="45" rx="4" class="node-solar"/>
          <text x="25" y="15" class="node-text">☀️ SOLAR</text>
          <text x="25" y="32" class="node-text" id="nodeRenew" fill="#22c55e" font-size="14">0</text>
          <text x="25" y="60" class="node-label">MW</text>
        </g>
        
        <!-- Gas -->
        <g transform="translate(100, 25)">
          <rect x="0" y="0" width="50" height="45" rx="4" class="node-gas"/>
          <text x="25" y="15" class="node-text">🏭 GAS</text>
          <text x="25" y="32" class="node-text" id="nodePeaker" fill="#eab308" font-size="14">0</text>
          <text x="25" y="60" class="node-label">MW</text>
        </g>
        
        <!-- EV -->
        <g transform="translate(30, 90)">
          <rect x="0" y="0" width="50" height="45" rx="4" class="node-ev"/>
          <text x="25" y="15" class="node-text">🔋 EV</text>
          <text x="25" y="32" class="node-text" id="nodeEV" fill="#a855f7" font-size="14">0%</text>
          <text x="25" y="60" class="node-label">BATTERY</text>
        </g>
        
        <!-- LDU -->
        <g transform="translate(170, 55)">
          <rect x="0" y="0" width="55" height="50" rx="4" class="node-ldu"/>
          <text x="27" y="15" class="node-text">⚡ LDU</text>
          <text x="27" y="35" class="node-text" id="nodeLDU" fill="#3b82f6" font-size="16">0</text>
          <text x="27" y="65" class="node-label">NET MW</text>
        </g>
        
        <!-- Load -->
        <g transform="translate(310, 55)">
          <rect x="0" y="0" width="55" height="50" rx="4" class="node-load"/>
          <text x="27" y="15" class="node-text">🏭 LOAD</text>
          <text x="27" y="35" class="node-text" id="nodeLoad" fill="#ef4444" font-size="16">0</text>
          <text x="27" y="65" class="node-label">MW DEMAND</text>
        </g>
        
        <!-- Flow Lines -->
        <path d="M80,47 L100,47" class="flow-line" stroke="#22c55e"/>
        <path d="M150,47 L170,80" class="flow-line" stroke="#eab308"/>
        <path d="M80,112 L80,90 L170,90" class="flow-line" stroke="#a855f7"/>
        <path d="M225,80 L310,80" class="flow-line" stroke="#3b82f6"/>
        
        <!-- Loss -->
        <text x="240" y="60" class="flow-loss" id="nodeLoss">⚡ Loss: 0 MW</text>
      </svg>
      
      <!-- Info boxes row -->
      <div style="display:flex;gap:8px;margin-top:8px">
        <div class="info-box solar" style="flex:1">
          <div class="info-val" id="infoRenew" style="color:var(--green)">0</div>
          <div class="info-label">Solar MW</div>
        </div>
        <div class="info-box gas" style="flex:1">
          <div class="info-val" id="infoGas" style="color:var(--yellow)">0</div>
          <div class="info-label">Gas MW</div>
        </div>
        <div class="info-box ev" style="flex:1">
          <div class="info-val" id="infoEV" style="color:var(--purple)">0%</div>
          <div class="info-label">EV SOC</div>
        </div>
        <div class="info-box ldu" style="flex:1">
          <div class="info-val" id="infoNet" style="color:var(--blue)">0</div>
          <div class="info-label">Net MW</div>
        </div>
      </div>
    </div>
    
    <!-- DISPATCH -->
    <div class="panel">
      <div class="panel-title">🔧 LDU DISPATCH</div>
      <div class="dispatch-grid">
        <div class="disp-card green">
          <div class="val" id="dSolar">0</div>
          <div class="lbl">☀️ Solar</div>
        </div>
        <div class="disp-card yellow">
          <div class="val" id="dGas">0</div>
          <div class="lbl">🏭 Gas</div>
        </div>
        <div class="disp-card purple">
          <div class="val" id="dEV">0</div>
          <div class="lbl">🔋 EV</div>
        </div>
        <div class="disp-card blue">
          <div class="val" id="dNet">0</div>
          <div class="lbl">⚡ NET</div>
        </div>
      </div>
      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div class="disp-card">
          <div class="val yellow" id="dLoss">0</div>
          <div class="lbl">📉 Loss</div>
        </div>
        <div class="disp-card">
          <div class="val red" id="dUnmet">0</div>
          <div class="lbl">⚠️ Unmet</div>
        </div>
      </div>
      <div class="events" id="eventLog" style="margin-top:10px"></div>
    </div>
    
    <!-- STABILITY -->
    <div class="panel">
      <div class="panel-title">📈 STABILITY ANALYTICS</div>
      <canvas id="historyChart" class="chart-box"></canvas>
    </div>
    
    <!-- SHOCK -->
    <div class="panel">
      <div class="panel-title">⚠️ SHOCK / RISK</div>
      <div class="gauge-row">
        <div class="gauge"><div class="gauge-val green" id="blackoutRisk">0%</div><div class="gauge-lbl">Blackout Risk</div></div>
        <div class="gauge"><div class="gauge-val green" id="gridStress">0%</div><div class="gauge-lbl">Grid Stress</div></div>
      </div>
      <div class="threats" id="threatList"></div>
    </div>
    
    <!-- BRAIN -->
    <div class="panel">
      <div class="panel-title">🧠 RL DECISION</div>
      <div class="brain-card">
        <div class="policy-name" id="policyName">ADAPTIVE POLICY</div>
        <div class="policy-reason" id="policyReason">Analyzing grid state...</div>
      </div>
      <div class="score-breakdown" id="scoreBreakdown"></div>
    </div>
  </div>
  
  <!-- CONTROLS -->
  <div class="controls">
    <select id="taskSel" class="btn">
      <option value="default">Default</option>
      <option value="long_horizon">Long Horizon</option>
      <option value="stress_shock">Stress Shock</option>
    </select>
    <select id="polSel" class="btn">
      <option value="adaptive">Smart</option>
      <option value="heuristic">Heuristic</option>
      <option value="random">Random</option>
    </select>
    <button class="btn primary" id="resetBtn">🔄 NEW RUN</button>
    <button class="btn" id="stepBtn">STEP</button>
    <button class="btn" id="playBtn">▶ RUN</button>
    <button class="btn" id="pauseBtn">⏹ STOP</button>
    <button class="btn danger" id="shockBtn">⚡ SHOCK</button>
  </div>

<script>
const API = '';
let sessionId = null, timer = null;
const historyData = [];

const cvs = document.getElementById('historyChart');
const ctx = cvs.getContext('2d');
const dpr = window.devicePixelRatio || 1;

function resize() {
  const r = cvs.parentElement.getBoundingClientRect();
  cvs.width = r.width * dpr; cvs.height = r.height * dpr;
  cvs.style.width = r.width + 'px'; cvs.style.height = r.height + 'px';
  ctx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();

function log(msg, type='') {
  const el = document.getElementById('eventLog');
  el.insertBefore(Object.assign(document.createElement('div'), {className: 'event ' + type, innerHTML: `T${document.getElementById('kStep').textContent.split('/')[0]}: ${msg}`}), el.firstChild);
  while (el.children.length > 20) el.lastChild.remove();
}

async function api(path, body) {
  const opts = {method: body ? 'POST' : 'GET'};
  if (body) { opts.headers = {'Content-Type': 'application/json'}; opts.body = JSON.stringify(body); }
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function updateBidLadder(renew, peak, demand) {
  document.getElementById('supplyBids').innerHTML = `
    <div class="bid-row solar"><span>Solar</span><span>${Math.round(renew)}@$20</span></div>
    <div class="bid-row peaker"><span>Gas</span><span>${Math.round(peak)}@$55</span></div>
  `;
  document.getElementById('demandBids').innerHTML = `
    <div class="bid-row demand"><span>Factory</span><span>${Math.round(demand)}@$85</span></div>
  `;
}

function updatePowerFlow(renew, peak, ev, delivered, loss) {
  // SVG nodes
  document.getElementById('nodeRenew').textContent = Math.round(renew);
  document.getElementById('nodePeaker').textContent = Math.round(peak);
  document.getElementById('nodeEV').textContent = ev > 0 ? Math.round(ev) + '⚡' : '0';
  document.getElementById('nodeLDU').textContent = Math.round(delivered);
  document.getElementById('nodeLoad').textContent = Math.round(delivered);
  document.getElementById('nodeLoss').textContent = '⚡ Loss: ' + loss.toFixed(1) + ' MW';
  
  // Info boxes
  document.getElementById('infoRenew').textContent = Math.round(renew);
  document.getElementById('infoGas').textContent = Math.round(peak);
  document.getElementById('infoEV').textContent = ev > 0 ? Math.round(ev) + '⚡' : '0';
  document.getElementById('infoNet').textContent = Math.round(delivered);
}

function updateDispatch(d) {
  document.getElementById('dSolar').textContent = d.renewable_dispatch_mwh.toFixed(0);
  document.getElementById('dGas').textContent = d.peaker_dispatch_mwh.toFixed(0);
  document.getElementById('dEV').textContent = d.ev_discharge_mwh.toFixed(1);
  document.getElementById('dLoss').textContent = d.transmission_loss_mwh.toFixed(1);
  document.getElementById('dNet').textContent = d.delivered_supply_mwh.toFixed(0);
  document.getElementById('dUnmet').textContent = d.unmet_demand_mwh.toFixed(0);
  if (d.corrections && d.corrections.length > 0) {
    d.corrections.forEach(c => log(c, 'warn'));
  }
}

function updateRisk(supply, demand) {
  const stress = Math.max(0, (demand - supply) / demand * 100);
  const blackout = Math.max(0, demand - supply) / demand * 100;
  
  const stEl = document.getElementById('gridStress');
  stEl.textContent = stress.toFixed(0) + '%';
  stEl.className = 'gauge-val ' + (stress < 20 ? 'green' : stress < 50 ? 'yellow' : 'red');
  
  const boEl = document.getElementById('blackoutRisk');
  boEl.textContent = blackout.toFixed(0) + '%';
  boEl.className = 'gauge-val ' + (blackout < 5 ? 'green' : blackout < 20 ? 'yellow' : 'red');
}

function updateScore(r) {
  document.getElementById('scoreBreakdown').innerHTML = `
    <div class="score-row"><span>Reliability</span><span class="score-pos">+${r.demand_satisfaction_score.toFixed(2)}</span></div>
    <div class="score-row"><span>Economic</span><span class="score-pos">+${r.cost_efficiency_score.toFixed(2)}</span></div>
    <div class="score-row"><span>Green</span><span class="score-pos">+${r.renewable_utilization_score.toFixed(2)}</span></div>
    <div class="score-row"><span>Penalties</span><span class="score-neg">-${(r.infeasibility_penalty + r.blackout_penalty).toFixed(2)}</span></div>
    <div class="score-row score-total"><span>TOTAL</span><span>${r.score.toFixed(2)}</span></div>
  `;
}

function drawChart() {
  const w = cvs.width / dpr, h = cvs.height / dpr;
  ctx.fillStyle = '#0a0e12';
  ctx.fillRect(0, 0, w, h);
  if (historyData.length < 2) return;
  
  const max = Math.max(...historyData.map(x => x.demand), ...historyData.map(x => x.supply), 150) * 1.1;
  const step = w / Math.max(1, historyData.length - 1);
  
  ctx.strokeStyle = '#3b82f6'; ctx.lineWidth = 1.5;
  ctx.beginPath();
  historyData.forEach((d, i) => { if (i===0) ctx.moveTo(i*step, h - (d.demand/max)*h*0.9); else ctx.lineTo(i*step, h - (d.demand/max)*h*0.9); });
  ctx.stroke();
  
  ctx.fillStyle = 'rgba(34,197,94,0.2)';
  ctx.beginPath();
  ctx.moveTo(0, h);
  historyData.forEach((d, i) => ctx.lineTo(i*step, h - (d.supply/max)*h*0.9));
  ctx.lineTo(w, h);
  ctx.fill();
  ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 1.5;
  ctx.beginPath();
  historyData.forEach((d, i) => { if (i===0) ctx.moveTo(i*step, h - (d.supply/max)*h*0.9); else ctx.lineTo(i*step, h - (d.supply/max)*h*0.9); });
  ctx.stroke();
}

async function reset() {
  const task = document.getElementById('taskSel').value;
  const data = await api('/reset', {task_id: task, seed: 42});
  sessionId = data.session_id;
  historyData.length = 0;
  document.getElementById('kScenario').textContent = task.toUpperCase();
  document.getElementById('kStatus').innerHTML = '<span class="live-dot"></span> RUNNING';
  document.getElementById('eventLog').innerHTML = '';
  log('Simulation started: ' + task);
}

async function step() {
  if (!sessionId) { await reset(); return; }
  const st = await api('/state?session_id=' + sessionId);
  if (st.episode_done) {
    document.getElementById('kStatus').textContent = 'COMPLETE';
    pause(); return;
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
  
  document.getElementById('kStep').textContent = (obs.step + 1) + '/' + obs.max_steps;
  document.getElementById('kReward').textContent = res.reward.score.toFixed(2);
  
  updateBidLadder(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, d);
  document.getElementById('clearingPrice').textContent = '$' + Math.round(mkt.clearing_price || 0);
  document.getElementById('clearingMW').textContent = (mkt.cleared_mwh || 0).toFixed(0) + ' MW';
  
  updatePowerFlow(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, disp.ev_discharge_mwh, disp.delivered_supply_mwh, disp.transmission_loss_mwh);
  updateDispatch(disp);
  
  historyData.push({demand: d, supply: disp.delivered_supply_mwh});
  drawChart();
  
  updateRisk(disp.delivered_supply_mwh, d);
  
  const rew = res.reward;
  document.getElementById('policyName').textContent = pol.toUpperCase() + ' POLICY';
  document.getElementById('policyReason').textContent = scarcity > 0.3 ? 'High scarcity - Emergency dispatch' : 'Balanced operation';
  updateScore(rew);
  
  if (obs.shock_active) {
    log('⚡ SHOCK!', 'shock');
    document.getElementById('threatList').innerHTML = '<div class="threat">⚡ Renewable drop detected!</div>';
  }
}

function play() { pause(); timer = setInterval(step, 400); }
function pause() { if (timer) clearInterval(timer); timer = null; }
async function shock() {
  if (!sessionId) return;
  await api('/inject-shock', {renewable_drop_mwh: 25});
  log('⚡ MANUAL SHOCK', 'shock');
  document.getElementById('threatList').innerHTML = '<div class="threat">⚡ Manual shock: -25 MW</div>';
}

document.getElementById('resetBtn').onclick = () => { pause(); reset(); };
document.getElementById('stepBtn').onclick = () => { pause(); step(); };
document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('shockBtn').onclick = shock;

reset();
</script>
</body>
</html>
"""