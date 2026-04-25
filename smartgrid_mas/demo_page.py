def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>SmartGrid MarketSim - Agent Debug</title>
  <style>
    :root { --bg: #0f1419; --panel: #1a2332; --border: #2d3a4f; --text: #e4e8ed; --muted: #6b7a8a; --green: #4ade80; --red: #f87171; --yellow: #fbbf24; --blue: #60a5fa; --purple: #a78bfa; --orange: #fb923c; }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    .header { background: var(--panel); padding: 12px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
    .header h1 { margin: 0; font-size: 18px; font-weight: 600; }
    .header .status { font-size: 12px; color: var(--muted); }
    .header .status.ok { color: var(--green); }
    
    .controls { background: var(--panel); padding: 12px 20px; border-bottom: 1px solid var(--border); display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    .control-group { display: flex; align-items: center; gap: 6px; }
    .control-group label { font-size: 12px; color: var(--muted); }
    select, input { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 4px; font-size: 13px; }
    button { background: var(--border); border: none; color: var(--text); padding: 8px 14px; border-radius: 4px; font-size: 13px; cursor: pointer; }
    button:hover { background: #3d4a5f; }
    button.primary { background: var(--green); color: #0f1419; font-weight: 600; }
    button.danger { background: var(--red); color: white; }
    
    .layout { display: grid; grid-template-columns: 1fr 320px; height: calc(100vh - 100px); }
    .left { display: grid; grid-template-rows: 1fr 200px; gap: 12px; padding: 12px; }
    .viz { background: var(--panel); border-radius: 8px; border: 1px solid var(--border); padding: 12px; position: relative; }
    .viz h3 { margin: 0 0 8px 0; font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .metrics-bar { display: flex; gap: 8px; flex-wrap: wrap; }
    .metric-box { flex: 1; min-width: 80px; background: var(--bg); border-radius: 6px; padding: 8px; text-align: center; }
    .metric-box .lbl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
    .metric-box .val { font-size: 18px; font-weight: 700; }
    .metric-box .val.green { color: var(--green); }
    .metric-box .val.red { color: var(--red); }
    .metric-box .val.yellow { color: var(--yellow); }
    .metric-box .val.blue { color: var(--blue); }
    .metric-box .val.orange { color: var(--orange); }
    .metric-box .val.purple { color: var(--purple); }
    
    .right { padding: 12px; display: flex; flex-direction: column; gap: 12px; overflow-y: auto; }
    .card { background: var(--panel); border-radius: 8px; border: 1px solid var(--border); padding: 12px; }
    .card h3 { margin: 0 0 8px 0; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .explanation { font-size: 12px; line-height: 1.5; }
    .explanation .label { color: var(--muted); font-size: 11px; }
    .explanation .value { color: var(--text); }
    .explanation .arrow { color: var(--yellow); margin: 4px 0; }
    .explanation .why { background: var(--bg); padding: 8px; border-radius: 4px; margin-top: 6px; border-left: 3px solid var(--blue); }
    .explanation .why-title { color: var(--blue); font-weight: 600; margin-bottom: 4px; }
    
    .bid-item { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
    .bid-item:last-child { border: none; }
    .bid-item .role { display: flex; align-items: center; gap: 6px; }
    .bid-item .dot { width: 8px; height: 8px; border-radius: 50%; }
    .bid-item .qty { font-weight: 600; }
    .bid-item .price { color: var(--muted); }
    
    .reward-breakdown { font-size: 11px; }
    .reward-row { display: flex; justify-content: space-between; padding: 3px 0; }
    .reward-row .name { color: var(--muted); }
    .reward-row .val { font-weight: 600; }
    .reward-row .val.pos { color: var(--green); }
    .reward-row .val.neg { color: var(--red); }
    .reward-row.total { border-top: 1px solid var(--border); margin-top: 4px; padding-top: 4px; font-weight: 700; }
    
    .event-log { font-size: 11px; max-height: 140px; overflow-y: auto; }
    .event-log div { padding: 4px 0; border-bottom: 1px solid var(--border); color: var(--muted); }
    .event-log .step-num { color: var(--blue); }
    .event-log .reward-val { color: var(--green); }
    .event-log .correction { color: var(--red); }
    .event-log .shock { color: var(--yellow); }
    
    .chart { height: 80px; background: var(--bg); border-radius: 4px; position: relative; }
    .chart canvas { width: 100%; height: 100%; }
    
    @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } .left { grid-template-rows: 1fr 180px; } }
  </style>
</head>
<body>
  <header class='header'>
    <h1>⚡ SmartGrid MarketSim</h1>
    <div class='status' id='connStatus'>Connecting...</div>
  </header>
  
  <div class='controls'>
    <div class='control-group'>
      <label>Task</label>
      <select id='task'>
        <option value='default'>Default</option>
        <option value='long_horizon'>Long Horizon</option>
        <option value='stress_shock'>Stress Shock</option>
      </select>
    </div>
    <div class='control-group'>
      <label>Policy</label>
      <select id='policy'>
        <option value='adaptive'>Adaptive</option>
        <option value='heuristic'>Heuristic</option>
        <option value='random'>Random</option>
      </select>
    </div>
    <div class='control-group'>
      <label>Speed</label>
      <select id='speed'>
        <option value='100'>Fast</option>
        <option value='500' selected>Normal</option>
        <option value='1000'>Slow</option>
      </select>
    </div>
    <button id='resetBtn' class='primary'>🔄 Reset</button>
    <button id='stepBtn'>Step ▶</button>
    <button id='playBtn'>▶▶ Play</button>
    <button id='pauseBtn'>⏸ Pause</button>
    <button id='shockBtn' class='danger'>⚡ Shock</button>
  </div>
  
  <div class='layout'>
    <div class='left'>
      <div class='viz'>
        <h3>Grid State</h3>
        <canvas id='scene'></canvas>
        <div class='metrics-bar'>
          <div class='metric-box'><div class='lbl'>Step</div><div class='val blue' id='mStep'>0</div></div>
          <div class='metric-box'><div class='lbl'>Reward</div><div class='val green' id='mReward'>0.00</div></div>
          <div class='metric-box'><div class='lbl'>Demand</div><div class='val blue' id='mDemand'>0</div></div>
          <div class='metric-box'><div class='lbl'>Supply</div><div class='val green' id='mSupply'>0</div></div>
          <div class='metric-box'><div class='lbl'>Price</div><div class='val yellow' id='mPrice'>$0</div></div>
          <div class='metric-box'><div class='lbl'>Errors</div><div class='val red' id='mErrors'>0</div></div>
        </div>
      </div>
      
      <div class='viz'>
        <h3>Reward History</h3>
        <div class='chart'><canvas id='chart'></canvas></div>
      </div>
    </div>
    
    <div class='right'>
      <div class='card'>
        <h3>🧠 Agent Decision</h3>
        <div class='explanation' id='agentExplain'>
          <div class='label'>Step 0 - Ready to start</div>
          <div class='value'>Press Reset then Play to begin</div>
        </div>
      </div>
      
      <div class='card'>
        <h3>📊 Market Bids</h3>
        <div class='explanation' id='bidList'>
          <div class='label'>No bids yet</div>
        </div>
      </div>
      
      <div class='card'>
        <h3>⚡ What Happened</h3>
        <div class='explanation' id='whatHappened'>
          <div class='label'>Waiting for step...</div>
        </div>
      </div>
      
      <div class='card'>
        <h3>📈 Reward Breakdown</h3>
        <div class='reward-breakdown' id='rewardBreakdown'>
          <div class='reward-row'><span class='name'>No reward yet</span></div>
        </div>
      </div>
      
      <div class='card'>
        <h3>📜 Event Log</h3>
        <div class='event-log' id='log'></div>
      </div>
    </div>
  </div>

<script>
const API = '';
let sessionId = null;
let timer = null;
let rewardHistory = [];
let obsCache = null;

const canvas = document.getElementById('scene');
const ctx = canvas.getContext('2d');
const chartCanvas = document.getElementById('chart');
const chartCtx = chartCanvas.getContext('2d');

function resize() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + 'px'; canvas.style.height = rect.height + 'px';
  ctx.scale(dpr, dpr);
  
  const crc = chartCanvas.getBoundingClientRect();
  chartCanvas.width = crc.width * dpr; chartCanvas.height = crc.height * dpr;
  chartCanvas.style.width = crc.width + 'px'; chartCanvas.style.height = crc.height + 'px';
  chartCtx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();

function drawGrid() {
  const w = canvas.width / dpr, h = canvas.height / dpr;
  ctx.fillStyle = '#1a2332';
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = '#2d3a4f';
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
  for (let y = 0; y < h; y += 30) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
}

const dpr = window.devicePixelRatio || 1;
function render(data) {
  drawGrid();
  const w = canvas.width / dpr, h = canvas.height / dpr;
  const maxH = h - 40, baseY = h - 30;
  
  const d = data.demand || 0, s = data.supply || 0, r = data.renewable || 0, p = data.peaker || 0, st = data.storage || 0;
  const max = Math.max(d, s) * 1.2 || 150;
  const sc = maxH / max;
  
  const barW = 50;
  const draw = (val, x, col, lbl) => {
    if (val <= 0) return;
    ctx.fillStyle = col;
    ctx.fillRect(x, baseY - val*sc, barW, val*sc);
    ctx.fillStyle = '#e4e8ed';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(lbl, x + barW/2, baseY + 14);
    ctx.fillText(val.toFixed(0), x + barW/2, baseY - val*sc - 4);
  };
  
  draw(r, w*0.15, '#4ade80', 'Renew');
  draw(p, w*0.32, '#fb923c', 'Peaker');
  draw(s, w*0.50, '#4ade80', 'Supply');
  draw(d, w*0.68, '#60a5fa', 'Demand');
  
  ctx.fillStyle = '#a78bfa';
  const stH = (st / 60) * maxH * 0.5;
  ctx.fillRect(w*0.85, baseY - stH, barW, stH);
  ctx.fillStyle = '#e4e8ed';
  ctx.fillText('Storage', w*0.85 + barW/2, baseY + 14);
  ctx.fillText((st/60*100).toFixed(0)+'%', w*0.85 + barW/2, baseY - stH - 4);
  
  if (data.shock) {
    ctx.fillStyle = '#f87171';
    ctx.font = 'bold 16px sans-serif';
    ctx.fillText('⚡ SHOCK', w/2, 24);
  }
}

function drawChart() {
  const w = chartCanvas.width / dpr, h = chartCanvas.height / dpr;
  chartCtx.fillStyle = '#0f1419';
  chartCtx.fillRect(0, 0, w, h);
  if (rewardHistory.length < 2) return;
  const max = Math.max(...rewardHistory, 1);
  const step = w / Math.max(1, rewardHistory.length - 1);
  chartCtx.strokeStyle = '#4ade80';
  chartCtx.lineWidth = 2;
  chartCtx.beginPath();
  rewardHistory.forEach((r, i) => {
    const x = i * step, y = h - (r / max) * (h - 10) - 5;
    if (i === 0) chartCtx.moveTo(x, y); else chartCtx.lineTo(x, y);
  });
  chartCtx.stroke();
}

function log(msg, cls='') {
  const el = document.getElementById('log');
  const div = document.createElement('div');
  div.className = cls;
  div.textContent = msg;
  el.insertBefore(div, el.firstChild);
}

async function api(path, body=null) {
  const opts = {method: body ? 'POST' : 'GET'};
  if (body) { opts.headers = {'Content-Type': 'application/json'}; opts.body = JSON.stringify(body); }
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function updateMetrics(data) {
  document.getElementById('mStep').textContent = data.step || 0;
  document.getElementById('mReward').textContent = (data.reward||0).toFixed(3);
  document.getElementById('mDemand').textContent = (data.demand||0).toFixed(0);
  document.getElementById('mSupply').textContent = (data.supply||0).toFixed(0);
  document.getElementById('mPrice').textContent = '$' + (data.price||0).toFixed(0);
  document.getElementById('mErrors').textContent = data.errors || 0;
  
  render(data);
}

function updateRewardBreakdown(rwd) {
  if (!rwd) return;
  const el = document.getElementById('rewardBreakdown');
  el.innerHTML = `
    <div class='reward-row'><span class='name'>Demand Satisfaction</span><span class='val pos'>+${(rwd.demand_satisfaction_score||0).toFixed(2)}</span></div>
    <div class='reward-row'><span class='name'>Cost Efficiency</span><span class='val pos'>+${(rwd.cost_efficiency_score||0).toFixed(2)}</span></div>
    <div class='reward-row'><span class='name'>Renewable Use</span><span class='val pos'>+${(rwd.renewable_utilization_score||0).toFixed(2)}</span></div>
    <div class='reward-row'><span class='name'>Stability</span><span class='val pos'>+${(rwd.stability_score||0).toFixed(2)}</span></div>
    <div class='reward-row'><span class='name'>Infeasibility</span><span class='val neg'>-${(rwd.infeasibility_penalty||0).toFixed(2)}</span></div>
    <div class='reward-row'><span class='name'>Blackout</span><span class='val neg'>-${(rwd.blackout_penalty||0).toFixed(2)}</span></div>
    <div class='reward-row total'><span class='name'>Total</span><span class='val'>${(rwd.score||0).toFixed(3)}</span></div>
  `;
}

function explainAgent(obs, policy, action) {
  const d = obs.demand_mwh, r = obs.renewable_availability_mwh, p = obs.peaker_capacity_mwh;
  const scarcity = obs.scarcity_index || 0;
  const leader = obs.leader_price_signal || 45;
  
  let why = '';
  if (policy === 'adaptive') {
    why = `Adaptive agent sees ${(scarcity*100).toFixed(0)}% scarcity.<br/>`;
    if (scarcity > 0.3) {
      why += `→ High scarcity: bidding aggressively to cover demand<br/>`;
      why += `→ Discharging storage to help balance grid`;
    } else {
      why += `→ Moderate scarcity: balanced supply mix<br/>`;
      why += `→ Charging storage when renewable is abundant`;
    }
    why += `<br/>Bidding at ${leader.toFixed(0)} * ${(1.1).toFixed(1)} = $${(leader*1.1).toFixed(0)} for peaker`;
  } else if (policy === 'heuristic') {
    why = `Heuristic agent uses fixed rules:<br/>`;
    why += `→ 55% from renewable, rest from peaker<br/>`;
    why += `→ Fixed price markup on leader signal`;
  } else {
    why = `Random agent bids randomly:<br/>`;
    why += `→ No strategy, baseline comparison`;
  }
  
  const el = document.getElementById('agentExplain');
  el.innerHTML = `
    <div class='label'>Step ${obs.step} - ${policy.toUpperCase()} Policy</div>
    <div class='value'>
      Demand: <b>${d.toFixed(0)} MWh</b> | Renewable: <b>${r.toFixed(0)} MWh</b><br/>
      Scarcity: <b>${(scarcity*100).toFixed(0)}%</b> | Leader: <b>$${leader.toFixed(0)}</b>
    </div>
    <div class='why'>
      <div class='why-title'>🤔 Why this action?</div>
      ${why}
    </div>
  `;
}

function showBids(action) {
  if (!action) return;
  const el = document.getElementById('bidList');
  const colors = {'renewable_prosumer':'#4ade80','peaker_plant':'#fb923c','industrial_load':'#60a5fa'};
  const names = {'renewable_prosumer':'Renewable','peaker_plant':'Peaker','industrial_load':'Demand'};
  el.innerHTML = action.bids.map(b => `
    <div class='bid-item'>
      <div class='role'><div class='dot' style='background:${colors[b.role]}||#888'></div>${names[b.role]||b.role}</div>
      <div><span class='qty'>${b.quantity_mwh.toFixed(0)} MWh</span> @ <span class='price'>$${b.price_usd_per_mwh.toFixed(0)}</span></div>
    </div>
  `).join('') + `
    <div class='bid-item'>
      <div class='role'><div class='dot' style='background:#a78bfa'></div>EV</div>
      <div>⚡ ${(action.ev_charge_mwh||0).toFixed(0)} / ${(action.ev_discharge_mwh||0).toFixed(0)} MWh</div>
    </div>
  `;
}

function showWhatHappened(info, market) {
  const el = document.getElementById('whatHappened');
  let html = '';
  
  if (market) {
    html += `<div class='label'>Market Clearing</div>`;
    html += `<div class='value'>Cleared: <b>${(market.cleared_mwh||0).toFixed(0)} MWh</b> @ <b>$${(market.clearing_price||0).toFixed(0)}/MWh</b></div>`;
    if (market.leader_adjusted_bids > 0) {
      html += `<div class='arrow'>→ ${market.leader_adjusted_bids} bids adjusted by leader signal</div>`;
    }
  }
  
  if (info && info.dispatch) {
    const disp = info.dispatch;
    html += `<div class='label'>LDU Dispatch</div>`;
    html += `<div class='value'>Delivered: <b>${(disp.delivered_supply_mwh||0).toFixed(0)} MWh</b> (${disp.transmission_loss||0}% loss)</div>`;
    if (disp.correction_count > 0) {
      html += `<div class='arrow'>⚠️ ${disp.correction_count} correction(s): ${(disp.corrections||[]).slice(0,2).join(', ')}</div>`;
    }
  }
  
  el.innerHTML = html || '<div class="label">Waiting for step...</div>';
}

async function reset() {
  rewardHistory.length = 0;
  drawChart();
  const task = document.getElementById('task').value;
  const data = await api('/reset', {task_id: task, seed: 42});
  sessionId = data.session_id;
  obsCache = data.observation;
  
  log(`Reset: ${task}`, 'step-num');
  
  updateMetrics({step:0, reward:0, demand:obsCache.demand_mwh, supply:0, renewable:obsCache.renewable_availability_mwh, peaker:obsCache.peaker_capacity_mwh, storage:obsCache.ev_storage_mwh, price:obsCache.leader_price_signal, errors:0, shock:false});
  
  document.getElementById('agentExplain').innerHTML = `<div class='label'>Step 0 - Ready</div><div class='value'>Task: ${task}, seed=42. Press Play.</div>`;
  document.getElementById('bidList').innerHTML = '<div class="label">No bids yet</div>';
  document.getElementById('whatHappened').innerHTML = '<div class="label">Waiting for step...</div>';
  updateRewardBreakdown(null);
}

async function step() {
  if (!sessionId) { await reset(); return; }
  
  const st = await api('/state?session_id=' + sessionId);
  if (st.episode_done) {
    log('Episode complete!', 'reward-val');
    pause();
    return;
  }
  
  const obs = st.observation;
  const policy = document.getElementById('policy').value;
  const d = obs.demand_mwh, r = obs.renewable_availability_mwh, p = obs.peaker_capacity_mwh, leader = obs.leader_price_signal, storage = obs.ev_storage_mwh, storageCap = obs.ev_storage_capacity_mwh;
  const scarcity = obs.scarcity_index || 0;
  
  // Use proper adaptive policy logic
  let renQty, peakQty, peakPrice, loadPrice, evCharge, evDischarge;
  
  if (policy === 'adaptive') {
    renQty = Math.min(r, d * (0.52 + 0.18 * (1 - scarcity)));
    peakQty = Math.min(p, Math.max(0, d - renQty) * (1 + 0.25 * scarcity));
    peakPrice = leader * 1.1;
    loadPrice = leader * 1.45;
    if (scarcity > 0.25) {
      evDischarge = Math.min(storage, 3 + 8 * scarcity);
      evCharge = 0;
    } else {
      evCharge = Math.min(storageCap - storage, 2);
      evDischarge = 0;
    }
  } else if (policy === 'heuristic') {
    renQty = Math.min(r, d * 0.55);
    peakQty = Math.min(p, d - renQty);
    peakPrice = leader * 1.02;
    loadPrice = 85;
    evCharge = r > d ? 3 : 0;
    evDischarge = r < d * 0.8 ? 2 : 0;
  } else {
    renQty = Math.min(r, d * 0.5 + Math.random() * 20);
    peakQty = Math.min(p, d * 0.4);
    peakPrice = 45 + Math.random() * 20;
    loadPrice = 70 + Math.random() * 20;
    evCharge = Math.random() > 0.5 ? 3 : 0;
    evDischarge = Math.random() > 0.5 ? 2 : 0;
  }
  
  const action = {
    action: {
      bids: [
        {agent_id:'r', role:'renewable_prosumer', bid_type:'supply', quantity_mwh:Math.max(0, renQty), price_usd_per_mwh:20},
        {agent_id:'p', role:'peaker_plant', bid_type:'supply', quantity_mwh:Math.max(0, peakQty), price_usd_per_mwh:peakPrice},
        {agent_id:'i', role:'industrial_load', bid_type:'demand', quantity_mwh:d, price_usd_per_mwh:loadPrice}
      ],
      ev_charge_mwh: Math.max(0, evCharge),
      ev_discharge_mwh: Math.max(0, evDischarge)
    }
  };
  
  showBids(action.action);
  
  const res = await api('/step?session_id=' + sessionId, action);
  const info = res.info || {};
  const market = info.market || {};
  const dispatch = info.dispatch || {};
  
  rewardHistory.push(res.reward.score);
  drawChart();
  
  updateMetrics({
    step: res.observation.step,
    reward: res.reward.score,
    demand: d,
    supply: dispatch.delivered_supply_mwh || 0,
    renewable: dispatch.renewable_dispatch_mwh || 0,
    peaker: dispatch.peaker_dispatch_mwh || 0,
    storage: dispatch.next_ev_storage_mwh || 0,
    price: market.clearing_price || leader,
    errors: dispatch.correction_count || 0,
    shock: res.observation.shock_active || false
  });
  
  explainAgent(res.observation, policy, action.action);
  showWhatHappened(info, market);
  updateRewardBreakdown(res.reward);
  
  log(`Step ${res.observation.step}: R=${res.reward.score.toFixed(3)}`, res.reward.score > 0.5 ? 'reward-val' : '');
}

function play() { pause(); timer = setInterval(step, parseInt(document.getElementById('speed').value)); }
function pause() { if (timer) clearInterval(timer); timer = null; }
async function shock() { if (!sessionId) return; await api('/inject-shock', {renewable_drop_mwh:25}); log('⚡ SHOCK!', 'shock'); }

document.getElementById('resetBtn').onclick = () => { pause(); reset(); };
document.getElementById('stepBtn').onclick = () => { pause(); step(); };
document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('shockBtn').onclick = shock;

document.getElementById('connStatus').textContent = '✓ Connected';
document.getElementById('connStatus').className = 'status ok';

render({demand:100, supply:80, renewable:50, peaker:30, storage:25});
drawChart();
</script>
</body>
</html>
"""