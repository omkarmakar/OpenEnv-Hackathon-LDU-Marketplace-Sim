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
    .kpi-wide { flex: 1.2; }
    .kpi-compact { font-size: 8px; }
    .meter-compact { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; font-size: 8px; }
    .meter-compact-item { text-align: center; padding: 4px; background: var(--bg); border-radius: 3px; }
    .kpi-compact { font-size: 8px; }
    .kpi { background: var(--panel); padding: 8px 14px; border-radius: 4px; border: 1px solid var(--border); }
    .kpi .lbl { font-size: 9px; color: var(--dim); }
    .kpi .val { font-size: 16px; font-weight: bold; }
    .live-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; display: inline-block; animation: blink 1s infinite; }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    
    /* MAIN GRID */
    .grid { display: grid; grid-template-columns: 1fr 1.2fr 1.1fr 1fr; grid-template-rows: auto auto auto; gap: 2px; padding: 2px; height: calc(100vh - 120px); background: var(--bg); }
    .rl-panel { grid-column: span 2; }
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
    .flow-loss-label { fill: var(--dim); font-size: 8px; text-anchor: middle; }
    .flow-loss-value { fill: var(--red); font-size: 10px; font-weight: bold; text-anchor: middle; }
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
    .chart-legend { display: flex; flex-wrap: wrap; gap: 8px; font-size: 8px; color: var(--dim); margin-bottom: 6px; }
    .legend-item { display: flex; align-items: center; gap: 4px; }
    .legend-line { width: 14px; height: 2px; border-radius: 2px; }
    
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
    .donut-track { stroke: #22303f; opacity: 0.9; }
    
    /* FORECAST VS ACTUAL */
    .forecast-chart { width: 100%; height: 100%; background: var(--bg); border-radius: 4px; }
    .forecast-stat { display: flex; justify-content: space-between; font-size: 9px; margin: 4px 0; padding: 4px 0; border-bottom: 1px solid var(--border); }
    
    /* CONGESTION HEATMAP */
    .heatmap-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
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
        <div class="kpi-wide"><div class="lbl">Reward (Current)</div><div class="val green" id="kReward">0.00%</div></div>
        <div class="kpi-wide"><div class="lbl">Avg Reward</div><div class="val cyan" id="kAvgReward">0.00%</div></div>
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
          <div class="lbl" style="margin-top:4px">INR display (internal clearing uses model units)</div>
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
            <text x="25" y="30" class="node-text" id="nodeEV" fill="#a855f7" font-size="12">SOC 0%</text>
            <text x="25" y="40" class="node-label" id="nodeEVFlow">CH 0.0 | DIS 0.0</text>
            <text x="25" y="60" class="node-label">SOC / MW</text>
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
          <g transform="translate(242, 52)">
            <rect x="-38" y="-12" width="76" height="26" rx="4" fill="#161d25" stroke="var(--border)" stroke-width="1"/>
            <text x="0" y="-2" class="flow-loss-label">Transmission Loss</text>
            <text x="0" y="9" class="flow-loss-value" id="nodeLoss">0.0 MW (0.0%)</text>
          </g>
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
    <div class="panel">
      <div class="panel-title">📊 POWER MIX & FORECAST</div>
      <div class="panel-content" style="display:flex;flex-direction:column">
        <div style="flex:1">
          <div style="font-size:9px;color:var(--dim);margin-bottom:4px">Live Generation</div>
          <div class="donut-container">
            <svg class="donut-chart" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="30" fill="none" class="donut-track" stroke-width="15"/>
              <circle id="mixSolar" cx="50" cy="50" r="30" fill="none" stroke="#22c55e" stroke-width="15" opacity="0.9" transform="rotate(-90 50 50)"/>
              <circle id="mixPlant" cx="50" cy="50" r="30" fill="none" stroke="#eab308" stroke-width="15" opacity="0.9" transform="rotate(-90 50 50)"/>
              <circle id="mixEV" cx="50" cy="50" r="30" fill="none" stroke="#a855f7" stroke-width="15" opacity="0.9" transform="rotate(-90 50 50)"/>
              <text x="50" y="51" text-anchor="middle" fill="var(--text)" font-size="12" font-weight="bold" id="mixTotal">0 MW</text>
              <text x="50" y="62" text-anchor="middle" fill="var(--dim)" font-size="7">LIVE MIX</text>
            </svg>
          </div>
          <div class="donut-legend">
            <div class="donut-item"><div class="donut-swatch" style="background:var(--green)"></div><span>Solar 33%</span></div>
            <div class="donut-item"><div class="donut-swatch" style="background:var(--yellow)"></div><span>Power Plant 27%</span></div>
            <div class="donut-item"><div class="donut-swatch" style="background:var(--purple)"></div><span>EV Discharge 40%</span></div>
          </div>
        </div>
        <div style="flex:1;margin-top:6px;border-top:1px solid var(--border);padding-top:6px">
          <div style="font-size:9px;color:var(--dim);margin-bottom:4px">Load Forecast (Synthetic)</div>
          <div class="forecast-stat"><span>Forecast</span><span style="color:var(--cyan)">185 MW</span></div>
          <div class="forecast-stat"><span>Actual</span><span style="color:var(--green)">178 MW</span></div>
          <div class="forecast-stat"><span>Error</span><span style="color:var(--yellow)">+3.9%</span></div>
          <div class="forecast-stat"><span>EV SOC</span><span style="color:var(--purple)" id="evSocStat">0%</span></div>
          <div class="forecast-stat"><span>EV CH / DIS</span><span style="color:var(--purple)" id="evCdStat">0.0 / 0.0 MW</span></div>
          <div class="forecast-stat"><span>Reserve Headroom</span><span style="color:var(--blue)" id="reserveHeadroom">0 MW</span></div>
        </div>
      </div>
    </div>

    <!-- MODULE 11: GRID STABILITY ANALYTICS -->
    <div class="panel">
      <div class="panel-title">📈 GRID STABILITY ANALYTICS</div>
      <div class="panel-content">
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-line" style="background:#f97316"></span><span>Demand (Expected)</span></div>
          <div class="legend-item"><span class="legend-line" style="background:#22c55e"></span><span>Solar (Expected)</span></div>
          <div class="legend-item"><span class="legend-line" style="background:#38bdf8"></span><span>Demand (Actual)</span></div>
          <div class="legend-item"><span class="legend-line" style="background:#a855f7"></span><span>Solar (Actual)</span></div>
        </div>
        <canvas id="historyChart" class="chart-box"></canvas>
      </div>
    </div>
    
    <!-- MODULE 4: CONGESTION / TRANSMISSION HEATMAP -->
    <div class="panel">
      <div class="panel-title">🔥 TRANSMISSION HEATMAP</div>
      <div class="panel-content">
        <div class="heatmap-grid">
          <div class="heatmap-cell green" id="cellSolarPlant">
            <div class="heatmap-val" id="lineSolarPlant">0%</div>
            <div class="heatmap-lbl">Solar -> Plant</div>
          </div>
          <div class="heatmap-cell yellow" id="cellPlantLDU">
            <div class="heatmap-val" id="linePlantLDU">0%</div>
            <div class="heatmap-lbl">Plant -> LDU</div>
          </div>
          <div class="heatmap-cell red" id="cellEVLDU">
            <div class="heatmap-val" id="lineEVLDU">0%</div>
            <div class="heatmap-lbl">EV -> LDU</div>
          </div>
          <div class="heatmap-cell green" id="cellLDULoad">
            <div class="heatmap-val" id="lineLDULoad">0%</div>
            <div class="heatmap-lbl">LDU -> Load</div>
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
            <div id="bidDepthRows">
              <div class="ob-row"><span>₹0</span><span style="color:var(--red)">-0 MW</span></div>
            </div>
          </div>
          <div class="ob-section">
            <div class="ob-header">ASK DEPTH</div>
            <div id="askDepthRows">
              <div class="ob-row"><span>₹0</span><span style="color:var(--green)">+0 MW</span></div>
            </div>
          </div>
        </div>
        <div class="ob-spread">
          <div style="font-size:8px;color:var(--dim)">Spread</div>
          <div style="font-weight:bold;color:var(--cyan)" id="spreadVal">₹0/MWh</div>
          <div style="font-size:8px;color:var(--dim);margin-top:2px" id="liquidityVal">Liquidity: -</div>
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
        <div id="threatList" style="margin-top:8px"></div>
      </div>
    </div>
    
    <!-- RL DECISION ENHANCED WITH POLICY CONFIDENCE + CORRECTION SAVINGS -->
    <div class="panel rl-panel">
      <div class="panel-title">🧠 RL DECISION ENGINE</div>
      <div class="panel-content" style="display:flex;flex-direction:column">
        <div style="flex:0">
          <div class="brain-card">
            <div class="policy-name" id="policyName">ADAPTIVE POLICY</div>
            <div class="policy-reason" id="policyReason">Analyzing grid state...</div>
          </div>
          <div class="score-breakdown" id="scoreBreakdown" style="font-size:8px"></div>
          <div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">
            <div style="font-size:8px;color:var(--dim);margin-bottom:4px">Session Performance</div>
            <div class="meter-compact">
              <div class="meter-compact-item"><div style="color:var(--cyan)" id="sessionSteps">0</div><div style="font-size:7px;color:var(--dim)">Steps</div></div>
              <div class="meter-compact-item"><div style="color:var(--green)" id="sessionAvg">0%</div><div style="font-size:7px;color:var(--dim)">Avg Score</div></div>
              <div class="meter-compact-item"><div style="color:var(--yellow)" id="sessionBest">-</div><div style="font-size:7px;color:var(--dim)">Best Pol</div></div>
            </div>
          </div>
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
            Mode: <span id="riskMode" style="color:var(--yellow);font-weight:bold">Defensive</span>
          </div>
        </div>
        <div style="border-top:1px solid var(--border);margin-top:6px;padding-top:6px;flex:1">
          <div style="font-size:9px;color:var(--dim);margin-bottom:6px">LDU Interventions</div>
          <div class="savings-grid">
            <div class="saving-item">
              <div class="saving-icon">🛡️</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">LDU Corrections</div><div class="saving-val" id="interventionCount">0</div></div>
            </div>
            <div class="saving-item">
              <div class="saving-icon">🚫</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">Demand Met Steps</div><div class="saving-val" id="blackoutsPrevented">0</div></div>
            </div>
            <div class="saving-item">
              <div class="saving-icon">⚡</div>
              <div style="flex:1"><div style="font-size:8px;color:var(--dim)">Recovery Events</div><div class="saving-val" id="recoveryEvents">0</div></div>
            </div>
          </div>
        </div>
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
let dayCurveData = [];
const runtimeStats = { steps: 0, correctionSteps: 0, zeroUnmetSteps: 0, recoveryEvents: 0, prevUnmet: 0, cumulativeReward: 0 };
const INR_PER_USD = 100;

const TASK_CURVE_CONFIG = {
  default: { max_steps: 24, initial_demand_mwh: 120.0, initial_renewable_mwh: 70.0, demand_trend_mwh: 1.2, renewable_trend_mwh: -0.6 },
  long_horizon: { max_steps: 48, initial_demand_mwh: 135.0, initial_renewable_mwh: 78.0, demand_trend_mwh: 1.5, renewable_trend_mwh: -0.8 },
  stress_shock: { max_steps: 30, initial_demand_mwh: 150.0, initial_renewable_mwh: 85.0, demand_trend_mwh: 2.0, renewable_trend_mwh: -1.0 }
};

function toInr(priceUsd) {
  return Math.round(priceUsd * INR_PER_USD);
}

function dailyProfile(step, maxSteps) {
  const phase = (step % maxSteps) / maxSteps;
  const morningPeak = Math.exp(-Math.pow((phase - 0.33) / 0.10, 2));
  const eveningPeak = Math.exp(-Math.pow((phase - 0.75) / 0.12, 2));
  const demandMultiplier = 0.90 + 0.18 * morningPeak + 0.35 * eveningPeak;

  const middaySolar = Math.exp(-Math.pow((phase - 0.50) / 0.18, 2));
  const renewableMultiplier = Math.max(0.05, 0.15 + 1.15 * middaySolar);
  return { demandMultiplier, renewableMultiplier };
}

function buildDayCurve(taskId) {
  const cfg = TASK_CURVE_CONFIG[taskId] || TASK_CURVE_CONFIG.default;
  let demand = cfg.initial_demand_mwh;
  let renewable = cfg.initial_renewable_mwh;
  const points = [];

  for (let step = 0; step < cfg.max_steps; step += 1) {
    points.push({ demand, renewable });
    const { demandMultiplier, renewableMultiplier } = dailyProfile(step, cfg.max_steps);
    demand = Math.max(20.0, demand * demandMultiplier + cfg.demand_trend_mwh);
    renewable = Math.max(0.0, renewable * renewableMultiplier + cfg.renewable_trend_mwh);
  }

  return points;
}

const cvs = document.getElementById('historyChart');
const ctx = cvs.getContext('2d');
const dpr = window.devicePixelRatio || 1;

function resize() {
  const r = cvs.parentElement.getBoundingClientRect();
  cvs.width = r.width * dpr; cvs.height = r.height * dpr;
  cvs.style.width = r.width + 'px'; cvs.style.height = r.height + 'px';
  ctx.scale(dpr, dpr);
  drawChart();
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

function updateMarketMicrostructure(market) {
  const book = market && market.post_signal_book ? market.post_signal_book : [];
  const bidRowsEl = document.getElementById('bidDepthRows');
  const askRowsEl = document.getElementById('askDepthRows');
  const spreadEl = document.getElementById('spreadVal');
  const liqEl = document.getElementById('liquidityVal');
  if (!bidRowsEl || !askRowsEl || !spreadEl || !liqEl) return;

  const bids = book
    .filter(b => b.bid_type === 'demand')
    .sort((a, b) => b.price_usd_per_mwh - a.price_usd_per_mwh)
    .slice(0, 3);
  const asks = book
    .filter(b => b.bid_type === 'supply')
    .sort((a, b) => a.price_usd_per_mwh - b.price_usd_per_mwh)
    .slice(0, 3);

  bidRowsEl.innerHTML = bids.length
    ? bids.map(b => `<div class="ob-row"><span>₹${toInr(b.price_usd_per_mwh).toLocaleString('en-IN')}</span><span style="color:var(--red)">-${Math.round(Math.max(0, b.quantity_mwh))} MW</span></div>`).join('')
    : '<div class="ob-row"><span>₹0</span><span style="color:var(--red)">-0 MW</span></div>';

  askRowsEl.innerHTML = asks.length
    ? asks.map(b => `<div class="ob-row"><span>₹${toInr(b.price_usd_per_mwh).toLocaleString('en-IN')}</span><span style="color:var(--green)">+${Math.round(Math.max(0, b.quantity_mwh))} MW</span></div>`).join('')
    : '<div class="ob-row"><span>₹0</span><span style="color:var(--green)">+0 MW</span></div>';

  const bestBid = bids.length ? bids[0].price_usd_per_mwh : 0;
  const bestAsk = asks.length ? asks[0].price_usd_per_mwh : 0;
  const spread = Math.max(0, bestBid - bestAsk);
  spreadEl.textContent = `₹${toInr(spread).toLocaleString('en-IN')}/MWh`;

  const supply = market.total_supply_offered || 0;
  const demand = market.total_demand_bid || 0;
  const depthRatio = supply / Math.max(1e-6, demand);
  const liquidity = depthRatio > 1.05 ? 'Excellent' : depthRatio > 0.9 ? 'Moderate' : 'Tight';
  liqEl.textContent = `Liquidity: ${liquidity}`;
}

function updatePowerFlow(renew, peak, evCharge, evDischarge, evStorage, evCapacity, delivered, loss) {
  // SVG nodes
  document.getElementById('nodeRenew').textContent = Math.round(renew);
  document.getElementById('nodePeaker').textContent = Math.round(peak);
  const socPct = Math.max(0, Math.min(100, (evStorage / Math.max(1e-6, evCapacity)) * 100));
  const evSocEl = document.getElementById('nodeEV');
  evSocEl.textContent = `SOC ${socPct.toFixed(0)}%`;
  evSocEl.style.fill = socPct < 25 ? 'var(--red)' : socPct < 45 ? 'var(--yellow)' : 'var(--purple)';
  document.getElementById('nodeEVFlow').textContent = `CH ${evCharge.toFixed(1)} | DIS ${evDischarge.toFixed(1)}`;
  document.getElementById('nodeLDU').textContent = Math.round(delivered);
  document.getElementById('nodeLoad').textContent = Math.round(delivered);
  const grossFlow = Math.max(1e-6, renew + peak + Math.max(0, evDischarge));
  const lossPct = (loss / grossFlow) * 100;
  const lossEl = document.getElementById('nodeLoss');
  lossEl.textContent = `${loss.toFixed(1)} MW (${lossPct.toFixed(1)}%)`;
  lossEl.style.fill = lossPct < 3.5 ? 'var(--yellow)' : 'var(--red)';

  const socStatEl = document.getElementById('evSocStat');
  if (socStatEl) {
    socStatEl.textContent = `${socPct.toFixed(0)}% (${evStorage.toFixed(1)} MWh)`;
    socStatEl.style.color = socPct < 25 ? 'var(--red)' : socPct < 45 ? 'var(--yellow)' : 'var(--purple)';
  }
  const cdStatEl = document.getElementById('evCdStat');
  if (cdStatEl) {
    cdStatEl.textContent = `${evCharge.toFixed(1)} / ${evDischarge.toFixed(1)} MW`;
  }
}

function updateDispatch(d) {
  if (d.corrections && d.corrections.length > 0) {
    d.corrections.forEach(c => log(c, 'warn'));
  }
}

function updateRisk(supply, demand) {
  const stress = Math.max(0, (demand - supply) / demand * 100);
  const blackout = Math.max(0, demand - supply) / demand * 100;

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
  const reliabilityPct = (r.demand_satisfaction_score * 100).toFixed(0);
  const economicPct = (r.cost_efficiency_score * 100).toFixed(0);
  const greenPct = (r.renewable_utilization_score * 100).toFixed(0);
  const penaltyVal = (r.infeasibility_penalty + r.blackout_penalty).toFixed(2);
  const totalPct = (r.score * 100).toFixed(1);
  document.getElementById('scoreBreakdown').innerHTML = `
    <div class="score-row"><span>Reliability</span><span class="score-pos">${reliabilityPct}%</span></div>
    <div class="score-row"><span>Economic</span><span class="score-pos">${economicPct}%</span></div>
    <div class="score-row"><span>Green</span><span class="score-pos">${greenPct}%</span></div>
    <div class="score-row"><span>Penalty Index</span><span class="score-neg">${penaltyVal}</span></div>
    <div class="score-row score-total"><span>TOTAL</span><span>${totalPct}%</span></div>
    <div class="score-row" style="font-size:8px;color:var(--dim)"><span>Raw Score</span><span>${r.score.toFixed(3)}</span></div>
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

function updatePowerMix(renew, peak, ev) {
  const evDispatch = Math.max(0, ev);
  const total = renew + peak + evDispatch;
  if (total === 0) return;

  const solarPct = (renew / total * 100);
  const plantPct = (peak / total * 100);
  const evPct = (evDispatch / total * 100);

  const CIRC = 2 * Math.PI * 30;
  const segments = [
    { id: 'mixSolar', pct: solarPct },
    { id: 'mixPlant', pct: plantPct },
    { id: 'mixEV', pct: evPct },
  ];
  let offset = 0;
  segments.forEach(seg => {
    const el = document.getElementById(seg.id);
    if (!el) return;
    const len = (Math.max(0, seg.pct) / 100) * CIRC;
    el.style.strokeDasharray = `${len} ${Math.max(0, CIRC - len)}`;
    el.style.strokeDashoffset = `${-offset}`;
    offset += len;
  });

  const totalEl = document.getElementById('mixTotal');
  if (totalEl) totalEl.textContent = `${Math.round(total)} MW`;
  
  // Update legend
  const legend = document.querySelector('.donut-legend');
  if (legend) {
    legend.innerHTML = `
      <div class="donut-item"><div class="donut-swatch" style="background:var(--green)"></div><span>Solar ${solarPct.toFixed(0)}%</span></div>
      <div class="donut-item"><div class="donut-swatch" style="background:var(--yellow)"></div><span>Power Plant ${plantPct.toFixed(0)}%</span></div>
      <div class="donut-item"><div class="donut-swatch" style="background:var(--purple)"></div><span>EV Discharge ${evPct.toFixed(0)}%</span></div>
    `;
  }
}

function updateForecast(demand, forecast) {
  const error = Math.abs(demand - forecast) / forecast * 100;
  const forecastEls = document.querySelectorAll('.forecast-stat');
  if (forecastEls.length >= 3) {
    forecastEls[0].innerHTML = `<span>Forecast (Synthetic)</span><span style="color:var(--cyan)">${Math.round(forecast)} MW</span>`;
    forecastEls[1].innerHTML = `<span>Actual</span><span style="color:var(--green)">${Math.round(demand)} MW</span>`;
    forecastEls[2].innerHTML = `<span>Error</span><span style="color:${error > 5 ? 'var(--red)' : 'var(--yellow)'}">${error > 5 ? '+' : ''}${error.toFixed(1)}%</span>`;
  }
}

function setLineLoad(cellId, valId, pct) {
  const cell = document.getElementById(cellId);
  const val = document.getElementById(valId);
  if (!cell || !val) return;
  const pctSafe = Math.max(0, Math.min(100, pct));
  const color = pctSafe > 80 ? 'red' : pctSafe > 60 ? 'yellow' : 'green';
  cell.className = 'heatmap-cell ' + color;
  val.textContent = Math.round(pctSafe) + '%';
}

function updateCongestion(renew, peak, ev, delivered, demand, peakerCap) {
  const demandBase = Math.max(1, demand);
  const plantCapBase = Math.max(1, peakerCap);

  const solarToPlant = (renew / demandBase) * 100;
  const plantToLdu = (peak / plantCapBase) * 100;
  const evToLdu = (Math.max(0, ev) / demandBase) * 100;
  const lduToLoad = (delivered / demandBase) * 100;

  setLineLoad('cellSolarPlant', 'lineSolarPlant', solarToPlant);
  setLineLoad('cellPlantLDU', 'linePlantLDU', plantToLdu);
  setLineLoad('cellEVLDU', 'lineEVLDU', evToLdu);
  setLineLoad('cellLDULoad', 'lineLDULoad', lduToLoad);
}

function updateResilienceScores(reward) {
  const reliability = Math.max(0, Math.min(100, reward.demand_satisfaction_score * 100));
  const efficiency = Math.max(0, Math.min(100, reward.cost_efficiency_score * 100));
  const greenScore = Math.max(0, Math.min(100, reward.renewable_utilization_score * 100));
  const resilience = Math.max(0, Math.min(100, reward.score * 100));
  
  document.getElementById('reliabilityScore').textContent = Math.round(reliability);
  document.getElementById('efficiencyScore').textContent = Math.round(efficiency);
  document.getElementById('greenScore').textContent = Math.round(greenScore);
  document.getElementById('resilienceScore').textContent = Math.round(resilience);
}

function updatePolicyConfidence(reward, dispatch, scarcity) {
  const unmetRatio = dispatch.unmet_demand_mwh / Math.max(1, dispatch.delivered_supply_mwh + dispatch.unmet_demand_mwh);
  const confidence = Math.max(
    5,
    Math.min(
      99,
      20 + reward.score * 70 + (1 - unmetRatio) * 10 - dispatch.correction_count * 4 - scarcity * 15
    )
  );
  const exploration = Math.max(5, Math.min(45, 8 + scarcity * 30 + (1 - reward.score) * 20));
  const riskPosture = unmetRatio > 0.05 || scarcity > 0.45 ? 'Defensive' : scarcity > 0.2 ? 'Balanced' : 'Aggressive';
  
  document.getElementById('confidenceVal').textContent = Math.round(confidence) + '%';
  document.getElementById('explorationVal').textContent = Math.round(exploration) + '%';
  
  const riskEl = document.getElementById('riskMode');
  if (riskEl) {
    const color = riskPosture === 'Defensive' ? 'var(--red)' : riskPosture === 'Balanced' ? 'var(--yellow)' : 'var(--green)';
    riskEl.style.color = color;
    riskEl.textContent = riskPosture;
  }
}

function updateInterventions(dispatch) {
  runtimeStats.steps += 1;
  if (dispatch.correction_count > 0) runtimeStats.correctionSteps += 1;
  if (dispatch.unmet_demand_mwh <= 1e-6) runtimeStats.zeroUnmetSteps += 1;
  if (runtimeStats.prevUnmet > 1e-6 && dispatch.unmet_demand_mwh <= 1e-6) runtimeStats.recoveryEvents += 1;
  runtimeStats.prevUnmet = dispatch.unmet_demand_mwh;

  document.getElementById('interventionCount').textContent = runtimeStats.correctionSteps;
  document.getElementById('blackoutsPrevented').textContent = runtimeStats.zeroUnmetSteps;
  document.getElementById('recoveryEvents').textContent = runtimeStats.recoveryEvents;
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

function drawChart() {
  const w = cvs.width / dpr, h = cvs.height / dpr;
  ctx.fillStyle = '#0a0e12';
  ctx.fillRect(0, 0, w, h);
  if (!dayCurveData || dayCurveData.length < 2) return;

  const padL = 26, padR = 8, padT = 8, padB = 18;
  const cw = Math.max(1, w - padL - padR);
  const ch = Math.max(1, h - padT - padB);

  const maxExpected = Math.max(
    ...dayCurveData.map(p => p.demand),
    ...dayCurveData.map(p => p.renewable),
    150
  );
  const maxActual = historyData.length > 0
    ? Math.max(...historyData.map(p => p.demand), ...historyData.map(p => p.renewable), 0)
    : 0;
  const yMax = Math.max(maxExpected, maxActual) * 1.1;
  const totalSteps = dayCurveData.length;

  const xAt = i => padL + (i / Math.max(1, totalSteps - 1)) * cw;
  const yAt = v => padT + (1 - (v / Math.max(1, yMax))) * ch;

  ctx.strokeStyle = 'rgba(100,116,139,0.35)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const y = padT + (i / 4) * ch;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(w - padR, y);
    ctx.stroke();
  }

  ctx.strokeStyle = '#f97316';
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  dayCurveData.forEach((p, i) => {
    const x = xAt(i), y = yAt(p.demand);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.strokeStyle = '#22c55e';
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  dayCurveData.forEach((p, i) => {
    const x = xAt(i), y = yAt(p.renewable);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();

  if (historyData.length >= 2) {
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    historyData.forEach((p, i) => {
      const x = xAt(i), y = yAt(p.demand);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.strokeStyle = '#a855f7';
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    historyData.forEach((p, i) => {
      const x = xAt(i), y = yAt(p.renewable);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  const currentStep = Math.max(0, Math.min(totalSteps - 1, historyData.length - 1));
  const markerX = xAt(currentStep);
  ctx.strokeStyle = 'rgba(59,130,246,0.7)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 3]);
  ctx.beginPath();
  ctx.moveTo(markerX, padT);
  ctx.lineTo(markerX, h - padB);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#64748b';
  ctx.font = '9px Courier New';
  ctx.fillText('T0', padL - 4, h - 4);
  ctx.fillText('T' + (totalSteps - 1), w - padR - 22, h - 4);
  ctx.fillText(Math.round(yMax) + ' MW', 2, padT + 7);
}

async function reset() {
  const task = document.getElementById('taskSel').value;
  const data = await api('/reset', {task_id: task, seed: 42});
  sessionId = data.session_id;
  historyData.length = 0;
runtimeStats.steps = 0;
  runtimeStats.correctionSteps = 0;
  runtimeStats.zeroUnmetSteps = 0;
  runtimeStats.recoveryEvents = 0;
  runtimeStats.prevUnmet = 0;
  runtimeStats.cumulativeReward = 0;
  dayCurveData = buildDayCurve(task);
  drawChart();
  document.getElementById('kScenario').textContent = task.toUpperCase();
  document.getElementById('kStatus').innerHTML = '<span class="live-dot"></span> RUNNING';
  const timeline = document.getElementById('eventTimeline');
  if (timeline) timeline.innerHTML = '<div class="timeline-item info"><div class="timeline-time">T0</div><div class="timeline-event">Simulation started: ' + task + '</div></div>';
  const threatList = document.getElementById('threatList');
  if (threatList) threatList.innerHTML = '';
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
  const scarcity = obs.scarcity_index || 0;
  const actionResp = await api('/act?session_id=' + sessionId, {policy: pol, personality: 'balanced'});
  const action = {action: actionResp.action};

  const res = await api('/step?session_id=' + sessionId, action);
  const info = res.info, disp = info.dispatch, mkt = info.market;
  
document.getElementById('kStep').textContent = (obs.step + 1) + '/' + obs.max_steps;
  const rewardPct = res.reward.score * 100;
  runtimeStats.cumulativeReward += res.reward.score;
  const avgRewardPct = (runtimeStats.cumulativeReward / runtimeStats.steps) * 100;
  
  const kRewardEl = document.getElementById('kReward');
  kRewardEl.textContent = rewardPct.toFixed(1) + '%';
  kRewardEl.style.color = rewardPct >= 75 ? 'var(--green)' : rewardPct >= 45 ? 'var(--yellow)' : 'var(--red)';
  
  const kAvgEl = document.getElementById('kAvgReward');
  if (kAvgEl) {
    kAvgEl.textContent = avgRewardPct.toFixed(1) + '%';
    kAvgEl.style.color = avgRewardPct >= 75 ? 'var(--green)' : avgRewardPct >= 45 ? 'var(--yellow)' : 'var(--red)';
  }
  
  // Update session performance display
  const sessionStepsEl = document.getElementById('sessionSteps');
  const sessionAvgEl = document.getElementById('sessionAvg');
  const sessionBestEl = document.getElementById('sessionBest');
  if (sessionStepsEl) sessionStepsEl.textContent = runtimeStats.steps;
  if (sessionAvgEl) {
    sessionAvgEl.textContent = avgRewardPct.toFixed(0) + '%';
    sessionAvgEl.style.color = avgRewardPct >= 75 ? 'var(--green)' : avgRewardPct >= 45 ? 'var(--yellow)' : 'var(--red)';
  }
  if (sessionBestEl) {
    const currentPol = pol;
    const polBench = currentPol === 'adaptive' ? '44%' : currentPol === 'heuristic' ? '30%' : '21%';
    sessionBestEl.textContent = polBench;
  }
  
  updateBidLadder(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, d);
  updateMarketMicrostructure(mkt);
  document.getElementById('clearingPrice').textContent = '₹' + toInr(mkt.clearing_price || 0).toLocaleString('en-IN');
  document.getElementById('clearingMW').textContent = (mkt.cleared_mwh || 0).toFixed(0) + ' MW';
  
  updatePowerFlow(
    disp.renewable_dispatch_mwh,
    disp.peaker_dispatch_mwh,
    disp.ev_charge_mwh,
    disp.ev_discharge_mwh,
    res.observation.ev_storage_mwh,
    res.observation.ev_storage_capacity_mwh,
    disp.delivered_supply_mwh,
    disp.transmission_loss_mwh
  );
  updateDispatch(disp);
  
  historyData.push({demand: d, renewable: r, supply: disp.delivered_supply_mwh});
  drawChart();
  
  updateRisk(disp.delivered_supply_mwh, d);
  
  const rew = res.reward;
  document.getElementById('policyName').textContent = pol.toUpperCase() + ' POLICY';
  const metPct = (rew.demand_satisfaction_score * 100).toFixed(0);
  const penalty = (rew.infeasibility_penalty + rew.blackout_penalty).toFixed(2);
  document.getElementById('policyReason').textContent = `Demand met ${metPct}% | Scarcity ${Math.round(scarcity * 100)}% | Penalty ${penalty}`;
  updateScore(rew);
  
  // NEW MODULE UPDATES
  updateGridHealth(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, d);
  const reserveHeadroom = Math.max(0, p - disp.peaker_dispatch_mwh);
  updatePowerMix(disp.renewable_dispatch_mwh, disp.peaker_dispatch_mwh, disp.ev_discharge_mwh);
  document.getElementById('reserveHeadroom').textContent = reserveHeadroom.toFixed(0) + ' MW';
  updateForecast(d, d + (Math.random() - 0.5) * 20);
  updateCongestion(
    disp.renewable_dispatch_mwh,
    disp.peaker_dispatch_mwh,
    disp.ev_discharge_mwh,
    disp.delivered_supply_mwh,
    d,
    p
  );
  updateResilienceScores(rew);
  updatePolicyConfidence(rew, disp, scarcity);
  updateInterventions(disp);
  
  // Add timeline events
  if (scarcity > 0.4) addTimelineEvent(obs.step, 'High demand period detected', 'warning');
  if (disp.unmet_demand_mwh > 0) addTimelineEvent(obs.step, 'Unmet demand warning', 'critical');
  if (obs.shock_active) addTimelineEvent(obs.step, 'Renewable drop shock detected', 'critical');
  if (obs.step % 5 === 0) addTimelineEvent(obs.step, 'Policy update executed', 'info');
  
  if (obs.shock_active) {
    log('⚡ SHOCK!', 'shock');
    const threatList = document.getElementById('threatList');
    if (threatList) threatList.innerHTML = '<div class="threat">⚡ Renewable drop detected!</div>';
  }
}

function play() { pause(); timer = setInterval(step, 400); }
function pause() { if (timer) clearInterval(timer); timer = null; }
async function shock() {
  if (!sessionId) return;
  await api('/inject-shock', {renewable_drop_mwh: 25});
  log('⚡ MANUAL SHOCK', 'shock');
  const threatList = document.getElementById('threatList');
  if (threatList) threatList.innerHTML = '<div class="threat">⚡ Manual shock: -25 MW</div>';
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
