def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>SmartGrid MarketSim</title>
  <style>
    :root {
      --bg: #0f1419;
      --panel: #1a2332;
      --border: #2d3a4f;
      --text: #e4e8ed;
      --muted: #8899aa;
      --green: #4ade80;
      --red: #f87171;
      --yellow: #fbbf24;
      --blue: #60a5fa;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    .header { background: var(--panel); padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
    .header h1 { margin: 0; font-size: 20px; font-weight: 600; color: var(--green); }
    .header .status { font-size: 13px; color: var(--muted); }
    
    .controls { background: var(--panel); padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
    .control-group { display: flex; align-items: center; gap: 8px; }
    .control-group label { font-size: 13px; color: var(--muted); }
    select, input { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 14px; }
    button { background: var(--border); border: none; color: var(--text); padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; transition: all 0.2s; }
    button:hover { background: #3d4a5f; }
    button.primary { background: var(--green); color: #0f1419; font-weight: 600; }
    button.primary:hover { background: #3bce70; }
    button.danger { background: var(--red); color: white; font-weight: 600; }
    button.danger:hover { background: #ef5555; }
    
    .main { display: grid; grid-template-columns: 1fr 380px; height: calc(100vh - 130px); }
    .viz { background: var(--panel); margin: 16px; border-radius: 12px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
    .viz canvas { width: 100%; height: 100%; }
    .viz-overlay { position: absolute; top: 16px; left: 16px; font-size: 12px; color: var(--muted); }
    
    .sidebar { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
    .card { background: var(--panel); border-radius: 12px; border: 1px solid var(--border); padding: 16px; }
    .card h3 { margin: 0 0 12px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
    
    .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .metric { text-align: center; padding: 12px; background: var(--bg); border-radius: 8px; }
    .metric .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
    .metric .value { font-size: 22px; font-weight: 700; }
    .metric .value.green { color: var(--green); }
    .metric .value.red { color: var(--red); }
    .metric .value.yellow { color: var(--yellow); }
    .metric .value.blue { color: var(--blue); }
    
    .chart { height: 120px; background: var(--bg); border-radius: 8px; position: relative; }
    .chart canvas { width: 100%; height: 100%; }
    
    .log { height: 160px; overflow-y: auto; font-size: 12px; font-family: 'Monaco', 'Consolas', monospace; line-height: 1.6; }
    .log div { padding: 4px 0; border-bottom: 1px solid var(--border); color: var(--muted); }
    .log div:last-child { border: none; }
    .log .step { color: var(--blue); }
    .log .reward { color: var(--green); }
    .log .error { color: var(--red); }
    .log .shock { color: var(--yellow); }
    
    .legend { display: flex; gap: 16px; font-size: 12px; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; }
    
    @media (max-width: 900px) {
      .main { grid-template-columns: 1fr; }
      .controls { flex-direction: column; align-items: stretch; }
    }
  </style>
</head>
<body>
  <header class='header'>
    <h1>⚡ SmartGrid MarketSim</h1>
    <div class='status' id='connectionStatus'>Connecting...</div>
  </header>
  
  <div class='controls'>
    <div class='control-group'>
      <label>Task</label>
      <select id='task'>
        <option value='default'>Default (24 steps)</option>
        <option value='long_horizon'>Long Horizon (48 steps)</option>
        <option value='stress_shock'>Stress Shock (30 steps)</option>
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
    <button id='stepBtn'>▶ Step</button>
    <button id='playBtn'>▶ Play</button>
    <button id='pauseBtn'>⏸ Pause</button>
    <button id='shockBtn' class='danger'>⚡ Shock</button>
  </div>
  
  <div class='main'>
    <div class='viz'>
      <canvas id='scene'></canvas>
      <div class='viz-overlay'>
        <div class='legend'>
          <div class='legend-item'><div class='legend-dot' style='background:#4ade80'></div>Renewable</div>
          <div class='legend-item'><div class='legend-dot' style='background:#f97316'></div>Peaker</div>
          <div class='legend-item'><div class='legend-dot' style='background:#60a5fa'></div>Demand</div>
          <div class='legend-item'><div class='legend-dot' style='background:#a78bfa'></div>Storage</div>
        </div>
      </div>
    </div>
    
    <div class='sidebar'>
      <div class='card'>
        <h3>Current Metrics</h3>
        <div class='metrics'>
          <div class='metric'>
            <div class='label'>Step</div>
            <div class='value blue' id='mStep'>-</div>
          </div>
          <div class='metric'>
            <div class='label'>Reward</div>
            <div class='value green' id='mReward'>-</div>
          </div>
          <div class='metric'>
            <div class='label'>Demand</div>
            <div class='value' id='mDemand'>-</div>
          </div>
          <div class='metric'>
            <div class='label'>Supply</div>
            <div class='value' id='mSupply'>-</div>
          </div>
          <div class='metric'>
            <div class='label'>Price</div>
            <div class='value yellow' id='mPrice'>-</div>
          </div>
          <div class='metric'>
            <div class='label'>Errors</div>
            <div class='value red' id='mErrors'>-</div>
          </div>
        </div>
      </div>
      
      <div class='card'>
        <h3>Reward Over Time</h3>
        <div class='chart'>
          <canvas id='rewardChart'></canvas>
        </div>
      </div>
      
      <div class='card'>
        <h3>Event Log</h3>
        <div class='log' id='log'></div>
      </div>
    </div>
  </div>

<script>
const API = '';
let sessionId = null;
let timer = null;
const rewardHistory = [];
const demandHistory = [];
const supplyHistory = [];

const canvas = document.getElementById('scene');
const ctx = canvas.getContext('2d');
const chartCanvas = document.getElementById('rewardChart');
const chartCtx = chartCanvas.getContext('2d');

function resize() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = rect.height + 'px';
  ctx.scale(dpr, dpr);
  
  const crc = chartCanvas.getBoundingClientRect();
  chartCanvas.width = crc.width * dpr;
  chartCanvas.height = crc.height * dpr;
  chartCanvas.style.width = crc.width + 'px';
  chartCanvas.style.height = crc.height + 'px';
  chartCtx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();

function drawGrid() {
  const w = canvas.width / (window.devicePixelRatio || 1);
  const h = canvas.height / (window.devicePixelRatio || 1);
  ctx.fillStyle = '#1a2332';
  ctx.fillRect(0, 0, w, h);
  
  ctx.strokeStyle = '#2d3a4f';
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 40) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 0; y < h; y += 40) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }
}

function drawBar(x, y, w, h, color, label, value) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = '#e4e8ed';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'center';
  if (label) ctx.fillText(label, x + w/2, y + h + 16);
  if (value) ctx.fillText(value, x + w/2, y - 8);
}

function render(data) {
  drawGrid();
  const w = canvas.width / (window.devicePixelRatio || 1);
  const h = canvas.height / (window.devicePixelRatio || 1);
  const barW = 80;
  const maxH = h * 0.6;
  const baseY = h - 60;
  
  const demand = data.demand || 120;
  const supply = data.supply || 100;
  const renewable = data.renewable || 50;
  const peaker = data.peaker || 35;
  const storage = data.storage || 25;
  const maxVal = Math.max(demand, supply, renewable + peaker) * 1.2;
  
  const scale = maxH / maxVal;
  
  const rx = w * 0.2;
  drawBar(rx, baseY - renewable * scale, barW, renewable * scale, '#4ade80', 'Renewable', renewable.toFixed(0));
  drawBar(rx + barW + 10, baseY - peaker * scale, barW, peaker * scale, '#f97316', 'Peaker', peaker.toFixed(0));
  
  const dx = w * 0.55;
  drawBar(dx, baseY - demand * scale, barW, demand * scale, '#60a5fa', 'Demand', demand.toFixed(0));
  
  const sx = w * 0.8;
  const storagePct = (storage / 60) * 100;
  ctx.fillStyle = '#a78bfa';
  ctx.fillRect(sx, baseY - maxH, barW, maxH);
  ctx.fillStyle = '#1a2332';
  ctx.fillRect(sx, baseY - maxH, barW, maxH * (1 - storage/60));
  ctx.fillStyle = '#e4e8ed';
  ctx.textAlign = 'center';
  ctx.fillText('Storage', sx + barW/2, baseY + 16);
  ctx.fillText(storagePct.toFixed(0) + '%', sx + barW/2, baseY - maxH - 8);
  
  if (data.shock) {
    ctx.fillStyle = '#f87171';
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('⚡ SHOCK', w/2, 50);
  }
}

function drawChart() {
  const w = chartCanvas.width / (window.devicePixelRatio || 1);
  const h = chartCanvas.height / (window.devicePixelRatio || 1);
  chartCtx.fillStyle = '#0f1419';
  chartCtx.fillRect(0, 0, w, h);
  
  if (rewardHistory.length < 2) return;
  const maxR = Math.max(...rewardHistory, 1);
  const step = w / Math.max(1, rewardHistory.length - 1);
  
  chartCtx.strokeStyle = '#4ade80';
  chartCtx.lineWidth = 2;
  chartCtx.beginPath();
  rewardHistory.forEach((r, i) => {
    const x = i * step;
    const y = h - (r / maxR) * (h - 20) - 10;
    if (i === 0) chartCtx.moveTo(x, y);
    else chartCtx.lineTo(x, y);
  });
  chartCtx.stroke();
  
  chartCtx.fillStyle = '#4ade80';
  chartCtx.font = '11px sans-serif';
  chartCtx.textAlign = 'right';
  chartCtx.fillText(maxR.toFixed(2), w - 4, 12);
}

function log(msg, type = '') {
  const el = document.getElementById('log');
  const div = document.createElement('div');
  div.className = type;
  div.innerHTML = msg;
  el.insertBefore(div, el.firstChild);
}

async function api(path, body = null) {
  const opts = { method: body ? 'POST' : 'GET' };
  if (body) opts.headers = { 'Content-Type': 'application/json' };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function updateUI(data) {
  document.getElementById('mStep').textContent = data.step || 0;
  document.getElementById('mReward').textContent = (data.reward || 0).toFixed(3);
  document.getElementById('mDemand').textContent = (data.demand || 0).toFixed(0);
  document.getElementById('mSupply').textContent = (data.supply || 0).toFixed(0);
  document.getElementById('mPrice').textContent = '$' + (data.price || 0).toFixed(0);
  document.getElementById('mErrors').textContent = data.errors || 0;
  
  rewardHistory.push(data.reward || 0);
  demandHistory.push(data.demand || 0);
  supplyHistory.push(data.supply || 0);
  drawChart();
  
  render({
    demand: data.demand,
    supply: data.supply,
    renewable: data.renewable,
    peaker: data.peaker,
    storage: data.storage,
    shock: data.shock
  });
}

async function reset() {
  const task = document.getElementById('task').value;
  rewardHistory.length = 0;
  demandHistory.length = 0;
  supplyHistory.length = 0;
  drawChart();
  
  const data = await api('/reset', { task_id: task, seed: 42 });
  sessionId = data.session_id;
  log(`<span class='step'>Reset:</span> ${task} (seed=42)`, 'step');
  log(`Session: ${sessionId.slice(0,8)}...`, '');
  
  const obs = data.observation;
  updateUI({
    step: 0,
    reward: 0,
    demand: obs.demand_mwh,
    supply: 0,
    renewable: obs.renewable_availability_mwh,
    peaker: obs.peaker_capacity_mwh,
    storage: obs.ev_storage_mwh,
    price: obs.leader_price_signal,
    errors: 0,
    shock: false
  });
}

async function step() {
  if (!sessionId) { await reset(); return; }
  
  const st = await api(`/state?session_id=${sessionId}`);
  if (st.episode_done) {
    log('<span class="reward">Episode complete!</span>', '');
    pause();
    return;
  }
  
  const obs = st.observation;
  const demand = obs.demand_mwh;
  const ren = obs.renewable_availability_mwh;
  const peaker = obs.peaker_capacity_mwh;
  const policy = document.getElementById('policy').value;
  const leader = obs.leader_price_signal;
  
  const renQty = Math.min(ren, demand * 0.55);
  const peakQty = Math.min(peaker, demand - renQty);
  const peakerPrice = policy === 'adaptive' ? leader * 1.1 : 55;
  
  const action = {
    action: {
      bids: [
        { agent_id: 'renewable', role: 'renewable_prosumer', bid_type: 'supply', quantity_mwh: renQty, price_usd_per_mwh: 20 },
        { agent_id: 'peaker', role: 'peaker_plant', bid_type: 'supply', quantity_mwh: peakQty, price_usd_per_mwh: peakerPrice },
        { agent_id: 'load', role: 'industrial_load', bid_type: 'demand', quantity_mwh: demand, price_usd_per_mwh: 85 }
      ],
      ev_charge_mwh: ren > demand ? 5 : 0,
      ev_discharge_mwh: ren < demand * 0.8 ? 3 : 0
    }
  };
  
  const res = await api(`/step?session_id=${sessionId}`, action);
  const info = res.info || {};
  const market = info.market || {};
  const dispatch = info.dispatch || {};
  
  updateUI({
    step: res.observation.step,
    reward: res.reward.score,
    demand: demand,
    supply: dispatch.delivered_supply_mwh || 0,
    renewable: dispatch.renewable_dispatch_mwh || 0,
    peaker: dispatch.peaker_dispatch_mwh || 0,
    storage: dispatch.next_ev_storage_mwh || 0,
    price: market.clearing_price || leader,
    errors: dispatch.correction_count || 0,
    shock: res.observation.shock_active || false
  });
  
  const rew = res.reward.score;
  const rewClass = rew > 0.6 ? 'reward' : rew > 0.3 ? '' : 'error';
  log(`<span class='step'>Step ${res.observation.step}:</span> reward=<span class='${rewClass}'>${rew.toFixed(3)}</span> price=$${market.clearing_price || 0}`, '');
}

function play() {
  pause();
  const speed = parseInt(document.getElementById('speed').value);
  timer = setInterval(step, speed);
}

function pause() {
  if (timer) clearInterval(timer);
  timer = null;
}

async function shock() {
  if (!sessionId) return;
  await api('/inject-shock', { renewable_drop_mwh: 25 });
  log('<span class="shock">⚡ SHOCK INJECTED (-25 MWh)!</span>', 'shock');
}

document.getElementById('resetBtn').onclick = reset;
document.getElementById('stepBtn').onclick = step;
document.getElementById('playBtn').onclick = play;
document.getElementById('pauseBtn').onclick = pause;
document.getElementById('shockBtn').onclick = shock;

document.getElementById('connectionStatus').textContent = '✓ Connected';

render({});
drawChart();
reset();
</script>
</body>
</html>
"""