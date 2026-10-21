# Exhibit panels (behavior lane)

Rendered by [`../exhibit.py`](../exhibit.py) from REEF-field frames (sha256 in each caption) and this lane's scores.
All panels: rule poly/poly, μ 0.155, σ 0.020, R 13, T 10, Euler + clip, float64, periodic N 256 (19.7 R).
Finite horizon: each encounter is scored on its window t_c + 20 tu, and frames after ~27 tu show the
colony meeting its own periodic images on the torus. Field is A in [0, 1], white to dark blue; scale bar 5 R.

| panel | run | what it shows |
|---|---|---|
| [A-P2-main.png](A-P2-main.png) | REEF-P2-E (GA, b/R +0.02) | **Main panel.** Encounter vs glider alone vs ring alone at 0, t_c (6.1), t_c + 5, + 10, + 20 tu, and total mass on a log axis with t_kr, t_int, t_c and the window end. Contact ignites an expanding colony; the controls are unchanged. |
| [B-offset-strip.png](B-offset-strip.png) | X1, X2, P1, P2, P3, X3, X4 (GA) | Every contact offset from b/R −1.5 to +1.5 ignites. Each frame is at its own t_c + 20 tu. |
| [C-X7-null.png](C-X7-null.png) | REEF-X7-E | **Null.** A static blob of the glider's mass at the glider's pre-contact position (2.1 R) evaporates in 1.4 tu without contact; the ring stays bitwise S103. |
| [D-X9-blob-in-contact.png](D-X9-blob-in-contact.png) | REEF-X9-E | The same blob placed at the glider's contact position ignites the same colony: the glider is a delivery mechanism. |
| [E-X11-half-dose.png](E-X11-half-dose.png) | REEF-X11-E | Half the dose at the contact position evaporates in 0.3 tu; the ring returns bitwise. |
| [F-check-matrix.png](F-check-matrix.png) | numerics routes for P2, P3 | **Numerics matrix.** Route × {class, t_c, ignition (D-017), front speed, E mass t20} from reef/numerics `e7d4ef6` `checks/matrix.json` (copied as `F-numerics-matrix.json`). Every route keeps FISSION; at R 26 that is the primary label under D-010 (see the R 26 note below). T 20 and R 26 timing and mass fall outside the frozen §9 tolerance. |
| [P3-panel.png](P3-panel.png) | REEF-P3-E (GA, b/R +0.99) | The selected contrast: flank contact, slowest ignition, same fate. |

**R 26 rescore (applying D-010, ruling D-024; not a new rule).** At R 26 the ring is judged against its own R 26
ring-alone control, never bitwise: the control is valid if it stays one STATIC body (< 0.02 R/tu) through the window,
and ring tolerance is relative to that control at the same time. It does (0.0003 R/tu), so the **primary label for P2
and P3 at R 26 is FISSION + PROLIFERATION** (P2 95 bodies, P3 60 at window end; `../scores/REEF-P?-E-R26-D010/score.json`).
Disclosed variant (D-024): additionally requiring ring-alone mass in 0.378–0.383 (the numerics 200–300 tu range) gives
CONTROL_FAILURE, because the ring-alone dips to 0.3759 at 4–11 tu as the 2×2-block seed relaxes, before contact
(`score-mass-band-variant.json`). Both are scored with `score.py`'s `score_rows_file` from the numerics lane's per-step recorder rows
(reef/numerics `8f17849`, `checks/REEF-P?-E-R26-rows/recorder/trace.jsonl` in project files, sha256 P2 `77eb6d8c…`,
P3 `01cfc2aa…`; t_c 6.1 / 6.7, t_int 5.4 / 5.9). An earlier 1-tu checkpoint-cadence rescore gave the same labels
(t_c 7.0 at that cadence, 111 / 63 bodies at its window end).
