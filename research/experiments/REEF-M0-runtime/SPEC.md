# REEF-M0 runtime benchmark specification

Committed before any timing result. Calibration only: these are timing inputs, not an encounter.

Rule (all cases): float64, poly kernel / poly growth, Euler + clip, periodic torus, mu=0.155, sigma=0.020.

Input construction (`bench.py:make_input`): an N x N zero world; S001 cells
(`alm.specimens.load("S001").cells/255`) placed with top-left at (N/4 - h/2, N/4 - w/2),
S103 cells (`alm.specimens.load("S103").cells/255`) at (3N/4 - h/2, 3N/4 - w/2). Batches of W
stack W copies (identical, since batch is a cost test). R=26 cases block-resize the N256
input with `np.kron(A, ones((2,2)))` (same physical extent as N256/R13). SHA-256 of the
float64 C-order input bytes is recorded.

Cases (each in a fresh subprocess, `python bench.py case <id>`):

| id | N | R | T | W | mode |
|---|---|---|---|---|---|
| n256-w1-engine | 256 | 13 | 10 | 1 | `alm.lenia.Lenia.step` |
| n256-w1-batch | 256 | 13 | 10 | 1 | `field.Batch.run`, snap_every=inf (per-step mass+centroid only) |
| n256-w1-instr | 256 | 13 | 10 | 1 | `field.Batch.run`, morph snapshot every T steps (1 tu) |
| n256-w2-batch / -instr | 256 | 13 | 10 | 2 | as above |
| n256-w4-batch / -instr | 256 | 13 | 10 | 4 | as above |
| n256-w4-engine | 256 | 13 | 10 | 4 | 4 sequential `Lenia` objects |
| n512-r13-engine / -instr | 512 | 13 | 10 | 1 | |
| n512-r26-engine / -instr | 512 | 26 | 10 | 1 | |
| n256-t20-engine / -instr | 256 | 13 | 20 | 1 | |
| check-fft | 256 | 13 | 10 | 1 | `alm_check.lenia.World(path="fft")` |
| check-direct | 256 | 13 | 10 | 1 | `alm_check.lenia.World(path="direct", boundary="wrap")` |

Timing: setup (input + kernel construction) timed separately; 10 warm-up steps
(3 for direct); a 1-sample probe sets step count to target ~3 s per sample; 3 samples;
per-case ceiling 30 s of timed stepping (fewer samples / steps recorded as truncation).
Recorded per sample: wall (perf_counter), process CPU (process_time), steps, worlds,
world-steps/s, tu/s/world. Per case: ru_maxrss of the case process (peak RSS of
that single process; no children are spawned), final-state SHA-256, and for -instr
cases the bytes of a compressed npz of series + final state (output-size proxy).

Correctness smoke (`bench.py smoke`): (a) `Lenia` vs `Batch` (W=1) vs `alm_check` fft
after 200 steps on the N256 input: max |diff|; (b) direct vs fft after 20 steps: max |diff|
(different arithmetic, so a small non-zero difference is expected); (c) existing
`tests/test_lane6_specimens.py::test_s103_is_an_exact_fixed_point` and `tests/test_lenia.py`.

Thread budget: OMP/OPENBLAS/MKL threads pinned to 1 (numpy FFT is pocketfft, single-threaded).
Concurrency: two `n256-w1-engine` processes run at once (`bench.py concurrent`) to test
multiprocessing vs batching.
