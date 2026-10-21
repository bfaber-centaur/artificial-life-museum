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
| [P3-panel.png](P3-panel.png) | REEF-P3-E (GA, b/R +0.99) | The selected contrast: flank contact, slowest ignition, same fate. |

Not shown and not claimed: numerical checks (numerics lane), R26, T20, a larger world.
