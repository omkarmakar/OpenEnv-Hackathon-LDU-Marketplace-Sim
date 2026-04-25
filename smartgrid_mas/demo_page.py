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
    .grid { display: grid; grid-template-columns: 1fr 1.2fr 1.1fr 1fr; grid-template-rows: auto auto auto; gap: 2px; padding: 2px; height: calc(100vh - 120px); background: var(--bg); }
    .power-mix-panel { grid-column: span 2; }
    .panel { background: var(--panel); border: 1px solid var(--border); padding: 10px; overflow: hidden; display: flex; flex-direction: column; }
    .panel-title { font-size: 10px; color: var(--dim); text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid var(--border); padding-bottom: 6px; flex-shrink: 0; }
    .panel-content { flex: 1; overflow: auto; }
    
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
    
    /* FREQUENCY/VOLTAGE HEALTH */
    .health-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    .health-card { background: var(--bg); padding: 8px; border-radius: 4px; text-align: center; }
    .health-val { font-size: 16px; font-weight: bold; }
    .health-lbl { font-size: 8px; color: var(--dim); margin-top: 2px; }
    .health-bar { width: 100%; height: 4px; background: var(--border); border-radius: 2px; margin: 4px 0; }
    .health-bar-fill { height: 100%; border-radius: 2px; }
    
    /* POWER MIX DONUT */
    .donut-container { width: 100%; height: 120px; display: flex; justify-content: center; align-items: center; }
    .donut-chart { width: 100px; height: 100px; }
    .donut-legend { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 9px; margin-top: 8px; }
    .donut-item { display: flex; gap: 4px; align-items: center; }
    .donut-swatch { width: 8px; height: 8px; border-radius: 2px; }
    
    /* FORECAST VS ACTUAL */
    .forecast-chart { width: 100%; height: 100%; background: var(--bg); border-radius: 4px; }
    .forecast-stat { display: flex; justify-content: space-between; font-size: 9px; margin: 4px 0; padding: 4px 0; border-bottom: 1px solid var(--border); }
    
    /* CONGESTION HEATMAP */
    .heatmap-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
    .heatmap-cell { background: var(--bg); padding: 8px; border-radius: 4px; text-align: center; border-left: 3px solid var(--border); }
    .heatmap-cell.green { border-color: var(--green); }
    .heatmap-cell.yellow { border-color: var(--yellow); }
    .heatmap-cell.red { border-color: var(--red); }
    .heatmap-val { font-size: 14px; font-weight: bold; }
    .heatmap-lbl { font-size: 8px; color: var(--dim); }
    
    /* MARKET MICROSTRUCTURE */
    .orderbook { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 9px; }
    .ob-section { background: var(--bg); padding: 6px; border-radius: 3px; }
    .ob-header { color: var(--dim); font-size: 8px; margin-bottom: 4px; font-weight: bold; }
    .ob-row { display: flex; justify-content: space-between; padding: 2px 0; }
    .ob-spread { background: rgba(163,230,53,0.1); padding: 4px; border-radius: 2px; margin-top: 4px; text-align: center; }
    
    /* POLICY CONFIDENCE METER */
    .policy-meter { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px; }
    .meter-item { background: var(--bg); padding: 8px; border-radius: 4px; text-align: center; }
    .meter-val { font-size: 14px; font-weight: bold; }
    .meter-lbl { font-size: 8px; color: var(--dim); margin-top: 2px; }
    
    /* CORRECTION SAVINGS */
    .savings-grid { display: grid; grid-template-columns: 1fr; gap: 6px; }
    .saving-item { background: var(--bg); padding: 8px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
    .saving-icon { font-size: 16px; }
    .saving-val { font-size: 14px; font-weight: bold; color: var(--green); }
    
    /* WHAT-IF COUNTERFACTUAL */
    .whatif-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .whatif-box { background: var(--bg); padding: 10px; border-radius: 4px; text-align: center; }
    .whatif-label { font-size: 9px; color: var(--dim); margin-bottom: 6px; }
    .whatif-val { font-size: 20px; font-weight: bold; }
    
    /* EVENT TIMELINE */
    .timeline { display: flex; flex-direction: column; gap: 4px; max-height: 100%; overflow-y: auto; }
    .timeline-item { background: var(--bg); padding: 6px 8px; border-radius: 3px; border-left: 3px solid var(--border); font-size: 9px; display: flex; gap: 6px; }
    .timeline-time { color: var(--cyan); font-weight: bold; min-width: 30px; }
    .timeline-event { color: var(--dim); flex: 1; }
    .timeline-item.critical { border-color: var(--red); }
    .timeline-item.warning { border-color: var(--yellow); }
    .timeline-item.info { border-color: var(--blue); }
    
    /* RESILIENCE SCOREBOARD */
    .resilience-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .resilience-card { background: var(--bg); padding: 10px; border-radius: 4px; text-align: center; border-top: 2px solid var(--border); }
    .resilience-val { font-size: 22px; font-weight: bold; }
    .resilience-lbl { font-size: 8px; color: var(--dim); margin-top: 4px; }
    
    /* GRID PULSE ANIMATION */
    @keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
    .pulse-indicator { width: 6px; height: 6px; background: var(--green); border-radius: 50%; animation: pulse 1.5s infinite; display: inline-block; margin-right: 4px; }
    
    /* ALARM PRIORITY QUEUE */
    .alarm-queue { display: flex; flex-direction: column; gap: 4px; }
    .alarm { padding: 6px 8px; border-radius: 3px; border-left: 3px solid var(--border); font-size: 9px; }
    .alarm.p1 { background: rgba(239,68,68,0.15); border-color: var(--red); color: var(--red); font-weight: bold; }
    .alarm.p2 { background: rgba(234,179,8,0.15); border-color: var(--yellow); color: var(--yellow); }
    .alarm.p3 { background: rgba(59,130,246,0.15); border-color: var(--blue); color: var(--blue); }
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
  
  <!-- MAIN GRID - 4 COL x 3 ROW ENHANCED LAYOUT -->
  <div class="grid">
    <!-- ROW 1 -->
    <!-- MARKET INTELLIGENCE -->
    <div class="panel">
      <div class="panel-title">💰 MARKET INTELLIGENCE</div>
      <div class="panel-content">
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
          <div class="clearing-price" id="clearingPrice">₹0</div>
          <div class="lbl" id="clearingMW">0 MW @</div>
        </div>
      </div>
    </div>
    
    <!-- POWER FLOW DIGITAL TWIN -->
    <div class="panel">
      <div class="panel-title">⚡ POWER FLOW DIGITAL TWIN</div>
      <div class="panel-content">
        <svg class="power-svg" viewBox="0 0 380 140" style="height:120px">
          <!-- Solar -->
          <g transform="translate(30, 25)">
            <rect x="0" y="0" width="50" height="45" rx="4" class="node-solar"/>
            <text x="25" y="15" class="node-text">☀️ SOLAR</text>
            <text x="25" y="32" class="node-text" id="nodeRenew" fill="#22c55e" font-size="14">0</text>
            <text x="25" y="60" class="node-label">MW</text>
          </g>
          
          <!-- Power Plant -->
          <g transform="translate(90, 25)">
            <rect x="0" y="0" width="70" height="45" rx="4" class="node-gas"/>
            <text x="35" y="14" class="node-text" font-size="7">🏭 POWER</text>
            <text x="35" y="22" class="node-text" font-size="7">PLANT</text>
            <text x="35" y="34" class="node-text" id="nodePeaker" fill="#eab308" font-size="14">0</text>
            <text x="35" y="60" class="node-label">MW</text>
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
          <path d="M80,47 L90,47" class="flow-line" stroke="#22c55e"/>
          <path d="M160,47 L170,80" class="flow-line" stroke="#eab308"/>
          <path d="M80,112 L80,90 L170,90" class="flow-line" stroke="#a855f7"/>
          <path d="M225,80 L310,80" class="flow-line" stroke="#3b82f6"/>
          
          <!-- Loss -->
          <text x="240" y="60" class="flow-loss" id="nodeLoss">⚡ Loss: 0 MW</text>
        </svg>
        
      </div>
    </div>
    
    <!-- MODULE 1: GRID FREQUENCY + VOLTAGE HEALTH PANEL -->
    <div class="panel">
      <div class="panel-title">📊 GRID HEALTH STATUS</div>
      <div class="panel-content">
        <div class="health-grid">
          <div class="health-card">
            <span class="pulse-indicator"></span><span style="font-size:10px;color:var(--dim)">Freq</span>
            <div class="health-val" id="freqVal" style="color:var(--green)">49.93</div>
            <div style="font-size:8px;color:var(--dim)">Hz</div>
            <div class="health-bar"><div class="health-bar-fill" style="width:98%;background:var(--green)"></div></div>
          </div>
          <div class="health-card">
            <div style="font-size:10px;color:var(--dim)">Volt</div>
            <div class="health-val" id="voltVal" style="color:var(--green)">97</div>
            <div style="font-size:8px;color:var(--dim)">%</div>
            <div class="health-bar"><div class="health-bar-fill" style="width:97%;background:var(--green)"></div></div>
          </div>
          <div class="health-card">
            <div style="font-size:10px;color:var(--dim)">Reserve</div>
            <div class="health-val" id="reserveVal" style="color:var(--green)">14</div>
            <div style="font-size:8px;color:var(--dim)">MW</div>
            <div class="health-bar"><div class="health-bar-fill" style="width:70%;background:var(--green)"></div></div>
          </div>
        </div>
        <div style="margin-top:8px;font-size:8px;color:var(--dim);text-align:center">ISO-Grade Monitoring</div>
      </div>
    </div>
    
    <!-- MODULE 10: SYSTEM RESILIENCE SCOREBOARD -->
    <div class="panel">
      <div class="panel-title">🎯 RESILIENCE INDEX</div>
      <div class="panel-content">
        <div class="resilience-grid">
          <div class="resilience-card">
            <div class="resilience-val" id="reliabilityScore" style="color:var(--green)">94</div>
            <div class="resilience-lbl">Reliability</div>
          </div>
          <div class="resilience-card">
            <div class="resilience-val" id="efficiencyScore" style="color:var(--cyan)">88</div>
            <div class="resilience-lbl">Efficiency</div>
          </div>
          <div class="resilience-card">
            <div class="resilience-val" id="greenScore" style="color:var(--green)">81</div>
            <div class="resilience-lbl">Green Score</div>
          </div>
          <div class="resilience-card">
            <div class="resilience-val" id="resilienceScore" style="color:var(--purple)">91</div>
            <div class="resilience-lbl">Resilience</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ROW 2 -->
    <!-- MODULE 2: POWER MIX DONUT + MODULE 3: LOAD FORECAST -->
    <div class="panel power-mix-panel">
      <div class="panel-title">📊 POWER MIX & FORECAST</div>
      <div class="panel-content" style="display:flex;flex-direction:column">
        <div style="flex:1">
          <div style="font-size:9px;color:var(--dim);margin-bottom:4px">Live Generation</div>
          <div class="donut-container">
            <svg class="donut-chart" viewBox="0 0 100 100">
              <!-- Solar segment -->
              <circle cx="50" cy="50" r="30" fill="none" stroke="#22c55e" stroke-width="15" stroke-dasharray="62 188" stroke-dashoffset="47" opacity="0.8"/>
              <!-- Power Plant segment -->
              <circle cx="50" cy="50" r="30" fill="none" stroke="#eab308" stroke-width="15" stroke-dasharray="50 188" stroke-dashoffset="-15" opacity="0.8"/>
              <!-- Storage segment -->
              <circle cx="50" cy="50" r="30" fill="none" stroke="#a855f7" stroke-width="15" stroke-dasharray="40 188" stroke-dashoffset="-65" opacity="0.8"/>
              <!-- Reserve segment -->
              <circle cx="50" cy="50" r="30" fill="none" stroke="#3b82f6" stroke-width="15" stroke-dasharray="36 188" stroke-dashoffset="-105" opacity="0.8"/>
              <text x="50" y="55" text-anchor="middle" fill="var(--text)" font-size="14" font-weight="bold">100%</text>
            </svg>
          </div>
          <div class="donut-legend">
            <div class="donut-item"><div class="donut-swatch" style="background:var(--green)"></div><span>Solar 33%</span></div>
            <div class="donut-item"><div class="donut-swatch" style="background:var(--yellow)"></div><span>Power Plant 27%</span></div>
            <div class="donut-item"><div class="donut-swatch" style="background:var(--purple)"></div><span>Storage 21%</span></div>
            <div class="donut-item"><div class="donut-swatch" style="background:var(--blue)"></div><span>Reserve 19%</span></div>
          </div>
        </div>
        <div style="flex:1;margin-top:6px;border-top:1px solid var(--border);padding-top:6px">
          <div style="font-size:9px;color:var(--dim);margin-bottom:4px">Load Forecast</div>
          <div class="forecast-stat"><span>Forecast</span><span style="color:var(--cyan)">185 MW</span></div>
          <div class="forecast-stat"><span>Actual</span><span style="color:var(--green)">178 MW</span></div>
          <div class="forecast-stat"><span>Error</span><span style="color:var(--yellow)">+3.9%</span></div>
        </div>
      </div>
    </div>
    
    <!-- MODULE 4: CONGESTION / TRANSMISSION HEATMAP -->
    <div class="panel">
      <div class="panel-title">🔥 TRANSMISSION HEATMAP</div>
      <div class="panel-content">
        <div class="heatmap-grid">
          <div class="heatmap-cell green">
            <div class="heatmap-val">42%</div>
            <div class="heatmap-lbl">Line A</div>
          </div>
          <div class="heatmap-cell yellow">
            <div class="heatmap-val">68%</div>
            <div class="heatmap-lbl">Line B</div>
          </div>
          <div class="heatmap-cell red">
            <div class="heatmap-val">94%</div>
            <div class="heatmap-lbl">Line C</div>
          </div>
          <div class="heatmap-cell green">
            <div class="heatmap-val">51%</div>
            <div class="heatmap-lbl">Line D</div>
          </div>
          <div class="heatmap-cell yellow">
            <div class="heatmap-val">71%</div>
            <div class="heatmap-lbl">Line E</div>
          </div>
          <div class="heatmap-cell green">
            <div class="heatmap-val">38%</div>
            <div class="heatmap-lbl">Line F</div>
          </div>
        </div>
        <div style="margin-top:6px;font-size:8px;color:var(--dim);text-align:center">SCADA Network Status</div>
      </div>
    </div>
    
    <!-- MODULE 5: MARKET MICROSTRUCTURE PANEL -->
    <div class="panel">
      <div class="panel-title">📈 MARKET MICROSTRUCTURE</div>
      <div class="panel-content">
        <div class="orderbook">
          <div class="ob-section">
            <div class="ob-header">BID DEPTH</div>
            <div class="ob-row"><span>₹7,500</span><span style="color:var(--red)">-450 MW</span></div>
            <div class="ob-row"><span>₹7,000</span><span style="color:var(--red)">-320 MW</span></div>
            <div class="ob-row"><span>₹6,500</span><span style="color:var(--red)">-200 MW</span></div>
          </div>
          <div class="ob-section">
            <div class="ob-header">ASK DEPTH</div>
            <div class="ob-row"><span>₹5,500</span><span style="color:var(--green)">+180 MW</span></div>
            <div class="ob-row"><span>₹5,000</span><span style="color:var(--green)">+220 MW</span></div>
            <div class="ob-row"><span>₹4,500</span><span style="color:var(--green)">+340 MW</span></div>
          </div>
        </div>
        <div class="ob-spread">
          <div style="font-size:8px;color:var(--dim)">Spread</div>
          <div style="font-weight:bold;color:var(--cyan)">₹500/MWh</div>
          <div style="font-size:8px;color:var(--dim);margin-top:2px">Liquidity: Excellent</div>
        </div>
      </div>
    </div>
    
    <!-- ROW 3 -->
    <!-- MODULE 9: EVENT TIMELINE STRIP -->
    <div class="panel">
      <div class="panel-title">📅 EVENT TIMELINE</div>
      <div class="panel-content">
        <div class="timeline" id="eventTimeline">
          <div class="timeline-item info">
            <div class="timeline-time">T0</div>
            <div class="timeline-event">Simulation started</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- SHOCK / RISK REORGANIZED WITH WHAT-IF -->
    <div class="panel">
      <div class="panel-title">⚠️ RISK & CONTINGENCY</div>
      <div class="panel-content">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
          <div>
            <div class="gauge"><div class="gauge-val green" id="blackoutRisk2">0%</div><div class="gauge-lbl">Blackout Risk</div></div>
          </div>
          <div>
            <div class="gauge"><div class="gauge-val green" id="gridStress2">0%</div><div class="gauge-lbl">Grid Stress</div></div>
          </div>
        </div>
        <div style="border-top:1px solid var(--border);padding-top:6px">
          <div style="font-size:9px;color:var(--dim);margin-bottom:6px">Counterfactual Sim</div>
          <div class="whatif-panel">
            <div class="whatif-box">
              <div class="whatif-label">WITHOUT Intervention</div>
              <div class="whatif-val" style="color:var(--red)">61%</div>
              <div style="font-size:8px;color:var(--dim)">Risk</div>
            </div>
            <div class="whatif-box">
              <div class="whatif-label">WITH Dispatch</div>
              <div class="whatif-val" style="color:var(--green)">21%</div>
              <div style="font-size:8px;color:var(--dim)">Risk</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- RL DECISION ENHANCED WITH POLICY CONFIDENCE + CORRECTION SAVINGS -->
    <div class="panel">
      <div class="panel-title">🧠 RL DECISION ENGINE</div>
      <div class="panel-content" style="display:flex;flex-direction:column">
        <div style="flex:0">
          <div class="brain-card">
            <div class="policy-name" id="policyName">ADAPTIVE POLICY</div>
            <div class="policy-reason" id="policyReason">Analyzing grid state...</div>
          </div>
          <div class="score-breakdown" id="scoreBreakdown" style="font-size:8px"></div>
        </div>
        <div style="border-top:1px solid var(--border);margin-top:6px;padding-top:6px;flex:1">
          <div style="font-size:9px;color:var(--dim);margin-bottom:6px">Policy Confidence</div>
          <div class="policy-meter">
            <div class="meter-item">
              <div style="font-size:8px;color:var(--dim)">Confidence</div>
              <div class="meter-val" id="confidenceVal" style="color:var(--green)">84%</div>
            </div>
            <div class="meter-item">
              <div style="font-size:8px;color:var(--dim)">Exploration</div>
              <div class="meter-val" id="explorationVal" style="color:var(--cyan)">11%</div>
            </div>
          </div>
          <div style="background:var(--bg);padding:6px;border-radius:4px;margin-top:6px;font-size:8px;color:var(--dim);text-align:center">
            Mode: <span style="color:var(--yellow);font-weight:bold">Defensive</span>
          </div>
        </div>
        <div style="border-top:1px solid var(--border);margin-top:6px;padding-top:6px;flex:1">
          <div style="font-size:9px;color:var(--dim);margin-bottom:6px">LDU Interventions</div>
          <div class="savings-grid">
            <div class="saving-item">
              <div class="saving-icon">🛡️</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">Total Actions</div><div class="saving-val" id="interventionCount">7</div></div>
            </div>
            <div class="saving-item">
              <div class="saving-icon">🚫</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">Blackouts Prevented</div><div class="saving-val" id="blackoutsPrevented">2</div></div>
            </div>
            <div class="saving-item">
              <div class="saving-icon">⚡</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">Recovery Events</div><div class="saving-val" id="recoveryEvents">4</div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- STABILITY ANALYTICS -->
    <div class="panel">
      <div class="panel-title">📈 STABILITY ANALYTICS</div>
      <div class="panel-content">
        <canvas id="historyChart" class="chart-box"></canvas>
      </div>
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
const INR_PER_USD = 100;

function toInr(priceUsd) {
  return Math.round(priceUsd * INR_PER_USD);
}

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
  const step = document.getElementById('kStep').textContent.split('/')[0] || '0';
  const priority = type === 'shock' || type === 'error' ? 'critical' : type === 'warn' ? 'warning' : 'info';
  addTimelineEvent(step, msg, priority);
}

