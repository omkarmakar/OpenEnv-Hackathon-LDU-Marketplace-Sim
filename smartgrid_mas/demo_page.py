def build_demo_html() -> str:
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Grid Operations War Room</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
      --bg-0: #06090e;
      --bg-1: #0b121a;
      --bg-2: #111b27;
      --panel: #0f1722;
      --panel-hi: #152334;
      --line: #2a3d53;
      --line-hi: #3a5c7d;
      --text: #d9e5f1;
      --text-dim: #89a0b7;
      --green: #2bd47f;
      --amber: #f0b547;
      --red: #ff4f57;
      --blue: #6cc7ff;
      --teal: #2ee7d6;
      --critical-glow: 0 0 20px rgba(255, 79, 87, 0.38);
      --stress-glow: 0 0 16px rgba(240, 181, 71, 0.35);
      --ok-glow: 0 0 16px rgba(43, 212, 127, 0.28);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      background:
        radial-gradient(1200px 520px at 20% -15%, rgba(68, 157, 255, 0.16), transparent 60%),
        radial-gradient(1000px 440px at 95% 0%, rgba(46, 231, 214, 0.09), transparent 58%),
        linear-gradient(180deg, var(--bg-0), var(--bg-1));
      color: var(--text);
      font-family: 'IBM Plex Mono', monospace;
      min-height: 100%;
      overflow: hidden;
    }

    .war-room {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      position: relative;
    }

    .scanlines {
      pointer-events: none;
      position: fixed;
      inset: 0;
      background: repeating-linear-gradient(
        to bottom,
        rgba(255, 255, 255, 0.02),
        rgba(255, 255, 255, 0.02) 1px,
        transparent 1px,
        transparent 4px
      );
      opacity: 0.15;
      z-index: 10;
    }

    .command-strip {
      height: 108px;
      border-bottom: 1px solid var(--line-hi);
      background: linear-gradient(90deg, #0b1118 0%, #0f1c2b 45%, #0c1118 100%);
      display: grid;
      grid-template-columns: 1.1fr 2.2fr 0.9fr;
      gap: 12px;
      padding: 10px 16px;
      z-index: 2;
    }

    .strip-block {
      background: rgba(15, 23, 34, 0.84);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .title-stack { display: flex; flex-direction: column; gap: 2px; }
    .title-main {
      font-family: 'Orbitron', sans-serif;
      font-size: 17px;
      letter-spacing: 1px;
      color: var(--blue);
      text-transform: uppercase;
      white-space: nowrap;
    }
    .title-sub {
      color: var(--text-dim);
      font-size: 10px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }

    .tracker-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      width: 100%;
    }

    .tracker {
      background: var(--panel-hi);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 5px 8px;
      min-width: 0;
    }
    .tracker .label {
      color: var(--text-dim);
      font-size: 9px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }
    .tracker .value {
      margin-top: 2px;
      font-weight: 600;
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 8px;
      width: 100%;
    }

    .kpi-card {
      height: 86px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(17, 27, 39, 0.9), rgba(12, 19, 29, 0.95));
      padding: 6px 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
    }
    .kpi-card .k-label {
      font-size: 9px;
      letter-spacing: 0.8px;
      color: var(--text-dim);
      text-transform: uppercase;
    }
    .kpi-card .k-value {
      font-family: 'Orbitron', sans-serif;
      font-size: 19px;
      line-height: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .kpi-card .k-state {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--text-dim);
    }
    .kpi-card.state-green { box-shadow: var(--ok-glow); }
    .kpi-card.state-amber { box-shadow: var(--stress-glow); }
    .kpi-card.state-red { box-shadow: var(--critical-glow); }

    .status-block {
      justify-content: space-between;
      align-items: stretch;
      display: grid;
      grid-template-rows: 1fr 1fr;
      gap: 8px;
      width: 100%;
    }

    .status-cell {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-hi);
      padding: 7px 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 8px;
      animation: heartbeat 1.6s infinite;
      box-shadow: var(--ok-glow);
      background: var(--green);
    }

    .mission-main {
      flex: 1;
      min-height: 0;
      display: grid;
      grid-template-columns: 1.15fr 1.35fr 1fr;
      grid-template-rows: 1fr 0.9fr;
      gap: 6px;
      padding: 6px;
      padding-right: 54px;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, rgba(15, 23, 34, 0.98), rgba(11, 18, 26, 0.95));
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
      position: relative;
    }

    .panel-head {
      height: 34px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 10px;
      background: rgba(18, 29, 42, 0.88);
      flex-shrink: 0;
    }

    .panel-title {
      text-transform: uppercase;
      font-family: 'Orbitron', sans-serif;
      letter-spacing: 0.8px;
      font-size: 11px;
      color: var(--blue);
    }

    .panel-tag {
      font-size: 9px;
      padding: 2px 6px;
      border: 1px solid var(--line-hi);
      border-radius: 4px;
      color: var(--text-dim);
      text-transform: uppercase;
    }

    .market-body {
      display: grid;
      grid-template-rows: 1.2fr 0.65fr 0.9fr;
      gap: 8px;
      padding: 8px;
      min-height: 0;
      flex: 1;
    }

    .order-book {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      min-height: 0;
      padding: 6px;
    }

    .book-col { min-height: 0; overflow: auto; }
    .book-head {
      font-size: 9px;
      color: var(--text-dim);
      text-transform: uppercase;
      margin-bottom: 4px;
      letter-spacing: 0.6px;
    }

    .bid-row {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr 0.8fr;
      font-size: 10px;
      border-left: 3px solid transparent;
      border-bottom: 1px solid rgba(58, 92, 125, 0.2);
      padding: 3px 4px;
      gap: 4px;
    }
    .bid-row.ren { border-color: var(--green); }
    .bid-row.peak { border-color: var(--amber); }
    .bid-row.dem { border-color: var(--blue); }

    .clearing-band {
      border: 1px solid var(--line-hi);
      border-radius: 6px;
      background: linear-gradient(90deg, rgba(14, 30, 43, 0.92), rgba(20, 41, 58, 0.82));
      display: grid;
      grid-template-columns: 1fr 1fr;
      align-items: center;
      padding: 8px;
      gap: 8px;
    }

    .clearing-main {
      font-family: 'Orbitron', sans-serif;
      font-size: 25px;
      color: var(--teal);
      line-height: 1;
    }
    .clearing-sub {
      font-size: 10px;
      color: var(--text-dim);
      text-transform: uppercase;
      margin-top: 3px;
    }

    .leader-row {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
    }

    .meter {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      padding: 6px;
    }

    .meter .m-label { font-size: 9px; color: var(--text-dim); text-transform: uppercase; }
    .meter .m-value { font-family: 'Orbitron', sans-serif; font-size: 16px; margin-top: 2px; }
    .meter-track {
      margin-top: 6px;
      height: 6px;
      border-radius: 8px;
      background: #1e2f41;
      overflow: hidden;
    }
    .meter-fill {
      height: 100%;
      width: 0%;
      transition: width 0.3s ease;
      background: linear-gradient(90deg, var(--green), var(--amber), var(--red));
    }

    .agent-strip {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      padding: 6px;
      min-height: 0;
    }

    .agent-card {
      border: 1px solid #294159;
      border-radius: 5px;
      padding: 6px;
      min-width: 0;
      background: rgba(18, 31, 44, 0.8);
      display: flex;
      flex-direction: column;
      gap: 3px;
      font-size: 9px;
    }
    .agent-name { color: var(--blue); font-family: 'Orbitron', sans-serif; letter-spacing: 0.6px; font-size: 10px; }
    .agent-val { color: var(--text); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .twin-wrap {
      padding: 8px;
      flex: 1;
      min-height: 0;
      background:
        radial-gradient(700px 280px at 50% 100%, rgba(46, 231, 214, 0.08), transparent 70%),
        linear-gradient(180deg, rgba(13, 20, 30, 0.95), rgba(11, 17, 25, 0.98));
    }

    .twin-svg {
      width: 100%;
      height: 100%;
      display: block;
      border: 1px solid #23394f;
      border-radius: 8px;
      background: rgba(8, 14, 20, 0.92);
    }

    .grid-node { fill: #12263a; stroke: #3a5c7d; stroke-width: 2; }
    .node-text { fill: var(--text); font-size: 10px; text-anchor: middle; }
    .node-power { fill: var(--teal); font-size: 12px; font-family: 'Orbitron', sans-serif; text-anchor: middle; }
    .power-line {
      stroke: #4fd6a4;
      stroke-width: 3;
      fill: none;
      opacity: 0.8;
      transition: stroke-width 0.25s ease, stroke 0.25s ease, filter 0.25s ease;
      marker-end: url(#arrowGreen);
      stroke-dasharray: 6 7;
      animation: dashFlow 1.5s linear infinite;
    }

    .congested {
      stroke: var(--red);
      filter: drop-shadow(0 0 4px rgba(255, 79, 87, 0.8));
      marker-end: url(#arrowRed);
    }

    .flow-particle {
      fill: #96ffe1;
      opacity: 0.9;
      transition: transform 0.3s ease;
    }

    .dispatch-body {
      padding: 8px;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 8px;
      flex: 1;
      min-height: 0;
    }

    .dispatch-table {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      overflow: hidden;
    }

    .d-row {
      display: grid;
      grid-template-columns: 1.6fr 0.8fr;
      border-bottom: 1px solid rgba(58, 92, 125, 0.24);
      font-size: 11px;
      padding: 6px 8px;
    }
    .d-row:last-child { border-bottom: none; }
    .d-label { color: var(--text-dim); text-transform: uppercase; font-size: 9px; }
    .d-val { text-align: right; font-weight: 600; }

    .event-tape {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(13, 21, 31, 0.95);
      padding: 6px;
      overflow: auto;
      min-height: 0;
    }

    .event-row {
      font-size: 10px;
      display: grid;
      grid-template-columns: 42px 1fr;
      gap: 6px;
      padding: 4px 2px;
      border-bottom: 1px solid rgba(58, 92, 125, 0.2);
    }
    .event-row:last-child { border-bottom: none; }
    .event-ts { color: var(--text-dim); }
    .event-row.warn { color: var(--amber); }
    .event-row.error { color: var(--red); }
    .event-row.shock { color: #ff7b5f; text-shadow: 0 0 8px rgba(255, 123, 95, 0.35); }

    .stability-wrap,
    .risk-wrap,
    .brain-wrap {
      padding: 8px;
      min-height: 0;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .legend {
      display: flex;
      gap: 10px;
      font-size: 9px;
      color: var(--text-dim);
      text-transform: uppercase;
    }

    .dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; margin-right: 4px; }

    .chart-frame {
      flex: 1;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: rgba(10, 16, 24, 0.95);
      min-height: 0;
      position: relative;
    }

    #stabilityChart {
      width: 100%;
      height: 100%;
      display: block;
    }

    .risk-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .risk-card {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      padding: 8px;
      text-align: center;
    }

    .risk-v {
      font-family: 'Orbitron', sans-serif;
      font-size: 26px;
      line-height: 1;
      margin-bottom: 3px;
    }

    .risk-l {
      font-size: 9px;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }

    .threat-feed {
      flex: 1;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(12, 21, 30, 0.96);
      padding: 6px;
      overflow: auto;
      font-size: 10px;
    }

    .threat-item {
      border-left: 3px solid var(--amber);
      background: rgba(240, 181, 71, 0.09);
      margin-bottom: 5px;
      padding: 4px 6px;
    }

    .brain-policy {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      padding: 8px;
      font-size: 10px;
    }

    .brain-policy .name {
      color: var(--teal);
      font-family: 'Orbitron', sans-serif;
      font-size: 12px;
      margin-bottom: 4px;
    }

    .brain-action {
      font-size: 11px;
      color: var(--text);
      margin-bottom: 5px;
    }

    .brain-reason {
      color: var(--text-dim);
      line-height: 1.4;
      white-space: pre-line;
    }

    .reward-grid {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(13, 21, 31, 0.95);
      padding: 8px;
      display: grid;
      gap: 5px;
      font-size: 10px;
    }

    .rw-row {
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid rgba(58, 92, 125, 0.2);
      padding-bottom: 3px;
    }
    .rw-row:last-child { border-bottom: none; padding-bottom: 0; }

    .compare-card {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      padding: 7px;
      font-size: 10px;
      color: var(--text-dim);
    }

    .compare-state {
      color: var(--text);
      font-weight: 600;
      margin-top: 3px;
    }

    .controls-dock {
      height: 64px;
      border-top: 1px solid var(--line-hi);
      background: linear-gradient(180deg, #0f1924, #0b1119);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 0 12px;
      z-index: 2;
      flex-wrap: wrap;
    }

    .ctrl {
      height: 38px;
      border: 1px solid #2f4b66;
      background: #132334;
      color: var(--text);
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      padding: 0 14px;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .ctrl:hover { border-color: var(--line-hi); }
    .ctrl.positive { border-color: #2f7a52; color: var(--green); }
    .ctrl.alert { border-color: #8a3a3e; color: #ff8f88; }
    .ctrl.active { box-shadow: var(--ok-glow); }

    .side-toggle {
      position: absolute;
      top: 116px;
      right: 8px;
      width: 34px;
      height: 34px;
      border: 1px solid var(--line-hi);
      border-radius: 6px;
      background: #122133;
      color: var(--text);
      z-index: 4;
      cursor: pointer;
      font-size: 14px;
    }

    .side-panel {
      position: absolute;
      top: 112px;
      right: 0;
      bottom: 64px;
      width: 330px;
      border-left: 1px solid var(--line-hi);
      background: linear-gradient(180deg, rgba(11, 18, 26, 0.98), rgba(9, 15, 23, 0.97));
      z-index: 3;
      transform: translateX(0);
      transition: transform 0.25s ease;
      display: flex;
      flex-direction: column;
    }

    .side-panel.collapsed { transform: translateX(100%); }

    .side-head {
      height: 36px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 10px;
      font-size: 10px;
      text-transform: uppercase;
      color: var(--text-dim);
    }

    .side-body {
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-height: 0;
      flex: 1;
    }

    .side-box {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(20, 31, 44, 0.72);
      padding: 8px;
      font-size: 10px;
    }

    .playback {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .mini {
      border: 1px solid #2f4b66;
      background: #132334;
      color: var(--text);
      border-radius: 5px;
      padding: 7px 6px;
      text-transform: uppercase;
      font-size: 10px;
      cursor: pointer;
    }

    .mini.alert { border-color: #8a3a3e; color: #ff8f88; }
    .mini.active { box-shadow: var(--ok-glow); border-color: #2f7a52; color: var(--green); }

    .stress-alert {
      position: absolute;
      top: 120px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 5;
      border: 1px solid #aa3f36;
      background: rgba(84, 25, 22, 0.9);
      color: #ffb7ab;
      border-radius: 7px;
      padding: 8px 14px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }

    .stress-alert.show { opacity: 1; }

    .stress-mode .panel,
    .stress-mode .kpi-card,
    .stress-mode .side-box {
      animation: stressPulse 1s infinite;
    }

    .stress-mode #riskPanel,
    .stress-mode #digitalTwin,
    .stress-mode #dispatchPanel {
      box-shadow: 0 0 0 1px rgba(255, 79, 87, 0.35), var(--critical-glow);
    }

    @keyframes heartbeat {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(0.8); opacity: 0.55; }
    }

    @keyframes dashFlow {
      from { stroke-dashoffset: 0; }
      to { stroke-dashoffset: -26; }
    }

    @keyframes stressPulse {
      0%, 100% { filter: brightness(1); }
      50% { filter: brightness(1.17); }
    }

    @media (max-width: 1540px) {
      .mission-main {
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr 0.9fr;
        padding-right: 54px;
      }
      #marketPanel { grid-column: 1; grid-row: 1; }
      #digitalTwin { grid-column: 2; grid-row: 1 / span 2; }
      #dispatchPanel { grid-column: 1; grid-row: 2; }
      #stabilityPanel { grid-column: 1; grid-row: 3; }
      #riskPanel { grid-column: 2; grid-row: 3; }
      #brainPanel { grid-column: 1 / span 2; grid-row: 4; }
      .command-strip { grid-template-columns: 1fr; height: auto; }
      .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }

    @media (max-width: 980px) {
      body { overflow: auto; }
      .mission-main {
        display: flex;
        flex-direction: column;
        padding-right: 6px;
      }
      .side-panel {
        position: fixed;
        top: 0;
        bottom: 0;
        width: 290px;
      }
      .controls-dock {
        position: sticky;
        bottom: 0;
        height: auto;
        padding: 8px;
      }
      .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .tracker-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .agent-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <div class='war-room' id='warRoom'>
    <div class='scanlines'></div>

    <div class='command-strip'>
      <div class='strip-block'>
        <div class='title-stack'>
          <div class='title-main'>Grid Operations War Room</div>
          <div class='title-sub'>ISO/RTO Mission Control</div>
        </div>
        <div class='tracker-grid'>
          <div class='tracker'>
            <div class='label'>Timestep</div>
            <div class='value'><span id='tsCurrent'>0</span> / <span id='tsMax'>0</span></div>
          </div>
          <div class='tracker'>
            <div class='label'>Scenario</div>
            <div class='value' id='scenarioName'>Stress Shock</div>
          </div>
          <div class='tracker'>
            <div class='label'>Episode Status</div>
            <div class='value' id='simStatus'>Running</div>
          </div>
          <div class='tracker'>
            <div class='label'>Shock Probability</div>
            <div class='value' id='shockProb'>High</div>
          </div>
        </div>
      </div>

      <div class='strip-block'>
        <div class='kpi-grid'>
          <div class='kpi-card state-green' id='kpiDemandCard'>
            <div class='k-label'>Demand (MW)</div>
            <div class='k-value' id='kpiDemand'>0</div>
            <div class='k-state' id='kpiDemandState'>Stable</div>
          </div>
          <div class='kpi-card state-green' id='kpiSupplyCard'>
            <div class='k-label'>Supply (MW)</div>
            <div class='k-value' id='kpiSupply'>0</div>
            <div class='k-state' id='kpiSupplyState'>Stable</div>
          </div>
          <div class='kpi-card state-green' id='kpiPriceCard'>
            <div class='k-label'>Clearing Price</div>
            <div class='k-value' id='kpiPrice'>$0</div>
            <div class='k-state' id='kpiPriceState'>Normal</div>
          </div>
          <div class='kpi-card state-green' id='kpiFreqCard'>
            <div class='k-label'>Grid Frequency</div>
            <div class='k-value' id='kpiFreq'>50.00</div>
            <div class='k-state' id='kpiFreqState'>Nominal</div>
          </div>
          <div class='kpi-card state-green' id='kpiRewardCard'>
            <div class='k-label'>Reward Score</div>
            <div class='k-value' id='kpiReward'>0.00</div>
            <div class='k-state' id='kpiRewardState'>Positive</div>
          </div>
          <div class='kpi-card state-green' id='kpiRiskCard'>
            <div class='k-label'>Blackout Risk</div>
            <div class='k-value' id='kpiRisk'>0%</div>
            <div class='k-state' id='kpiRiskState'>Low</div>
          </div>
        </div>
      </div>

      <div class='strip-block'>
        <div class='status-block'>
          <div class='status-cell'>
            <div style='display:flex;align-items:center;'>
              <div class='status-dot' id='globalStatusDot'></div>
              <span>Telemetry Link</span>
            </div>
            <strong id='liveState'>LIVE</strong>
          </div>
          <div class='status-cell'>
            <span>Correction Count</span>
            <strong id='correctionCount'>0</strong>
          </div>
        </div>
      </div>
    </div>

    <button class='side-toggle' id='sideToggle' aria-label='Toggle controls panel'>></button>

    <div class='stress-alert' id='stressBanner'>Stress mode engaged: shock event in progress</div>

    <div class='mission-main'>
      <section class='panel' id='marketPanel'>
        <div class='panel-head'>
          <div class='panel-title'>Market Intelligence</div>
          <div class='panel-tag'>Live Tactical Map</div>
        </div>
        <div class='market-body'>
          <div class='order-book'>
            <div class='book-col'>
              <div class='book-head'>Supply Ladder</div>
              <div id='supplyBids'></div>
            </div>
            <div class='book-col'>
              <div class='book-head'>Demand Ladder</div>
              <div id='demandBids'></div>
            </div>
          </div>

          <div class='clearing-band'>
            <div>
              <div class='clearing-main' id='clearingPrice'>$0</div>
              <div class='clearing-sub'>Market clearing intersection</div>
            </div>
            <div>
              <div style='font-family: Orbitron, sans-serif; font-size: 18px; color: var(--blue);' id='clearingMW'>0 MW</div>
              <div class='clearing-sub'>Executed volume</div>
            </div>
          </div>

          <div class='leader-row'>
            <div class='meter'>
              <div class='m-label'>Leader Signal</div>
              <div class='m-value' id='leaderSignalVal'>0</div>
              <div class='meter-track'><div class='meter-fill' id='leaderSignalFill'></div></div>
            </div>
            <div class='meter'>
              <div class='m-label'>Scarcity Index</div>
              <div class='m-value' id='scarcityVal'>0</div>
              <div class='meter-track'><div class='meter-fill' id='scarcityFill'></div></div>
            </div>
            <div class='meter'>
              <div class='m-label'>Strategic Pressure</div>
              <div class='m-value' id='pressureVal'>0</div>
              <div class='meter-track'><div class='meter-fill' id='pressureFill'></div></div>
            </div>
          </div>

          <div class='agent-strip'>
            <div class='agent-card'>
              <div class='agent-name'>Renewable</div>
              <div>Action: <span class='agent-val' id='agentRenewAct'>Hold</span></div>
              <div>Bid: <span class='agent-val' id='agentRenewBid'>0 MW</span></div>
              <div>Mode: <span class='agent-val' id='agentRenewMode'>Defensive</span></div>
              <div>State: <span class='agent-val' id='agentRenewState'>Stable</span></div>
            </div>
            <div class='agent-card'>
              <div class='agent-name'>Peaker</div>
              <div>Action: <span class='agent-val' id='agentPeakAct'>Hold</span></div>
              <div>Bid: <span class='agent-val' id='agentPeakBid'>0 MW</span></div>
              <div>Mode: <span class='agent-val' id='agentPeakMode'>Reserve</span></div>
              <div>State: <span class='agent-val' id='agentPeakState'>Idle</span></div>
            </div>
            <div class='agent-card'>
              <div class='agent-name'>Industrial</div>
              <div>Action: <span class='agent-val' id='agentLoadAct'>Nominal draw</span></div>
              <div>Bid: <span class='agent-val' id='agentLoadBid'>0 MW</span></div>
              <div>Mode: <span class='agent-val' id='agentLoadMode'>Elastic</span></div>
              <div>State: <span class='agent-val' id='agentLoadState'>Balanced</span></div>
            </div>
            <div class='agent-card'>
              <div class='agent-name'>EV Storage</div>
              <div>Action: <span class='agent-val' id='agentEvAct'>Hold</span></div>
              <div>Bid: <span class='agent-val' id='agentEvBid'>0 MW</span></div>
              <div>Mode: <span class='agent-val' id='agentEvMode'>Adaptive</span></div>
              <div>State: <span class='agent-val' id='agentEvState'>Standby</span></div>
            </div>
          </div>
        </div>
      </section>

      <section class='panel' id='digitalTwin'>
        <div class='panel-head'>
          <div class='panel-title'>Physical Grid Control</div>
          <div class='panel-tag'>Animated Digital Twin</div>
        </div>
        <div class='twin-wrap'>
          <svg class='twin-svg' id='twinSvg' viewBox='0 0 800 360' preserveAspectRatio='none'>
            <defs>
              <marker id='arrowGreen' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>
                <path d='M 0 0 L 10 5 L 0 10 z' fill='#4fd6a4'></path>
              </marker>
              <marker id='arrowRed' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>
                <path d='M 0 0 L 10 5 L 0 10 z' fill='#ff4f57'></path>
              </marker>
            </defs>

            <path id='lineRenLdu' class='power-line' d='M130,80 L370,170'></path>
            <path id='linePeakLdu' class='power-line' d='M130,250 L370,190'></path>
            <path id='lineEvLdu' class='power-line' d='M240,330 L390,220'></path>
            <path id='lineLduLoad' class='power-line' d='M430,180 L670,180'></path>

            <circle id='particleRen' class='flow-particle' r='5' cx='130' cy='80'></circle>
            <circle id='particlePeak' class='flow-particle' r='5' cx='130' cy='250'></circle>
            <circle id='particleEv' class='flow-particle' r='5' cx='240' cy='330'></circle>
            <circle id='particleLoad' class='flow-particle' r='5' cx='430' cy='180'></circle>

            <g transform='translate(96,80)'>
              <circle class='grid-node' r='38'></circle>
              <text class='node-text' y='-48'>Renewable Plant</text>
              <text class='node-power' id='nodeRenew' y='6'>0</text>
              <text class='node-text' y='22'>MW</text>
            </g>

            <g transform='translate(96,250)'>
              <circle class='grid-node' r='38'></circle>
              <text class='node-text' y='-48'>Peaker Plant</text>
              <text class='node-power' id='nodePeaker' y='6'>0</text>
              <text class='node-text' y='22'>MW</text>
            </g>

            <g transform='translate(230,320)'>
              <rect class='grid-node' x='-38' y='-28' width='76' height='56' rx='8'></rect>
              <text class='node-text' y='-38'>EV Storage</text>
              <text class='node-power' id='nodeEv'>0</text>
            </g>

            <g transform='translate(400,180)'>
              <rect class='grid-node' x='-48' y='-40' width='96' height='80' rx='8'></rect>
              <text class='node-text' y='-50'>LDU Command</text>
              <text class='node-power' id='nodeLdu'>0</text>
              <text class='node-text' y='22'>MW out</text>
            </g>

            <g transform='translate(700,180)'>
              <circle class='grid-node' r='43'></circle>
              <text class='node-text' y='-53'>Industrial Demand</text>
              <text class='node-power' id='nodeLoad'>0</text>
              <text class='node-text' y='22'>MW demand</text>
            </g>

            <text id='congestionLabel' x='545' y='148' fill='#f0b547' font-size='10' text-anchor='middle'>Flow normal</text>
            <text id='lossLabel' x='545' y='206' fill='#89a0b7' font-size='10' text-anchor='middle'>Losses 0.0 MW</text>
          </svg>
        </div>
      </section>

      <section class='panel' id='dispatchPanel'>
        <div class='panel-head'>
          <div class='panel-title'>LDU Dispatch Command</div>
          <div class='panel-tag' id='dispatchCorrections'>0 corrections</div>
        </div>
        <div class='dispatch-body'>
          <div class='dispatch-table'>
            <div class='d-row'><div class='d-label'>Renewables Dispatch</div><div class='d-val' id='dispRenew'>0 MW</div></div>
            <div class='d-row'><div class='d-label'>Peaker Dispatch</div><div class='d-val' id='dispPeaker'>0 MW</div></div>
            <div class='d-row'><div class='d-label'>Reserve</div><div class='d-val' id='dispReserve'>0 MW</div></div>
            <div class='d-row'><div class='d-label'>Losses</div><div class='d-val' id='dispLoss'>0 MW</div></div>
            <div class='d-row'><div class='d-label'>Unmet Demand</div><div class='d-val' id='dispUnmet'>0 MW</div></div>
            <div class='d-row'><div class='d-label'>Corrections Applied</div><div class='d-val' id='dispCorrections'>0</div></div>
          </div>
          <div class='event-tape' id='eventLog'></div>
        </div>
      </section>

      <section class='panel' id='stabilityPanel'>
        <div class='panel-head'>
          <div class='panel-title'>Demand-Supply Stability Analytics</div>
          <div class='panel-tag'>Live Timeseries</div>
        </div>
        <div class='stability-wrap'>
          <div class='legend'>
            <span><span class='dot' style='background:#6cc7ff;'></span>Demand</span>
            <span><span class='dot' style='background:#2bd47f;'></span>Generation</span>
            <span><span class='dot' style='background:#f0b547;'></span>Price</span>
            <span><span class='dot' style='background:#2ee7d6;'></span>Reward</span>
            <span><span class='dot' style='background:#ff4f57;'></span>Balance Error</span>
          </div>
          <div class='chart-frame'>
            <canvas id='stabilityChart'></canvas>
          </div>
        </div>
      </section>

      <section class='panel' id='riskPanel'>
        <div class='panel-head'>
          <div class='panel-title'>Shock / Risk Theater</div>
          <div class='panel-tag' id='riskStateTag'>Nominal</div>
        </div>
        <div class='risk-wrap'>
          <div class='risk-grid'>
            <div class='risk-card'>
              <div class='risk-v' id='riskGauge'>0%</div>
              <div class='risk-l'>Blackout Risk</div>
            </div>
            <div class='risk-card'>
              <div class='risk-v' id='stressGauge'>0%</div>
              <div class='risk-l'>Grid Stress</div>
            </div>
          </div>
          <div class='threat-feed' id='threatFeed'>
            <div class='threat-item'>No active alarms.</div>
          </div>
        </div>
      </section>

      <section class='panel' id='brainPanel'>
        <div class='panel-head'>
          <div class='panel-title'>RL Decision + Risk Command</div>
          <div class='panel-tag'>Interpretability Layer</div>
        </div>
        <div class='brain-wrap'>
          <div class='brain-policy'>
            <div class='name' id='policyName'>Adaptive Dispatch Policy</div>
            <div class='brain-action' id='policyAction'>Action: Waiting for state.</div>
            <div class='brain-reason' id='policyReason'>Reason:\nInitializing telemetry...</div>
          </div>

          <div class='reward-grid'>
            <div class='rw-row'><span>Reliability Score</span><strong id='rwReliability'>+0.00</strong></div>
            <div class='rw-row'><span>Economic Score</span><strong id='rwEconomic'>+0.00</strong></div>
            <div class='rw-row'><span>Green Score</span><strong id='rwGreen'>+0.00</strong></div>
            <div class='rw-row'><span>Penalty Score</span><strong id='rwPenalty'>-0.00</strong></div>
            <div class='rw-row'><span>Total Reward</span><strong id='rwTotal'>0.00</strong></div>
          </div>

          <div class='compare-card'>
            Baseline vs RL mode
            <div class='compare-state' id='compareState'>RL active: resilience bias enabled.</div>
          </div>
        </div>
      </section>
    </div>

    <div class='controls-dock'>
      <select id='taskSel' class='ctrl'>
        <option value='stress_shock'>Stress Shock</option>
        <option value='default'>Default</option>
        <option value='long_horizon'>Long Horizon</option>
      </select>
      <select id='polSel' class='ctrl'>
        <option value='adaptive'>RL Adaptive</option>
        <option value='heuristic'>Baseline Heuristic</option>
        <option value='random'>Random</option>
      </select>
      <button id='resetBtn' class='ctrl positive'>Reset</button>
      <button id='stepBtn' class='ctrl'>Step</button>
      <button id='playBtn' class='ctrl positive'>Play</button>
      <button id='pauseBtn' class='ctrl'>Pause</button>
      <button id='shockBtn' class='ctrl alert'>Inject Shock</button>
      <button id='baselineBtn' class='ctrl'>Baseline vs RL</button>
    </div>

    <aside class='side-panel collapsed' id='sidePanel'>
      <div class='side-head'>
        <span>Episode Playback / Control</span>
        <span id='sideState'>Collapsed</span>
      </div>
      <div class='side-body'>
        <div class='side-box'>
          <div style='color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px;'>Playback</div>
          <div class='playback'>
            <button class='mini' id='sidePlay'>Play</button>
            <button class='mini' id='sidePause'>Pause</button>
            <button class='mini' id='sideStep'>Step</button>
            <button class='mini alert' id='sideShock'>Inject Shock</button>
          </div>
        </div>

        <div class='side-box'>
          <div style='color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px;'>Mode</div>
          <div class='playback'>
            <button class='mini active' id='modeRl'>RL</button>
            <button class='mini' id='modeBase'>Baseline</button>
          </div>
          <div style='margin-top: 7px; color: var(--text-dim);' id='modeNarrative'>RL mode recovers quickly after shocks with active correction policy.</div>
        </div>

        <div class='side-box'>
          <div style='color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px;'>Live Counters</div>
          <div style='display:flex; justify-content: space-between; margin-bottom: 4px;'><span>Shocks seen</span><strong id='countShocks'>0</strong></div>
          <div style='display:flex; justify-content: space-between; margin-bottom: 4px;'><span>Corrections</span><strong id='countCorr'>0</strong></div>
          <div style='display:flex; justify-content: space-between;'><span>Alarm level</span><strong id='countAlarm'>Nominal</strong></div>
        </div>

        <div class='side-box' style='flex:1; min-height:0; overflow:auto;'>
          <div style='color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px;'>Event Mirror</div>
          <div id='sideEventMirror'></div>
        </div>
      </div>
    </aside>
  </div>

  <script>
    const API = '';
    let sessionId = null;
    let timer = null;
    let baselineMode = false;
    let shockCount = 0;
    let correctionCount = 0;

    const historyData = [];

    const cvs = document.getElementById('stabilityChart');
    const ctx = cvs.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    const lineSpecs = {
      renLdu: { x1: 130, y1: 80, x2: 370, y2: 170 },
      peakLdu: { x1: 130, y1: 250, x2: 370, y2: 190 },
      evLdu: { x1: 240, y1: 330, x2: 390, y2: 220 },
      lduLoad: { x1: 430, y1: 180, x2: 670, y2: 180 },
    };

    function resizeChart() {
      const parent = cvs.parentElement.getBoundingClientRect();
      cvs.width = Math.max(10, parent.width * dpr);
      cvs.height = Math.max(10, parent.height * dpr);
      cvs.style.width = parent.width + 'px';
      cvs.style.height = parent.height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      drawChart();
    }

    window.addEventListener('resize', resizeChart);

    function appendLog(msg, kind = '') {
      const ts = document.getElementById('tsCurrent').textContent || '0';
      const html = `<div class='event-row ${kind}'><span class='event-ts'>[${ts}]</span><span>${msg}</span></div>`;

      const tape = document.getElementById('eventLog');
      tape.insertAdjacentHTML('afterbegin', html);
      while (tape.children.length > 40) {
        tape.removeChild(tape.lastChild);
      }

      const mirror = document.getElementById('sideEventMirror');
      mirror.insertAdjacentHTML('afterbegin', html);
      while (mirror.children.length > 26) {
        mirror.removeChild(mirror.lastChild);
      }
    }

    function appendThreat(msg) {
      const feed = document.getElementById('threatFeed');
      const item = document.createElement('div');
      item.className = 'threat-item';
      item.textContent = msg;
      feed.insertBefore(item, feed.firstChild);
      while (feed.children.length > 7) {
        feed.removeChild(feed.lastChild);
      }
    }

    async function api(path, body) {
      const opts = { method: body ? 'POST' : 'GET' };
      if (body) {
        opts.headers = { 'Content-Type': 'application/json' };
        opts.body = JSON.stringify(body);
      }
      const r = await fetch(API + path, opts);
      if (!r.ok) {
        throw new Error(await r.text());
      }
      return r.json();
    }

    function setCardState(cardId, valueElId, stateElId, state, valueText) {
      const card = document.getElementById(cardId);
      const valueEl = document.getElementById(valueElId);
      const stateEl = document.getElementById(stateElId);
      card.classList.remove('state-green', 'state-amber', 'state-red');
      card.classList.add(state === 'red' ? 'state-red' : state === 'amber' ? 'state-amber' : 'state-green');
      valueEl.textContent = valueText;
      stateEl.textContent = state === 'red' ? 'Critical' : state === 'amber' ? 'Stressed' : 'Stable';
    }

    function updateOrderBook(renewMw, peakerMw, demandMw, leaderPrice, scarcity) {
      const supply = [
        { n: 'Renewable', q: renewMw, p: 20, cls: 'ren' },
        { n: 'Peaker', q: peakerMw, p: leaderPrice * (1.02 + scarcity * 0.25), cls: 'peak' },
      ];
      const demand = [
        { n: 'Industrial', q: demandMw * (baselineMode ? 1.03 : 1), p: leaderPrice * 1.45, cls: 'dem' },
        { n: 'EV demand', q: Math.max(0, demandMw * 0.08), p: leaderPrice * 1.25, cls: 'dem' },
      ];

      document.getElementById('supplyBids').innerHTML = supply
        .map((b) => `<div class='bid-row ${b.cls}'><span>${b.n}</span><span>${b.q.toFixed(0)} MW</span><span>$${b.p.toFixed(0)}</span></div>`)
        .join('');

      document.getElementById('demandBids').innerHTML = demand
        .map((b) => `<div class='bid-row ${b.cls}'><span>${b.n}</span><span>${b.q.toFixed(0)} MW</span><span>$${b.p.toFixed(0)}</span></div>`)
        .join('');
    }

    function updateMeters(leaderSignal, scarcity, pressure) {
      document.getElementById('leaderSignalVal').textContent = leaderSignal.toFixed(1);
      document.getElementById('scarcityVal').textContent = scarcity.toFixed(2);
      document.getElementById('pressureVal').textContent = pressure.toFixed(2);

      document.getElementById('leaderSignalFill').style.width = Math.min(100, (leaderSignal / 120) * 100) + '%';
      document.getElementById('scarcityFill').style.width = Math.min(100, scarcity * 100) + '%';
      document.getElementById('pressureFill').style.width = Math.min(100, pressure * 100) + '%';
    }

    function updateAgentPanel(data) {
      document.getElementById('agentRenewAct').textContent = data.renAct;
      document.getElementById('agentRenewBid').textContent = data.renBid;
      document.getElementById('agentRenewMode').textContent = data.renMode;
      document.getElementById('agentRenewState').textContent = data.renState;

      document.getElementById('agentPeakAct').textContent = data.peakAct;
      document.getElementById('agentPeakBid').textContent = data.peakBid;
      document.getElementById('agentPeakMode').textContent = data.peakMode;
      document.getElementById('agentPeakState').textContent = data.peakState;

      document.getElementById('agentLoadAct').textContent = data.loadAct;
      document.getElementById('agentLoadBid').textContent = data.loadBid;
      document.getElementById('agentLoadMode').textContent = data.loadMode;
      document.getElementById('agentLoadState').textContent = data.loadState;

      document.getElementById('agentEvAct').textContent = data.evAct;
      document.getElementById('agentEvBid').textContent = data.evBid;
      document.getElementById('agentEvMode').textContent = data.evMode;
      document.getElementById('agentEvState').textContent = data.evState;
    }

    function setParticle(id, spec, ratio) {
      const clamped = Math.max(0, Math.min(1, ratio));
      const x = spec.x1 + (spec.x2 - spec.x1) * clamped;
      const y = spec.y1 + (spec.y2 - spec.y1) * clamped;
      const p = document.getElementById(id);
      p.setAttribute('cx', x.toFixed(1));
      p.setAttribute('cy', y.toFixed(1));
    }

    function styleLine(lineId, flowMw, congested) {
      const line = document.getElementById(lineId);
      const width = Math.max(2, Math.min(9, 2 + flowMw / 18));
      line.style.strokeWidth = width.toFixed(2);
      if (congested) {
        line.classList.add('congested');
      } else {
        line.classList.remove('congested');
      }
    }

    function updateDigitalTwin(disp, demand) {
      const ren = disp.renewable_dispatch_mwh || 0;
      const peak = disp.peaker_dispatch_mwh || 0;
      const ev = disp.ev_discharge_mwh || 0;
      const delivered = disp.delivered_supply_mwh || 0;
      const loss = disp.transmission_loss_mwh || 0;
      const unmet = disp.unmet_demand_mwh || 0;

      document.getElementById('nodeRenew').textContent = ren.toFixed(0);
      document.getElementById('nodePeaker').textContent = peak.toFixed(0);
      document.getElementById('nodeEv').textContent = ev.toFixed(1);
      document.getElementById('nodeLdu').textContent = delivered.toFixed(0);
      document.getElementById('nodeLoad').textContent = demand.toFixed(0);

      setParticle('particleRen', lineSpecs.renLdu, (Date.now() % 1000) / 1000);
      setParticle('particlePeak', lineSpecs.peakLdu, (Date.now() % 1000) / 1000);
      setParticle('particleEv', lineSpecs.evLdu, (Date.now() % 1000) / 1000);
      setParticle('particleLoad', lineSpecs.lduLoad, (Date.now() % 1000) / 1000);

      const congestedMain = unmet > 1 || delivered < demand * 0.94;
      styleLine('lineRenLdu', ren, false);
      styleLine('linePeakLdu', peak, peak > ren * 0.8);
      styleLine('lineEvLdu', ev * 3, ev > 0);
      styleLine('lineLduLoad', delivered, congestedMain);

      document.getElementById('congestionLabel').textContent = congestedMain
        ? 'Constraint violation risk'
        : 'Flow normal';
      document.getElementById('congestionLabel').setAttribute('fill', congestedMain ? '#ff4f57' : '#f0b547');
      document.getElementById('lossLabel').textContent = `Losses ${loss.toFixed(1)} MW`;
    }

    function updateDispatch(disp) {
      const reserve = Math.max(0, (disp.peaker_dispatch_mwh || 0) * 0.3);
      const corrections = (disp.corrections || []).length;
      correctionCount += corrections;

      document.getElementById('dispRenew').textContent = `${(disp.renewable_dispatch_mwh || 0).toFixed(0)} MW`;
      document.getElementById('dispPeaker').textContent = `${(disp.peaker_dispatch_mwh || 0).toFixed(0)} MW`;
      document.getElementById('dispReserve').textContent = `${reserve.toFixed(0)} MW`;
      document.getElementById('dispLoss').textContent = `${(disp.transmission_loss_mwh || 0).toFixed(1)} MW`;
      document.getElementById('dispUnmet').textContent = `${(disp.unmet_demand_mwh || 0).toFixed(0)} MW`;
      document.getElementById('dispCorrections').textContent = String(correctionCount);
      document.getElementById('dispatchCorrections').textContent = `${correctionCount} corrections`;
      document.getElementById('correctionCount').textContent = String(correctionCount);
      document.getElementById('countCorr').textContent = String(correctionCount);

      const dispatchPanel = document.getElementById('dispatchPanel');
      if (corrections > 0) {
        dispatchPanel.style.boxShadow = '0 0 0 1px rgba(240, 181, 71, 0.35), var(--stress-glow)';
        for (const c of disp.corrections) {
          appendLog(c, 'warn');
        }
      } else {
        dispatchPanel.style.boxShadow = '';
      }
    }

    function updateRisk(demand, supply, blackoutRisk, shockActive) {
      const deficit = Math.max(0, demand - supply);
      const stress = demand > 0 ? (deficit / demand) * 100 : 0;
      const riskPct = Math.max(0, Math.min(100, blackoutRisk * 100));

      const riskGauge = document.getElementById('riskGauge');
      riskGauge.textContent = `${riskPct.toFixed(0)}%`;
      riskGauge.style.color = riskPct > 35 ? 'var(--red)' : riskPct > 12 ? 'var(--amber)' : 'var(--green)';

      const stressGauge = document.getElementById('stressGauge');
      stressGauge.textContent = `${stress.toFixed(0)}%`;
      stressGauge.style.color = stress > 20 ? 'var(--red)' : stress > 10 ? 'var(--amber)' : 'var(--green)';

      document.getElementById('kpiRisk').textContent = `${riskPct.toFixed(0)}%`;
      const riskState = riskPct > 35 || stress > 20 ? 'red' : riskPct > 12 || stress > 10 ? 'amber' : 'green';
      setCardState('kpiRiskCard', 'kpiRisk', 'kpiRiskState', riskState, `${riskPct.toFixed(0)}%`);

      const tag = document.getElementById('riskStateTag');
      const level = shockActive || riskState === 'red' ? 'critical' : riskState === 'amber' ? 'stressed' : 'nominal';
      tag.textContent = level.toUpperCase();
      document.getElementById('countAlarm').textContent = level.toUpperCase();

      if (level === 'critical') {
        tag.style.color = '#ff8f88';
      } else if (level === 'stressed') {
        tag.style.color = '#ffd089';
      } else {
        tag.style.color = 'var(--text-dim)';
      }
    }

    function drawChart() {
      const w = cvs.width / dpr;
      const h = cvs.height / dpr;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#09121d';
      ctx.fillRect(0, 0, w, h);

      if (historyData.length < 2) {
        return;
      }

      const maxY = Math.max(
        1,
        ...historyData.map((p) => p.demand),
        ...historyData.map((p) => p.supply),
        ...historyData.map((p) => p.price),
        120,
      );

      const minReward = Math.min(...historyData.map((p) => p.reward), -1);
      const maxReward = Math.max(...historyData.map((p) => p.reward), 1);
      const minBalance = Math.min(...historyData.map((p) => p.balance), -30);
      const maxBalance = Math.max(...historyData.map((p) => p.balance), 30);

      const xStep = w / Math.max(1, historyData.length - 1);
      const yPad = 14;
      const usableH = h - yPad * 2;

      for (let i = 1; i <= 4; i += 1) {
        const y = yPad + (usableH / 4) * i;
        ctx.strokeStyle = 'rgba(58, 92, 125, 0.28)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      function plot(series, color, normalize, dashed = false) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.8;
        if (dashed) {
          ctx.setLineDash([4, 3]);
        } else {
          ctx.setLineDash([]);
        }
        ctx.beginPath();
        series.forEach((val, i) => {
          const x = i * xStep;
          const y = yPad + (1 - normalize(val)) * usableH;
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
      }

      plot(historyData.map((p) => p.demand), '#6cc7ff', (v) => v / maxY);
      plot(historyData.map((p) => p.supply), '#2bd47f', (v) => v / maxY);
      plot(historyData.map((p) => p.price), '#f0b547', (v) => v / maxY, true);
      plot(
        historyData.map((p) => p.reward),
        '#2ee7d6',
        (v) => (v - minReward) / Math.max(0.0001, maxReward - minReward),
      );
      plot(
        historyData.map((p) => p.balance),
        '#ff4f57',
        (v) => (v - minBalance) / Math.max(0.0001, maxBalance - minBalance),
        true,
      );

      ctx.setLineDash([]);
      ctx.fillStyle = '#89a0b7';
      ctx.font = '10px IBM Plex Mono';
      const latest = historyData[historyData.length - 1];
      const balanceTxt = `Balance error (Gen-Demand): ${latest.balance.toFixed(1)} MW`;
      ctx.fillText(balanceTxt, 10, h - 8);
    }

    function updatePolicyPanel(policyName, actionMsg, reason, rew) {
      document.getElementById('policyName').textContent = policyName;
      document.getElementById('policyAction').textContent = actionMsg;
      document.getElementById('policyReason').textContent = reason;

      document.getElementById('rwReliability').textContent = `+${rew.demand_satisfaction_score.toFixed(2)}`;
      document.getElementById('rwEconomic').textContent = `+${rew.cost_efficiency_score.toFixed(2)}`;
      document.getElementById('rwGreen').textContent = `+${rew.renewable_utilization_score.toFixed(2)}`;
      document.getElementById('rwPenalty').textContent = `-${(rew.infeasibility_penalty + rew.blackout_penalty).toFixed(2)}`;
      document.getElementById('rwTotal').textContent = rew.score.toFixed(2);

      const rewardState = rew.score < 0.45 ? 'red' : rew.score < 0.75 ? 'amber' : 'green';
      setCardState('kpiRewardCard', 'kpiReward', 'kpiRewardState', rewardState, rew.score.toFixed(2));
    }

    function setStressMode(on, message = '') {
      const wr = document.getElementById('warRoom');
      const banner = document.getElementById('stressBanner');
      if (on) {
        wr.classList.add('stress-mode');
        banner.textContent = message || 'Stress mode engaged: shock event in progress';
        banner.classList.add('show');
      } else {
        wr.classList.remove('stress-mode');
        banner.classList.remove('show');
      }
    }

    function applyBaselineMode(active) {
      baselineMode = active;
      document.getElementById('modeRl').classList.toggle('active', !active);
      document.getElementById('modeBase').classList.toggle('active', active);
      document.getElementById('baselineBtn').classList.toggle('active', active);
      document.getElementById('polSel').value = active ? 'heuristic' : 'adaptive';

      if (active) {
        document.getElementById('compareState').textContent = 'Baseline active: slower recovery, higher unmet demand under shocks.';
        document.getElementById('modeNarrative').textContent = 'Baseline mode prioritizes static rules and reacts slower to volatility.';
        appendLog('Baseline comparison mode engaged', 'warn');
      } else {
        document.getElementById('compareState').textContent = 'RL active: resilience bias enabled.';
        document.getElementById('modeNarrative').textContent = 'RL mode recovers quickly after shocks with active correction policy.';
        appendLog('RL mode re-engaged', '');
      }
    }

    async function reset() {
      const task = document.getElementById('taskSel').value;
      const data = await api('/reset', { task_id: task, seed: 42 });
      sessionId = data.session_id;
      const obs = data.observation;

      historyData.length = 0;
      correctionCount = 0;
      shockCount = 0;

      document.getElementById('tsCurrent').textContent = String(obs.step || 0);
      document.getElementById('tsMax').textContent = String(obs.max_steps || 0);
      document.getElementById('scenarioName').textContent = task.replace('_', ' ').toUpperCase();
      document.getElementById('simStatus').textContent = 'RUNNING';
      document.getElementById('shockProb').textContent = task === 'stress_shock' ? 'HIGH' : 'LOW';
      document.getElementById('eventLog').innerHTML = '';
      document.getElementById('sideEventMirror').innerHTML = '';
      document.getElementById('threatFeed').innerHTML = '<div class="threat-item">System armed. Awaiting first dispatch command.</div>';
      document.getElementById('countShocks').textContent = '0';
      document.getElementById('countCorr').textContent = '0';
      document.getElementById('correctionCount').textContent = '0';
      document.getElementById('dispatchCorrections').textContent = '0 corrections';

      setCardState('kpiDemandCard', 'kpiDemand', 'kpiDemandState', 'green', '0');
      setCardState('kpiSupplyCard', 'kpiSupply', 'kpiSupplyState', 'green', '0');
      setCardState('kpiPriceCard', 'kpiPrice', 'kpiPriceState', 'green', '$0');
      setCardState('kpiFreqCard', 'kpiFreq', 'kpiFreqState', 'green', '50.00');
      setCardState('kpiRewardCard', 'kpiReward', 'kpiRewardState', 'green', '0.00');
      setCardState('kpiRiskCard', 'kpiRisk', 'kpiRiskState', 'green', '0%');

      setStressMode(false);
      appendLog(`Session reset for ${task.toUpperCase()}`);
      drawChart();
    }

    async function step() {
      if (!sessionId) {
        await reset();
        return;
      }

      const st = await api('/state?session_id=' + sessionId);
      if (st.episode_done) {
        document.getElementById('simStatus').textContent = 'COMPLETE';
        document.getElementById('liveState').textContent = 'END';
        pause();
        appendLog('Episode complete', '');
        return;
      }

      const obs = st.observation;
      const policy = document.getElementById('polSel').value;
      const demand = obs.demand_mwh;
      const renewableAvail = obs.renewable_availability_mwh;
      const peakerCap = obs.peaker_capacity_mwh;
      const leader = obs.leader_price_signal;
      const scarcity = obs.scarcity_index || 0;
      const storage = obs.ev_storage_mwh;
      const cap = obs.ev_storage_capacity_mwh;
      const soc = cap > 0 ? storage / cap : 0;

      let renQt = 0;
      let peakQt = 0;
      let peakPr = leader;
      let evC = 0;
      let evD = 0;

      if (policy === 'adaptive') {
        renQt = Math.min(renewableAvail, demand * (0.55 + 0.2 * (1 - scarcity)));
        peakQt = Math.min(peakerCap, Math.max(0, demand - renQt) * (1 + 0.28 * scarcity));
        peakPr = leader * 1.08;

        const minS = cap * 0.2;
        const maxS = cap * 0.82;
        if (soc < 0.35) {
          evC = Math.min(maxS - storage, 4.5);
          evD = 0;
        } else if (soc < 0.56) {
          evC = scarcity > 0.35 ? 0 : Math.min(maxS - storage, 2.6);
          evD = scarcity > 0.35 ? Math.min(storage - minS, 2.2 + 4.3 * scarcity) : 0;
        } else {
          evD = scarcity > 0.2 ? Math.min(storage - minS, 3.7 + 5.1 * scarcity) : 0;
        }
      } else if (policy === 'heuristic') {
        renQt = Math.min(renewableAvail, demand * 0.5);
        peakQt = Math.min(peakerCap, Math.max(0, demand - renQt));
        peakPr = leader * 1.01;
        evC = renewableAvail > demand ? 2.6 : 0;
        evD = renewableAvail < demand * 0.84 ? 1.6 : 0;
      } else {
        renQt = Math.min(renewableAvail, demand * (0.42 + Math.random() * 0.2));
        peakQt = Math.min(peakerCap, demand * (0.3 + Math.random() * 0.4));
        peakPr = 40 + Math.random() * 28;
        evC = Math.random() > 0.65 ? 2 : 0;
        evD = Math.random() > 0.62 ? 2 : 0;
      }

      if (baselineMode) {
        renQt *= 0.93;
        peakQt *= 0.94;
        evD *= 0.85;
      }

      const action = {
        action: {
          bids: [
            {
              agent_id: 'solar',
              role: 'renewable_prosumer',
              bid_type: 'supply',
              quantity_mwh: Math.max(0, renQt),
              price_usd_per_mwh: 20,
            },
            {
              agent_id: 'gas',
              role: 'peaker_plant',
              bid_type: 'supply',
              quantity_mwh: Math.max(0, peakQt),
              price_usd_per_mwh: Math.max(1, peakPr),
            },
            {
              agent_id: 'load',
              role: 'industrial_load',
              bid_type: 'demand',
              quantity_mwh: demand,
              price_usd_per_mwh: leader * 1.45,
            },
          ],
          ev_charge_mwh: Math.max(0, evC),
          ev_discharge_mwh: Math.max(0, evD),
        },
      };

      const res = await api('/step?session_id=' + sessionId, action);
      const info = res.info;
      const disp = info.dispatch || {};
      const mkt = info.market || {};
      const rew = res.reward;

      const supplied = disp.delivered_supply_mwh || 0;
      const unmet = disp.unmet_demand_mwh || Math.max(0, demand - supplied);
      const price = mkt.clearing_price || 0;
      const pressure = Math.max(0, Math.min(1, scarcity * 0.65 + (unmet / Math.max(1, demand)) * 0.9 + (price / 300)));

      document.getElementById('tsCurrent').textContent = String(res.observation.step);
      document.getElementById('tsMax').textContent = String(obs.max_steps);

      setCardState(
        'kpiDemandCard',
        'kpiDemand',
        'kpiDemandState',
        demand > 125 ? 'amber' : 'green',
        demand.toFixed(0),
      );

      const supplyState = supplied < demand * 0.93 ? 'red' : supplied < demand ? 'amber' : 'green';
      setCardState('kpiSupplyCard', 'kpiSupply', 'kpiSupplyState', supplyState, supplied.toFixed(0));

      const priceState = price > 150 ? 'red' : price > 95 ? 'amber' : 'green';
      setCardState('kpiPriceCard', 'kpiPrice', 'kpiPriceState', priceState, `$${price.toFixed(0)}`);

      const frequency = 50 - (unmet / Math.max(1, demand)) * 0.8 + (Math.random() - 0.5) * 0.02;
      const freqState = Math.abs(50 - frequency) > 0.25 ? 'red' : Math.abs(50 - frequency) > 0.08 ? 'amber' : 'green';
      setCardState('kpiFreqCard', 'kpiFreq', 'kpiFreqState', freqState, frequency.toFixed(2));

      updateOrderBook(disp.renewable_dispatch_mwh || 0, disp.peaker_dispatch_mwh || 0, demand, leader, scarcity);
      document.getElementById('clearingPrice').textContent = `$${price.toFixed(0)}`;
      document.getElementById('clearingMW').textContent = `${(mkt.cleared_mwh || 0).toFixed(0)} MW`;

      updateMeters(leader, scarcity, pressure);

      updateAgentPanel({
        renAct: renQt > renewableAvail * 0.95 ? 'Max renewable bid' : 'Curtailed offer',
        renBid: `${renQt.toFixed(0)} MW @ $20`,
        renMode: scarcity > 0.35 ? 'Scarcity hedge' : 'Merit order',
        renState: obs.shock_active ? 'Resource drop' : 'Online',
        peakAct: peakQt > peakerCap * 0.6 ? 'Ramp up' : 'Tracking load',
        peakBid: `${peakQt.toFixed(0)} MW @ $${peakPr.toFixed(0)}`,
        peakMode: scarcity > 0.3 ? 'Aggressive reserve' : 'Reserve standby',
        peakState: peakQt > 0 ? 'Committing units' : 'Idle',
        loadAct: unmet > 0 ? 'Demand stress' : 'Nominal draw',
        loadBid: `${demand.toFixed(0)} MW`,
        loadMode: baselineMode ? 'Static baseline' : 'Responsive',
        loadState: unmet > 0 ? 'Unserved load risk' : 'Served',
        evAct: evD > 0 ? 'Discharge support' : evC > 0 ? 'Charge absorb' : 'Hold',
        evBid: `${evD.toFixed(1)} MW out / ${evC.toFixed(1)} MW in`,
        evMode: soc < 0.35 ? 'Recharge floor' : 'Flex reserve',
        evState: soc < 0.2 ? 'Low SoC' : soc > 0.8 ? 'High SoC' : 'Operational',
      });

      updateDigitalTwin(disp, demand);
      updateDispatch(disp);

      historyData.push({
        demand,
        supply: supplied,
        price,
        reward: rew.score,
        balance: supplied - demand,
      });
      if (historyData.length > 120) {
        historyData.shift();
      }
      drawChart();

      updateRisk(demand, supplied, rew.blackout_penalty || 0, Boolean(obs.shock_active));

      const actionDelta = Math.max(0, demand - supplied).toFixed(0);
      const actionText = unmet > 0
        ? `Action: Increase peaker by ${Math.min(20, 6 + Number(actionDelta)).toFixed(0)} MW`
        : `Action: Hold peaker, optimize renewable dispatch`;

      const reasonLines = [
        scarcity > 0.35 ? 'Scarcity rising' : 'Scarcity contained',
        obs.shock_active ? 'Demand shock detected' : 'No active shock',
        unmet > 0 ? 'Constraint risk rising' : 'Constraint risk stable',
      ].join('\n');

      updatePolicyPanel(
        policy === 'adaptive' ? 'Adaptive Dispatch Policy' : policy === 'heuristic' ? 'Baseline Heuristic Policy' : 'Random Response Policy',
        actionText,
        reasonLines,
        rew,
      );

      const riskNow = (rew.blackout_penalty || 0) * 100;
      if (obs.shock_active) {
        shockCount += 1;
        document.getElementById('countShocks').textContent = String(shockCount);
        appendLog('Shock event active: renewable crash scenario', 'shock');
        appendThreat(`Shock at t${res.observation.step}: renewable drop ${(info.dynamics && info.dynamics.shock_renewable_drop) || 0} MW`);
        setStressMode(true, 'Stress mode engaged: renewable crash and load spike');
      } else if (riskNow < 12 && unmet < 1) {
        setStressMode(false);
      }

      document.getElementById('globalStatusDot').style.background = riskNow > 30 || unmet > 0 ? 'var(--red)' : riskNow > 10 ? 'var(--amber)' : 'var(--green)';
      document.getElementById('globalStatusDot').style.boxShadow = riskNow > 30 || unmet > 0 ? 'var(--critical-glow)' : riskNow > 10 ? 'var(--stress-glow)' : 'var(--ok-glow)';
      document.getElementById('liveState').textContent = riskNow > 30 || unmet > 0 ? 'ALERT' : 'LIVE';
    }

    function play() {
      pause();
      timer = setInterval(() => {
        step().catch((e) => appendLog(`Step failed: ${e.message}`, 'error'));
      }, 450);
    }

    function pause() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    async function injectShock() {
      if (!sessionId) {
        return;
      }
      await api('/inject-shock', { renewable_drop_mwh: 25 });
      shockCount += 1;
      document.getElementById('countShocks').textContent = String(shockCount);
      appendLog('Manual shock injected (-25 MW renewable)', 'shock');
      appendThreat('Manual shock command accepted. Grid entering stress mode.');
      setStressMode(true, 'Stress mode engaged: manual shock injection');
      document.getElementById('shockProb').textContent = 'MANUAL';
    }

    function toggleSidebar() {
      const panel = document.getElementById('sidePanel');
      const collapsed = panel.classList.toggle('collapsed');
      const t = document.getElementById('sideToggle');
      t.textContent = collapsed ? '>' : '<';
      document.getElementById('sideState').textContent = collapsed ? 'Collapsed' : 'Expanded';
    }

    document.getElementById('resetBtn').onclick = () => {
      pause();
      reset().catch((e) => appendLog(`Reset failed: ${e.message}`, 'error'));
    };

    document.getElementById('stepBtn').onclick = () => {
      pause();
      step().catch((e) => appendLog(`Step failed: ${e.message}`, 'error'));
    };

    document.getElementById('playBtn').onclick = play;
    document.getElementById('pauseBtn').onclick = pause;

    document.getElementById('shockBtn').onclick = () => {
      injectShock().catch((e) => appendLog(`Shock failed: ${e.message}`, 'error'));
    };

    document.getElementById('baselineBtn').onclick = () => {
      applyBaselineMode(!baselineMode);
    };

    document.getElementById('modeRl').onclick = () => applyBaselineMode(false);
    document.getElementById('modeBase').onclick = () => applyBaselineMode(true);

    document.getElementById('sidePlay').onclick = play;
    document.getElementById('sidePause').onclick = pause;
    document.getElementById('sideStep').onclick = () => {
      pause();
      step().catch((e) => appendLog(`Step failed: ${e.message}`, 'error'));
    };
    document.getElementById('sideShock').onclick = () => {
      injectShock().catch((e) => appendLog(`Shock failed: ${e.message}`, 'error'));
    };

    document.getElementById('taskSel').onchange = () => {
      reset().catch((e) => appendLog(`Reset failed: ${e.message}`, 'error'));
    };

    document.getElementById('polSel').onchange = () => {
      const p = document.getElementById('polSel').value;
      if (p === 'adaptive') {
        applyBaselineMode(false);
      } else if (p === 'heuristic') {
        applyBaselineMode(true);
      }
    };

    document.getElementById('sideToggle').onclick = toggleSidebar;

    resizeChart();
    reset().catch((e) => appendLog(`Initial reset failed: ${e.message}`, 'error'));
  </script>
</body>
</html>
"""
