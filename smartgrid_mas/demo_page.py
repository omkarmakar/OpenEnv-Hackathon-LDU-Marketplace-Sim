def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>SmartGrid - Energy Market Simulator</title>
  <style>
    :root { --bg: #0d1117; --panel: #161b22; --border: #30363d; --text: #c9d1d9; --muted: #8b949e; --green: #3fb950; --red: #f85149; --yellow: #d29922; --blue: #58a6ff; --purple: #a371f7; --cyan: #39d0d6; --orange: #f0883e; }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    
    .topbar { background: linear-gradient(90deg, #1a2a1a, #0d1117, #1a2a1a); padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
    .logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
    .logo span { color: var(--green); }
    .status-pill { background: var(--panel); padding: 4px 12px; border-radius: 20px; font-size: 12px; display: flex; align-items: center; gap: 6px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); }
    
    .controls { background: var(--panel); padding: 10px 16px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; border-bottom: 1px solid var(--border); }
    select, button { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 14px; border-radius: 6px; font-size: 13px; cursor: pointer; }
    button { font-weight: 600; }
    button:hover { background: var(--border); }
    button.primary { background: var(--green); color: var(--bg); border: none; }
    button.danger { background: var(--red); color: white; border: none; }
    
    .main { display: grid; grid-template-columns: 1fr 340px; gap: 12px; padding: 12px; }
    .left-panel { display: grid; grid-template-rows: auto auto 1fr; gap: 12px; }
    .right-panel { display: flex; flex-direction: column; gap: 12px; }
    
    .card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
    .card-title { font-size: 11px; text-transform: uppercase; color: var(--muted); letter-spacing: 0.5px; margin-bottom: 10px; font-weight: 600; }
    
    .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .kpi { background: var(--bg); border-radius: 8px; padding: 12px; text-align: center; }
    .kpi-label { font-size: 10px; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 700; }
    .kpi-value.green { color: var(--green); }
    .kpi-value.red { color: var(--red); }
    .kpi-value.yellow { color: var(--yellow); }
    .kpi-value.blue { color: var(--blue); }
    .kpi-value.purple { color: var(--purple); }
    
    .energy-flow { display: flex; align-items: center; justify-content: space-around; padding: 16px; background: var(--bg); border-radius: 8px; }
    .flow-box { text-align: center; }
    .flow-icon { font-size: 32px; }
    .flow-name { font-size: 11px; color: var(--muted); margin: 4px 0 2px; }
    .flow-value { font-size: 20px; font-weight: 700; }
    .flow-arrow { font-size: 20px; color: var(--muted); }
    .flow-arrow.charging { color: var(--green); }
    .flow-arrow.discharging { color: var(--red); }
    
    .battery-viz { display: flex; gap: 2px; height: 60px; align-items: flex-end; justify-content: center; padding: 10px; background: var(--bg); border-radius: 8px; }
    .bat-cell { width: 30px; background: var(--border); opacity: 0.3; border-radius: 2px; }
    .bat-cell.filled { opacity: 1; }
    .bat-cell.danger { background: var(--red); }
    .bat-cell.warn { background: var(--yellow); }
    .bat-cell.good { background: var(--green); }
    .bat-cell.full { background: var(--purple); }
    .bat-labels { display: flex; justify-content: space-between; font-size: 9px; color: var(--muted); margin-top: 4px; }
    
    .bid-table { font-size: 13px; }
    .bid-row { display: flex; justify-content: space-between; padding: 8px; background: var(--bg); border-radius: 6px; margin-bottom: 4px; align-items: center; }
    .bid-row .dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
    .bid-row .amt { font-weight: 700; }
    .bid-row .price { color: var(--muted); font-size: 12px; }
    
    .reward-row { display: flex; justify-content: space-between; font-size: 12px; padding: 3px 0; }
    .reward-row .label { color: var(--muted); }
    .reward-row .val { font-weight: 600; }
    .reward-row .pos { color: var(--green); }
    .reward-row .neg { color: var(--red); }
    .reward-total { border-top: 1px solid var(--border); margin-top: 6px; padding-top: 6px; font-weight: 700; font-size: 14px; }
    
    .chart-area { height: 120px; background: var(--bg); border-radius: 8px; position: relative; }
    .chart-area canvas { width: 100%; height: 100%; }
    
    .simple-log { font-size: 11px; max-height: 100px; overflow-y: auto; }
    .simple-log div { padding: 4px 6px; color: var(--muted); border-bottom: 1px solid var(--border); }
    
    .explanation { font-size: 12px; line-height: 1.5; color: var(--text); }
    .explanation .highlight { background: var(--bg); padding: 8px; border-radius: 6px; border-left: 3px solid var(--blue); margin-top: 6px; }
    
    .warning-box { background: rgba(248, 81, 73, 0.15); border: 1px solid var(--red); border-radius: 6px; padding: 8px; font-size: 12px; color: var(--red); display: none; }
    .warning-box.show { display: block; }
    
    @media (max-width: 900px) { .main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class='topbar'>
    <div class='logo'>⚡ <span>SmartGrid</span></div>
    <div class='status-pill'><div class='status-dot'></div><span id='connStatus'>Ready</span></div>
  </div>
  
  <div class='controls'>
    <select id='task'><option value='default'>Default (24 steps)</option><option value='long_horizon'>Long Horizon (48)</option><option value='stress_shock'>Stress Shock (30)</option></select>
    <select id='policy'><option value='adaptive'>Smart Policy</option><option value='heuristic'>Rule Policy</option><option value='random'>Random</option></select>
    <button id='resetBtn' class='primary'>🔄 New Game</button>
    <button id='stepBtn'>Step ▶</button>
    <button id='playBtn'>▶▶ Auto Run</button>
    <button id='pauseBtn'>⏸ Stop</button>
    <button id='shockBtn' class='danger'>⚡ Add Shock</button>
    <select id='speed'><option value='80'>Fast</option><option value='300'>Normal</option><option value='800'>Slow</option></select>
  </div>
  
  <div class='main'>
    <div class='left-panel'>
      <div class='card'>
        <div class='card-title'>⚡ Energy Balance</div>
        <div class='kpi-grid'>
          <div class='kpi'><div class='kpi-label'>Demand</div><div class='kpi-value blue' id='kDemand'>0</div></div>
          <div class='kpi'><div class='kpi-label'>Supply</div><div class='kpi-value green' id='kSupply'>0</div></div>
          <div class='kpi'><div class='kpi-label'>Score</div><div class='kpi-value' id='kScore'>0.00</div></div>
        </div>
      </div>
      
      <div class='card'>
        <div class='card-title'>🔋 EV Battery (20% - 80%)</div>
        <div class='battery-viz' id='batteryViz'></div>
        <div class='bat-labels'><span>0%</span><span>20%</span><span>80%</span><span>100%</span></div>
        <div class='warning-box' id='batteryWarning'>⚠️ Battery hit limit!</div>
      </div>
      
      <div class='card'>
        <div class='card-title'>📈 Supply vs Demand</div>
        <div class='chart-area'><canvas id='mainChart'></canvas></div>
      </div>
    </div>
    
    <div class='right-panel'>
      <div class='card'>
        <div class='card-title'>💰 Market Bids</div>
        <div class='bid-table' id='bidTable'></div>
      </div>
      
      <div class='card'>
        <div class='card-title'>📊 How Score Works</div>
        <div class='reward-row'><span class='label'>Satisfaction</span><span class='val pos' id='rSatisf'>+0.00</span></div>
        <div class='reward-row'><span class='label'>Cost Savings</span><span class='val pos' id='rCost'>+0.00</span></div>
        <div class='reward-row'><span class='label'>Green Energy</span><span class='val pos' id='rGreen'>+0.00</span></div>
        <div class='reward-row'><span class='label'>Stability</span><span class='val pos' id='rStable'>+0.00</span></div>
        <div class='reward-row'><span class='label'>Corrections</span><span class='val neg' id='rPenalty'>-0.00</span></div>
        <div class='reward-row'><span class='label'>Blackouts</span><span class='val neg' id='rBlackout'>-0.00</span></div>
        <div class='reward-row total'><span class='label'>TOTAL SCORE</span><span class='val' id='rTotal'>0.00</span></div>
      </div>
      
      <div class='card'>
        <div class='card-title'>📜 What Happened</div>
        <div class='simple-log' id='activityLog'></div>
      </div>
    </div>
  </div>

<script>
const API = '';
let sessionId = null, timer = null, obsCache = null;
const rewardData = [], supplyData = [], demandData = [];

const canvas = document.getElementById('mainChart');
const ctx = canvas.getContext('2d');
const dpr = window.devicePixelRatio || 1;

function resize() {
  const rc = canvas.parentElement.getBoundingClientRect();
  canvas.width = rc.width * dpr; canvas.height = 120 * dpr;
  canvas.style.width = rc.width + 'px'; canvas.style.height = '120px';
  ctx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();

function drawBattery(socPct) {
  const el = document.getElementById('batteryViz');
  const cells = 10;
  const filled = Math.floor(socPct / 10);
  let html = '';
  for (let i = 0; i < cells; i++) {
    let cls = 'bat-cell';
    if (i < filled) {
      cls += ' filled';
      if (socPct < 25) cls += ' danger';
      else if (socPct < 40) cls += ' warn';
      else if (socPct < 70) cls += ' good';
      else cls += ' full';
    }
    html += '<div class="' + cls + '"></div>';
  }
  el.innerHTML = html;
  
  const warn = document.getElementById('batteryWarning');
  warn.className = socPct <= 22 || socPct >= 78 ? 'warning-box show' : 'warning-box';
}

function drawChart() {
  const w = canvas.width / dpr, h = canvas.height / dpr;
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, w, h);
  if (supplyData.length < 2) return;
  
  const max = Math.max(...demandData, ...supplyData, 150);
  const step = w / Math.max(1, supplyData.length - 1);
  
  // Supply area
  ctx.beginPath();
  ctx.moveTo(0, h);
  supplyData.forEach((v, i) => ctx.lineTo(i * step, h - (v / max) * h * 0.9));
  ctx.lineTo(w, h);
  ctx.fillStyle = 'rgba(63, 185, 80, 0.2)';
  ctx.fill();
  
  // Supply line
  ctx.strokeStyle = '#3fb950';
  ctx.lineWidth = 2;
  ctx.beginPath();
  supplyData.forEach((v, i) => { if (i===0) ctx.moveTo(i*step, h-(v/max)*h*0.9); else ctx.lineTo(i*step, h-(v/max)*h*0.9); });
  ctx.stroke();
  
  // Demand line
  ctx.strokeStyle = '#58a6ff';
  ctx.beginPath();
  demandData.forEach((v, i) => { if (i===0) ctx.moveTo(i*step, h-(v/max)*h*0.9); else ctx.lineTo(i*step, h-(v/max)*h*0.9); });
  ctx.stroke();
}

function log(msg) {
  const el = document.getElementById('activityLog');
  const div = document.createElement('div');
  div.textContent = msg;
  el.insertBefore(div, el.firstChild);
}

async function api(path, body) {
  const opts = {method: body ? 'POST' : 'GET'};
  if (body) { opts.headers = {'Content-Type': 'application/json'}; opts.body = JSON.stringify(body); }
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function updateKPIs(data) {
  document.getElementById('kDemand').textContent = Math.round(data.demand || 0);
  document.getElementById('kSupply').textContent = Math.round(data.supply || 0);
  document.getElementById('kScore').textContent = (data.reward || 0).toFixed(2);
  document.getElementById('kScore').className = 'kpi-value ' + (data.reward > 0.5 ? 'green' : data.reward > 0.3 ? 'yellow' : 'red');
}

function updateReward(r) {
  document.getElementById('rSatisf').textContent = '+' + (r.demand_satisfaction_score || 0).toFixed(2);
  document.getElementById('rCost').textContent = '+' + (r.cost_efficiency_score || 0).toFixed(2);
  document.getElementById('rGreen').textContent = '+' + (r.renewable_utilization_score || 0).toFixed(2);
  document.getElementById('rStable').textContent = '+' + (r.stability_score || 0).toFixed(2);
  document.getElementById('rPenalty').textContent = '-' + (r.infeasibility_penalty || 0).toFixed(2);
  document.getElementById('rBlackout').textContent = '-' + (r.blackout_penalty || 0).toFixed(2);
  document.getElementById('rTotal').textContent = (r.score || 0).toFixed(2);
}

function updateBids(action) {
  const colors = {'renewable_prosumer': '#3fb950', 'peaker_plant': '#f0883e', 'industrial_load': '#58a6ff', 'ev': '#a371f7'};
  const names = {'renewable_prosumer': 'Solar/Wind', 'peaker_plant': 'Gas Plant', 'industrial_load': 'Factory', 'ev': 'EV Battery'};
  let html = '';
  action.bids.forEach(b => {
    html += '<div class="bid-row"><div class="dot" style="background:' + colors[b.role] + '"></div><span>' + (names[b.role] || b.role) + '</span><div><span class="amt">' + Math.round(b.quantity_mwh) + '</span> <span class="price">@ $' + Math.round(b.price_usd_per_mwh) + '</span></div></div>';
  });
  const ev = action.ev_charge_mwh || 0, evd = action.ev_discharge_mwh || 0;
  if (ev > 0 || evd > 0) {
    html += '<div class="bid-row"><div class="dot" style="background:#a371f7"></div><span>EV ⚡</span><div><span class="amt">' + ev.toFixed(1) + '/' + evd.toFixed(1) + '</span> <span class="price">MWh</span></div></div>';
  }
  document.getElementById('bidTable').innerHTML = html;
}

async function reset() {
  rewardData.length = supplyData.length = demandData.length = 0;
  drawChart();
  
  const task = document.getElementById('task').value;
  const data = await api('/reset', {task_id: task, seed: 42});
  sessionId = data.session_id;
  obsCache = data.observation;
  
  const cap = obsCache.ev_storage_capacity_mwh;
  const soc = obsCache.ev_storage_mwh / cap * 100;
  drawBattery(soc);
  log('New game: ' + task);
  
  updateKPIs({demand: obsCache.demand_mwh, supply: 0, reward: 0});
  document.getElementById('bidTable').innerHTML = 'Ready...';
}

async function step() {
  if (!sessionId) { await reset(); return; }
  const st = await api('/state?session_id=' + sessionId);
  if (st.episode_done) { log('Done! Score: ' + document.getElementById('kScore').textContent); pause(); return; }
  
  const obs = st.observation;
  const policy = document.getElementById('policy').value;
  const d = obs.demand_mwh, r = obs.renewable_availability_mwh, p = obs.peaker_capacity_mwh;
  const leader = obs.leader_price_signal, scarcity = obs.scarcity_index || 0;
  const storage = obs.ev_storage_mwh, cap = obs.ev_storage_capacity_mwh;
  
  let renQty, peakQty, peakPrice, evC, evD;
  if (policy === 'adaptive') {
    renQty = Math.min(r, d * (0.52 + 0.18 * (1 - scarcity)));
    peakQty = Math.min(p, (d - renQty) * (1 + 0.25 * scarcity));
    peakPrice = leader * 1.1;
    const soc = storage / cap;
    if (soc <= 0.35) { evC = Math.min(cap * 0.8 - storage, 5); evD = 0; }
    else if (soc <= 0.5) { evC = scarcity > 0.4 ? 0 : Math.min(cap * 0.8 - storage, 3); evD = scarcity > 0.4 ? Math.min(storage - cap * 0.2, 2 + 4 * scarcity) : 0; }
    else { evC = 0; evD = scarcity > 0.2 ? Math.min(storage - cap * 0.2, 4 + 5 * scarcity) : 0; }
  } else if (policy === 'heuristic') {
    renQty = Math.min(r, d * 0.55); peakQty = Math.min(p, d - renQty); peakPrice = leader * 1.02;
    evC = r > d ? 3 : 0; evD = r < d * 0.8 ? 2 : 0;
  } else {
    renQty = Math.min(r, d * 0.5 + Math.random() * 20);
    peakQty = Math.min(p, d * 0.4);
    peakPrice = 45 + Math.random() * 20;
    evC = Math.random() > 0.6 ? 2 : 0; evD = Math.random() > 0.6 ? 2 : 0;
  }
  
  const action = {action: {bids: [
    {agent_id:'s', role:'renewable_prosumer', bid_type:'supply', quantity_mwh:Math.max(0, renQty), price_usd_per_mwh:20},
    {agent_id:'g', role:'peaker_plant', bid_type:'supply', quantity_mwh:Math.max(0, peakQty), price_usd_per_mwh:peakPrice},
    {agent_id:'f', role:'industrial_load', bid_type:'demand', quantity_mwh:d, price_usd_per_mwh:leader * 1.45}
  ], ev_charge_mwh: Math.max(0, evC), ev_discharge_mwh: Math.max(0, evD)}};
  
  updateBids(action.action);
  const res = await api('/step?session_id=' + sessionId, action);
  const info = res.info, mkt = info.market, disp = info.dispatch;
  
  updateReward(res.reward);
  updateKPIs({demand: d, supply: disp.delivered_supply_mwh || 0, reward: res.reward.score});
  
  const soc = (disp.next_ev_storage_mwh || 0) / cap * 100;
  drawBattery(soc);
  
  supplyData.push(disp.delivered_supply_mwh || 0);
  demandData.push(d);
  drawChart();
  
  const msg = 'Step ' + res.observation.step + ': ' + Math.round(d) + '→' + Math.round(disp.delivered_supply_mwh || 0) + ' MW, score=' + res.reward.score.toFixed(2);
  if (disp.correction_count > 0) msg += ' ⚠️';
  log(msg);
}

function play() { pause(); timer = setInterval(step, parseInt(document.getElementById('speed').value)); }
function pause() { if (timer) clearInterval(timer); timer = null; }
async function shock() { if (!sessionId) return; await api('/inject-shock', {renewable_drop_mwh:25}); log('⚡ SHOCK!'); }

document.getElementById('resetBtn').onclick = () => { pause(); reset(); };
document.getElementById('stepBtn').onclick = () => { pause(); step(); };
document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('shockBtn').onclick = shock;

document.getElementById('connStatus').textContent = 'Ready';
reset();
</script>
</body>
</html>
"""