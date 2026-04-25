# LDU Ablation Comparison (adaptive policy)

| Scenario | Profile | Avg Reward | Avg Cost USD | Blackout Rate | Reserve Shortfall Rate | Stability Event Rate |
|---|---|---:|---:|---:|---:|---:|
| normal | ablate_ramp | 0.3491 | 21890.217 | 0.5417 | 0.9583 | 0.2500 |
| normal | ablate_reserve | 0.5845 | 21673.586 | 0.5833 | 0.0000 | 0.0000 |
| normal | ablate_startup_emissions | 0.3611 | 20022.278 | 0.5833 | 0.9583 | 0.2500 |
| normal | full_ldu | 0.3495 | 21673.586 | 0.5833 | 0.9583 | 0.2500 |
| outage | ablate_ramp | 0.1745 | 1831.957 | 1.0000 | 1.0000 | 1.0000 |
| outage | ablate_reserve | 0.3786 | 1831.957 | 1.0000 | 0.0000 | 0.7667 |
| outage | ablate_startup_emissions | 0.1744 | 1831.957 | 1.0000 | 1.0000 | 1.0000 |
| outage | full_ldu | 0.1744 | 1831.957 | 1.0000 | 1.0000 | 1.0000 |
| renewable_collapse | ablate_ramp | 0.1687 | 1398.162 | 1.0000 | 1.0000 | 1.0000 |
| renewable_collapse | ablate_reserve | 0.3684 | 1398.162 | 1.0000 | 0.0000 | 0.9667 |
| renewable_collapse | ablate_startup_emissions | 0.1687 | 1398.162 | 1.0000 | 1.0000 | 1.0000 |
| renewable_collapse | full_ldu | 0.1687 | 1398.162 | 1.0000 | 1.0000 | 1.0000 |
| shock | ablate_ramp | 0.1678 | 1301.792 | 1.0000 | 1.0000 | 1.0000 |
| shock | ablate_reserve | 0.3664 | 1301.792 | 1.0000 | 0.0000 | 0.9667 |
| shock | ablate_startup_emissions | 0.1678 | 1301.792 | 1.0000 | 1.0000 | 1.0000 |
| shock | full_ldu | 0.1678 | 1301.792 | 1.0000 | 1.0000 | 1.0000 |
