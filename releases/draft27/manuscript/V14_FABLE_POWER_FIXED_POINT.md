# Fable V13 power–mass feedback: evaluator-only arithmetic

The [source-hashed result](../analysis/results/v14_fable_power_fixed_point01.json) independently recomputes the **model's own assumed worst case** from its complete V13 response (SHA-256 `dae66235761235d241c8773d9af9c9700187d9920db638a17ce6dcda9bc4b379`). The rerunnable calculation is in [`analysis/audit_v14_fable_power_fixed_point.py`](../analysis/audit_v14_fable_power_fixed_point.py). None of the drag, propulsive efficiency, gearbox efficiency, specific engine mass, fuel flow or engine availability has been measured.

The specified case has a 364.3 kg heavy loading, 13 m/s, $q=103.51$ Pa, $S=42$ m², $C_{D0}=0.08$, $e=0.70$, $AR=6.2$, an extra 10 N drag, propulsive efficiency 0.45, drive efficiency 0.95 and a 15% shaft-power reserve. With $C_L=W/(qS)$ and $C_{Di}=C_L^2/(\pi e AR)$, the required engine-side power is

$$P_{e,\min}(m)=\frac{1.15V}{\eta_p\eta_g}\left[qS\left(C_{D0}+\frac{(mg/qS)^2}{\pi e AR}\right)+10\,\mathrm{N}\right].$$

| Arithmetic state under those assumptions | Result |
|---|---:|
| Heavy-case propeller-shaft requirement, no reserve | 16.561 kW |
| Propeller-shaft requirement with 15% reserve | 19.045 kW |
| Available at shaft from the *target* 19.5 kW engine and assumed 0.95 drive | 18.525 kW |
| Shortfall at the shaft | **0.520 kW** |
| Minimum engine-side target without engine-mass growth | 20.047 kW |
| Minimum drive efficiency if the 19.5 kW engine target is held fixed | 0.9767 |
| Self-consistent engine target using the *assumed incremental* 5.1 kg/kW mass rule | **20.195 kW** |
| Added engine mass / revised heavy-case mass in that scenario | 3.543 / 367.843 kg |

The fixed point solves $P_e=P_{e,\min}[364.3+5.1(P_e/1000-19.5)]$ with $P_e$ in watts; its numerical residual is below $4\times10^{-12}$ W. It is **not** a revised aircraft. The hypothetical heavier engine would reopen the component ledger, CG, structure, cooling and clearance calculations. The retained 19.5 kW target has only 11.86% paper reserve, not 15%. The model's retained 20 kg fuel row and assumed 0.31 kg/kWh at 19.5 kW imply 198.5 min, not its stated 20 min; that arithmetic contradiction cannot be turned into a real endurance claim.

Disposition: **HOLD**. A named engine with continuous torque/power, fuel and heat-rejection data, a measured transmission-efficiency map, and a matched propeller $C_P/C_T$ or stand test are required before installed thrust or flight is assessed. Raising a target number in a prompt does not close this gate.