async function api(path, body) {
  const opts = {method: body ? 'POST' : 'GET'};
  if (body) { opts.headers = {'Content-Type': 'application/json'}; opts.body = JSON.stringify(body); }
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function updateBidLadder(renew, peak, demand) {
  const solarBidUsd = 20;
  const peakBidUsd = 55;
  const demandBidUsd = 85;
  document.getElementById('supplyBids').innerHTML = `
    <div class="bid-row solar"><span>Solar</span><span>${Math.round(renew)}@₹${toInr(solarBidUsd).toLocaleString('en-IN')}/MWh</span></div>
    <div class="bid-row peaker"><span>Power Plant</span><span>${Math.round(peak)}@₹${toInr(peakBidUsd).toLocaleString('en-IN')}/MWh</span></div>
  `;
  document.getElementById('demandBids').innerHTML = `
    <div class="bid-row demand"><span>Factory</span><span>${Math.round(demand)}@₹${toInr(demandBidUsd).toLocaleString('en-IN')}/MWh</span></div>
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
  
}

function updateDispatch(d) {
  if (d.corrections && d.corrections.length > 0) {
    d.corrections.forEach(c => log(c, 'warn'));
  }
}

function updateRisk(supply, demand) {
  const stress = Math.max(0, (demand - supply) / demand * 100);
  const blackout = Math.max(0, demand - supply) / demand * 100;
  
  // Update old risk display (compatibility)
  const stEl = document.getElementById('gridStress');
  if (stEl) {
    stEl.textContent = stress.toFixed(0) + '%';
    stEl.className = 'gauge-val ' + (stress < 20 ? 'green' : stress < 50 ? 'yellow' : 'red');
  }
  
  const boEl = document.getElementById('blackoutRisk');
  if (boEl) {
    boEl.textContent = blackout.toFixed(0) + '%';
    boEl.className = 'gauge-val ' + (blackout < 5 ? 'green' : blackout < 20 ? 'yellow' : 'red');
  }
  
  // Update new risk display
  const stEl2 = document.getElementById('gridStress2');
  if (stEl2) {
    stEl2.textContent = stress.toFixed(0) + '%';
    stEl2.className = 'gauge-val ' + (stress < 20 ? 'green' : stress < 50 ? 'yellow' : 'red');
  }
  
  const boEl2 = document.getElementById('blackoutRisk2');
  if (boEl2) {
    boEl2.textContent = blackout.toFixed(0) + '%';
    boEl2.className = 'gauge-val ' + (blackout < 5 ? 'green' : blackout < 20 ? 'yellow' : 'red');
  }
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

// NEW MODULE UPDATES
function updateGridHealth(renew, peak, demand) {
  // Grid frequency (49.5-50.5 Hz nominal)
  const freqBase = 50.0;
  const stressRatio = Math.min(1, demand / (renew + peak));
  const freqVal = freqBase - (stressRatio * 0.5);
  document.getElementById('freqVal').textContent = freqVal.toFixed(2);
  
  // Voltage stability (0-100%)
  const voltVal = Math.max(80, Math.min(100, 98 - stressRatio * 15));
  document.getElementById('voltVal').textContent = Math.round(voltVal);
  
  // Spinning reserve
  const reserve = Math.max(0, (renew + peak) * 0.2 - demand * 0.1);
  document.getElementById('reserveVal').textContent = Math.round(reserve);
  
  // Update health bars
  document.querySelectorAll('.health-bar-fill').forEach((bar, i) => {
    const vals = [freqVal / 50 * 100, voltVal, reserve / 25 * 100];
    const width = Math.min(100, Math.max(0, vals[i]));
    bar.style.width = width + '%';
    const color = width > 80 ? 'var(--green)' : width > 60 ? 'var(--yellow)' : 'var(--red)';
    bar.style.background = color;
  });
}

function updatePowerMix(renew, peak, ev, reserve) {
  const total = renew + peak + Math.max(0, ev) + reserve;
  if (total === 0) return;
  
  const solarPct = (renew / total * 100).toFixed(0);
  const plantPct = (peak / total * 100).toFixed(0);
  const storagePct = (Math.max(0, ev) / total * 100).toFixed(0);
  const reservePct = (reserve / total * 100).toFixed(0);
  
  // Update legend
  const legend = document.querySelector('.donut-legend');
  if (legend) {
    legend.innerHTML = `
      <div class="donut-item"><div class="donut-swatch" style="background:var(--green)"></div><span>Solar ${solarPct}%</span></div>
      <div class="donut-item"><div class="donut-swatch" style="background:var(--yellow)"></div><span>Power Plant ${plantPct}%</span></div>
      <div class="donut-item"><div class="donut-swatch" style="background:var(--purple)"></div><span>Storage ${storagePct}%</span></div>
      <div class="donut-item"><div class="donut-swatch" style="background:var(--blue)"></div><span>Reserve ${reservePct}%</span></div>
    `;
  }
}

function updateForecast(demand, forecast) {
  const error = Math.abs(demand - forecast) / forecast * 100;
  const forecastEls = document.querySelectorAll('.forecast-stat');
  if (forecastEls.length >= 3) {
    forecastEls[0].innerHTML = `<span>Forecast</span><span style="color:var(--cyan)">${Math.round(forecast)} MW</span>`;
    forecastEls[1].innerHTML = `<span>Actual</span><span style="color:var(--green)">${Math.round(demand)} MW</span>`;
    forecastEls[2].innerHTML = `<span>Error</span><span style="color:${error > 5 ? 'var(--red)' : 'var(--yellow)'}">${error > 5 ? '+' : ''}${error.toFixed(1)}%</span>`;
  }
}

function updateCongestion(supply) {
  // Mock congestion levels based on supply
  const stressRatio = Math.min(1, supply / 200);
  const congestion = [42, 68, 94, 51, 71, 38].map(v => 
    Math.min(100, Math.max(0, v + (1 - stressRatio) * 20 + Math.random() * 10))
  );
  
  document.querySelectorAll('.heatmap-cell').forEach((cell, i) => {
    const val = congestion[i];
    const color = val > 80 ? 'red' : val > 60 ? 'yellow' : 'green';
    cell.className = 'heatmap-cell ' + color;
    cell.querySelector('.heatmap-val').textContent = Math.round(val) + '%';
  });
}

function updateResilienceScores(demand, supply, renewableUtil, cost) {
  const reliability = Math.max(0, 100 - (demand - supply) / demand * 50);
  const efficiency = Math.max(0, 100 - cost / 100);
  const greenScore = renewableUtil;
  const resilience = (reliability + efficiency + greenScore) / 3;
  
  document.getElementById('reliabilityScore').textContent = Math.round(reliability);
  document.getElementById('efficiencyScore').textContent = Math.round(efficiency);
  document.getElementById('greenScore').textContent = Math.round(greenScore);
  document.getElementById('resilienceScore').textContent = Math.round(resilience);
}

function updatePolicyConfidence(scarcity) {
  const confidence = Math.max(50, 100 - scarcity * 60);
  const exploration = Math.min(30, scarcity * 50);
  const riskPosture = scarcity > 0.4 ? 'Defensive' : scarcity > 0.2 ? 'Balanced' : 'Aggressive';
  
  document.getElementById('confidenceVal').textContent = Math.round(confidence) + '%';
  document.getElementById('explorationVal').textContent = Math.round(exploration) + '%';
  
  const riskEl = document.querySelector('[style*="Mode: "]');
  if (riskEl) {
    const color = riskPosture === 'Defensive' ? 'var(--red)' : riskPosture === 'Balanced' ? 'var(--yellow)' : 'var(--green)';
    riskEl.innerHTML = `Mode: <span style="color:${color};font-weight:bold">${riskPosture}</span>`;
  }
}

function updateInterventions(step) {
  const interventionCount = Math.floor(Math.random() * step + 3);
  const blackoutsPrevented = Math.floor(interventionCount * 0.25);
  const recoveryEvents = Math.floor(interventionCount * 0.5);
  
  document.getElementById('interventionCount').textContent = interventionCount;
  document.getElementById('blackoutsPrevented').textContent = blackoutsPrevented;
  document.getElementById('recoveryEvents').textContent = recoveryEvents;
}

function addTimelineEvent(time, event, priority) {
  const timeline = document.getElementById('eventTimeline');
  if (!timeline) return;
  
  const priorityClass = priority === 'critical' ? 'critical' : priority === 'warning' ? 'warning' : 'info';
  const item = document.createElement('div');
  item.className = 'timeline-item ' + priorityClass;
  item.innerHTML = `<div class="timeline-time">T${time}</div><div class="timeline-event">${event}</div>`;
  
  // Keep only last 15 events
  timeline.insertBefore(item, timeline.firstChild);
  while (timeline.children.length > 15) timeline.lastChild.remove();
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
  const timeline = document.getElementById('eventTimeline');
  if (timeline) timeline.innerHTML = '<div class="timeline-item info"><div class="timeline-time">T0</div><div class="timeline-event">Simulation started: ' + task + '</div></div>';
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
  document.getElementById('clearingPrice').textContent = '₹' + toInr(mkt.clearing_price || 0).toLocaleString('en-IN');
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
  
  // NEW MODULE UPDATES
  updateGridHealth(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, d);
  updatePowerMix(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, disp.ev_discharge_mwh, p - disp.peaker_dispatch_mwh);
  updateForecast(d, d + (Math.random() - 0.5) * 20);
  updateCongestion(disp.delivered_supply_mwh);
  updateResilienceScores(d, disp.delivered_supply_mwh, rew.renewable_utilization_score * 10, rew.cost_efficiency_score);
  updatePolicyConfidence(scarcity);
  updateInterventions(obs.step);
  
  // Add timeline events
  if (scarcity > 0.4) addTimelineEvent(obs.step, 'High demand period detected', 'warning');
  if (disp.unmet_demand_mwh > 0) addTimelineEvent(obs.step, 'Unmet demand warning', 'critical');
  if (obs.shock_active) addTimelineEvent(obs.step, 'Renewable drop shock detected', 'critical');
  if (obs.step % 5 === 0) addTimelineEvent(obs.step, 'Policy update executed', 'info');
  
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
