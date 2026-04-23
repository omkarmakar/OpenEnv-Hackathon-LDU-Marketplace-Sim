def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>SmartGrid MarketSim 3D Demo</title>
  <style>
    :root {
      --bg-a: #0c141d;
      --bg-b: #12202b;
      --panel: rgba(10, 18, 26, 0.88);
      --line: rgba(147, 179, 189, 0.22);
      --text: #e8f0ee;
      --accent: #f2b46d;
      --accent2: #7bd0bd;
      --warn: #f16b6b;
    }
    html, body { margin: 0; padding: 0; background: radial-gradient(circle at 20% 0%, #213449 0%, #0b131d 38%, #070d14 100%); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; }
    .wrap { display: grid; grid-template-columns: 340px 1fr; min-height: 100vh; }
    .side { border-right: 1px solid var(--line); background: var(--panel); backdrop-filter: blur(6px); padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .card { border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: rgba(255,255,255,0.02); }
    .card h3 { margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; letter-spacing: .12em; color: #c0d2cf; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    button, select, input { border-radius: 8px; border: 1px solid var(--line); background: rgba(255,255,255,0.03); color: var(--text); padding: 8px; }
    button { cursor: pointer; }
    button.primary { background: linear-gradient(135deg, #c38038, #f2b46d); color: #1d1408; font-weight: 700; border: none; }
    button.secondary { background: linear-gradient(135deg, #2b7d6f, #7bd0bd); color: #031612; border: none; font-weight: 700; }
    .main { display: grid; grid-template-rows: 1fr 220px; }
    #scene { width: 100%; height: 100%; }
    .timeline { border-top: 1px solid var(--line); background: rgba(8, 13, 20, 0.9); padding: 10px 14px; display: grid; grid-template-rows: 1fr 56px; gap: 8px; }
    .metrics { display: grid; grid-template-columns: repeat(6, minmax(100px, 1fr)); gap: 8px; }
    .metric { background: rgba(255,255,255,0.03); border: 1px solid var(--line); border-radius: 10px; padding: 8px; }
    .metric .k { color: #b6cac6; font-size: 11px; text-transform: uppercase; letter-spacing: .1em; }
    .metric .v { margin-top: 4px; font-size: 16px; font-weight: 700; }
    #spark { width: 100%; height: 100%; background: rgba(255,255,255,0.02); border: 1px solid var(--line); border-radius: 8px; }
    .log { font-size: 12px; line-height: 1.4; max-height: 180px; overflow: auto; white-space: pre-wrap; }
    @media (max-width: 900px) {
      .wrap { grid-template-columns: 1fr; }
      .side { border-right: none; border-bottom: 1px solid var(--line); }
      .main { grid-template-rows: 52vh 260px; }
    }
  </style>
</head>
<body>
<div class='wrap'>
  <aside class='side'>
    <div class='card'>
      <h3>Session</h3>
      <div class='grid'>
        <label>Task
          <select id='task'>
            <option value='default'>default</option>
            <option value='long_horizon'>long_horizon</option>
            <option value='stress_shock'>stress_shock</option>
          </select>
        </label>
        <label>Policy
          <select id='policy'>
            <option value='adaptive'>adaptive</option>
            <option value='heuristic'>heuristic</option>
            <option value='random'>random</option>
          </select>
        </label>
        <label>Personality
          <select id='personality'>
            <option value='balanced'>balanced</option>
            <option value='risk_averse'>risk_averse</option>
            <option value='opportunistic'>opportunistic</option>
            <option value='greedy'>greedy</option>
          </select>
        </label>
        <label>Speed
          <input id='speed' type='range' min='100' max='1800' step='100' value='600'>
        </label>
      </div>
      <div class='grid' style='margin-top:10px'>
        <button id='reset' class='primary'>Reset</button>
        <button id='step' class='secondary'>Step</button>
        <button id='play'>Play</button>
        <button id='pause'>Pause</button>
        <button id='shock'>Inject Shock</button>
      </div>
    </div>
    <div class='card'>
      <h3>Event Log</h3>
      <div id='log' class='log'>No events yet.</div>
    </div>
  </aside>
  <main class='main'>
    <div id='scene'></div>
    <section class='timeline'>
      <div class='metrics'>
        <div class='metric'><div class='k'>Step</div><div class='v' id='m-step'>-</div></div>
        <div class='metric'><div class='k'>Demand</div><div class='v' id='m-demand'>-</div></div>
        <div class='metric'><div class='k'>Supply</div><div class='v' id='m-supply'>-</div></div>
        <div class='metric'><div class='k'>Price</div><div class='v' id='m-price'>-</div></div>
        <div class='metric'><div class='k'>Reward</div><div class='v' id='m-reward'>-</div></div>
        <div class='metric'><div class='k'>Corrections</div><div class='v' id='m-corr'>-</div></div>
      </div>
      <canvas id='spark'></canvas>
    </section>
  </main>
</div>

<script src='https://unpkg.com/three@0.162.0/build/three.min.js'></script>
<script>
const API = '';
let sessionId = null;
let timer = null;
let eventsCursor = 0;
const rewardSeries = [];
const demandSeries = [];
const supplySeries = [];

const canvas = document.getElementById('spark');
const logEl = document.getElementById('log');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b111a);
const camera = new THREE.PerspectiveCamera(65, 2, 0.1, 1000);
camera.position.set(0, 22, 36);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio || 1);
document.getElementById('scene').appendChild(renderer.domElement);

const ambient = new THREE.AmbientLight(0xffffff, 0.7); scene.add(ambient);
const key = new THREE.DirectionalLight(0xfff4d6, 1.0); key.position.set(18, 25, 15); scene.add(key);

const grid = new THREE.GridHelper(70, 28, 0x335166, 0x1f3342); scene.add(grid);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(70,70), new THREE.MeshStandardMaterial({ color: 0x12212e, roughness: 0.95 }));
floor.rotation.x = -Math.PI/2; floor.position.y = -0.01; scene.add(floor);

function mkAgent(color, x, z, r = 1.2) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 24), new THREE.MeshStandardMaterial({ color, metalness: .25, roughness: .45 }));
  body.position.y = r + .3; g.add(body);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(r+0.4, 0.12, 12, 32), new THREE.MeshBasicMaterial({ color: 0x9fd8ce }));
  ring.rotation.x = Math.PI/2; ring.position.y = 0.2; g.add(ring);
  g.position.set(x, 0, z);
  scene.add(g);
  return { group: g, body, ring };
}

const agents = {
  renewable: mkAgent(0x6ed7a8, -14, -6, 1.4),
  peaker: mkAgent(0xf09b58, 2, -10, 1.5),
  industrial: mkAgent(0x81a2ff, 14, -6, 1.35),
  ev: mkAgent(0xd56eea, -2, 10, 1.25),
};

const shockMesh = new THREE.Mesh(
  new THREE.TorusKnotGeometry(1.8, 0.35, 70, 10),
  new THREE.MeshStandardMaterial({ color: 0xff6060, emissive: 0x6b1010, metalness: .45, roughness: .2 })
);
shockMesh.visible = false;
shockMesh.position.set(0, 11, 0);
scene.add(shockMesh);

function resize() {
  const host = document.getElementById('scene');
  const w = host.clientWidth;
  const h = host.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

function animate() {
  requestAnimationFrame(animate);
  const t = performance.now() * 0.001;
  shockMesh.rotation.x = t * 1.7;
  shockMesh.rotation.y = t * 1.1;
  agents.renewable.ring.rotation.z = t * 0.9;
  agents.peaker.ring.rotation.z = t * -1.1;
  agents.industrial.ring.rotation.z = t * 0.8;
  agents.ev.ring.rotation.z = t * -0.95;
  renderer.render(scene, camera);
}
animate();

function drawSpark() {
  const ctx = canvas.getContext('2d');
  const ratio = window.devicePixelRatio || 1;
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  canvas.width = w * ratio;
  canvas.height = h * ratio;
  ctx.scale(ratio, ratio);

  ctx.fillStyle = '#09121b';
  ctx.fillRect(0, 0, w, h);

  function drawLine(series, color, maxY) {
    if (series.length < 2) return;
    const dx = w / Math.max(1, series.length - 1);
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    series.forEach((v, i) => {
      const x = i * dx;
      const y = h - (Math.max(0, Math.min(maxY, v)) / maxY) * (h - 10) - 5;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  const maxDemand = Math.max(1, ...demandSeries, ...supplySeries);
  drawLine(demandSeries.slice(-80), '#6ca6ff', maxDemand);
  drawLine(supplySeries.slice(-80), '#73d8bc', maxDemand);
  drawLine(rewardSeries.slice(-80).map(x => x * maxDemand), '#efb26d', maxDemand);
}

function log(msg) {
  const now = new Date().toLocaleTimeString();
  logEl.textContent = `[${now}] ${msg}\n` + logEl.textContent;
}

async function api(path, method='GET', body=null, query='') {
  const res = await fetch(`${API}${path}${query}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function chooseAction(obs) {
  const policy = document.getElementById('policy').value;
  const personality = document.getElementById('personality').value;
  const demand = obs.demand_mwh;
  const ren = obs.renewable_availability_mwh;
  const peaker = obs.peaker_capacity_mwh;
  const leader = obs.leader_price_signal || 45;

  const renQty = Math.max(0, Math.min(ren, demand * (policy === 'adaptive' ? 0.62 : 0.55)));
  const peakQty = Math.max(0, Math.min(peaker, demand - renQty));

  let peakerPrice = 58;
  let loadPrice = 88;
  if (policy === 'adaptive') {
    peakerPrice = personality === 'opportunistic' ? leader * 1.16 : personality === 'risk_averse' ? leader * 1.02 : leader * 1.1;
    loadPrice = personality === 'risk_averse' ? leader * 1.33 : leader * 1.5;
  }

  return {
    action: {
      bids: [
        { agent_id: 'renewable_1', role: 'renewable_prosumer', bid_type: 'supply', quantity_mwh: renQty, price_usd_per_mwh: Math.max(15, leader*0.82) },
        { agent_id: 'peaker_1', role: 'peaker_plant', bid_type: 'supply', quantity_mwh: peakQty, price_usd_per_mwh: peakerPrice },
        { agent_id: 'industrial_1', role: 'industrial_load', bid_type: 'demand', quantity_mwh: demand, price_usd_per_mwh: loadPrice }
      ],
      ev_charge_mwh: ren > demand ? 2 : 0,
      ev_discharge_mwh: ren < demand * 0.8 ? 3 : 0,
    }
  };
}

function updateScene(stepPayload) {
  const info = stepPayload.info || {};
  const dispatch = info.dispatch || {};
  const market = info.market || {};

  const demand = stepPayload.observation.demand_mwh;
  const supply = dispatch.delivered_supply_mwh || 0;
  const reward = stepPayload.reward.score || 0;

  demandSeries.push(demand);
  supplySeries.push(supply);
  rewardSeries.push(reward);
  drawSpark();

  document.getElementById('m-step').textContent = String(stepPayload.observation.step);
  document.getElementById('m-demand').textContent = demand.toFixed(1);
  document.getElementById('m-supply').textContent = supply.toFixed(1);
  document.getElementById('m-price').textContent = (market.clearing_price || stepPayload.observation.leader_price_signal || 0).toFixed(1);
  document.getElementById('m-reward').textContent = reward.toFixed(3);
  document.getElementById('m-corr').textContent = String(dispatch.correction_count || 0);

  const scarcity = stepPayload.observation.scarcity_index || 0;
  agents.renewable.group.position.z = -6 + (dispatch.renewable_dispatch_mwh || 0) * 0.04;
  agents.peaker.group.position.z = -10 + (dispatch.peaker_dispatch_mwh || 0) * 0.04;
  agents.industrial.group.position.z = -6 - scarcity * 8;
  agents.ev.group.position.z = 10 + ((dispatch.next_ev_storage_mwh || 0) / Math.max(1, stepPayload.observation.ev_storage_capacity_mwh)) * 6;

  shockMesh.visible = !!stepPayload.observation.shock_active;
  if (shockMesh.visible) shockMesh.position.y = 9 + scarcity * 8;

  log(`step=${stepPayload.observation.step} reward=${reward.toFixed(3)} price=${(market.clearing_price || 0).toFixed(1)} corrections=${dispatch.correction_count || 0}`);
}

async function resetSession() {
  const task = document.getElementById('task').value;
  const payload = { task_id: task, seed: 42 };
  const data = await api('/reset', 'POST', payload);
  sessionId = data.session_id;
  eventsCursor = 0;
  rewardSeries.length = 0;
  demandSeries.length = 0;
  supplySeries.length = 0;
  drawSpark();
  log(`session reset: ${sessionId.slice(0,8)} task=${task}`);
}

async function singleStep() {
  if (!sessionId) await resetSession();
  const st = await api('/state', 'GET', null, `?session_id=${sessionId}`);
  if (st.episode_done) {
    log('episode done - press reset to start new run');
    pauseLoop();
    return;
  }
  const action = chooseAction(st.observation);
  const stepRes = await api('/step', 'POST', action, `?session_id=${sessionId}`);
  updateScene(stepRes);
}

function playLoop() {
  pauseLoop();
  const speed = Number(document.getElementById('speed').value);
  timer = setInterval(() => { singleStep().catch(err => log(`error: ${err.message}`)); }, speed);
}

function pauseLoop() {
  if (timer) clearInterval(timer);
  timer = null;
}

async function injectShock() {
  if (!sessionId) return;
  const res = await api('/inject-shock', 'POST', { renewable_drop_mwh: 24 }, `?session_id=${sessionId}`);
  log(`manual shock applied: drop=${res.shock_event.drop_mwh}`);
}

document.getElementById('reset').onclick = () => resetSession().catch(e => log(`reset error: ${e.message}`));
document.getElementById('step').onclick = () => singleStep().catch(e => log(`step error: ${e.message}`));
document.getElementById('play').onclick = playLoop;
document.getElementById('pause').onclick = pauseLoop;
document.getElementById('shock').onclick = () => injectShock().catch(e => log(`shock error: ${e.message}`));
document.getElementById('speed').oninput = () => { if (timer) playLoop(); };

resetSession().catch(err => log(`init error: ${err.message}`));
</script>
</body>
</html>
"""
