# Policy Comparison

| Policy | Scenario | Task | Avg Reward | Avg Cost USD | Blackout Rate | Constraint Violation Rate | Emissions tCO2 | Reserve Shortfall Rate | Stability Event Rate |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| adaptive | normal | normal | 0.3906 | 21611.331 | 0.5000 | 4.2917 | 876.8049 | 0.9583 | 0.2500 |
| heuristic | normal | normal | 0.5084 | 13530.967 | 0.9583 | 1.7917 | 777.7254 | 0.4583 | 0.2500 |
| random | normal | normal | 0.4896 | 13416.274 | 0.7083 | 4.2500 | 824.1362 | 0.6250 | 0.2500 |
| adaptive | outage | outage | 0.1563 | 800.626 | 1.0000 | 5.0000 | 0.0000 | 1.0000 | 1.0000 |
| heuristic | outage | outage | 0.4150 | 17053.054 | 0.9333 | 2.8000 | 1125.7141 | 0.7000 | 0.3667 |
| random | outage | outage | 0.4512 | 16678.429 | 0.8000 | 4.5333 | 1215.8771 | 0.5667 | 0.3000 |
| adaptive | renewable_collapse | renewable_collapse | 0.1637 | 1068.897 | 1.0000 | 5.0333 | 0.0000 | 1.0000 | 1.0000 |
| heuristic | renewable_collapse | renewable_collapse | 0.4060 | 17826.900 | 0.9000 | 2.8333 | 1185.0863 | 0.7000 | 0.3333 |
| random | renewable_collapse | renewable_collapse | 0.4129 | 17350.788 | 0.9000 | 4.9000 | 1252.6913 | 0.7333 | 0.2667 |
| adaptive | shock | stress_shock | 0.1558 | 950.583 | 1.0000 | 5.0333 | 0.0000 | 1.0000 | 1.0000 |
| heuristic | shock | stress_shock | 0.3909 | 17577.627 | 0.9000 | 2.7333 | 1147.9199 | 0.7000 | 0.4000 |
| random | shock | stress_shock | 0.4128 | 16854.880 | 0.9000 | 4.7000 | 1225.6502 | 0.6333 | 0.3333 |
