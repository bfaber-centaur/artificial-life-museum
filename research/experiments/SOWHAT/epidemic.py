"""Why space matters for epidemics: the same SIR disease, well mixed and on a lattice.

Every person is S, I or R. Each time step every infectious person makes 4 contacts and each
contact with a susceptible person transmits with probability beta; each infectious person then
recovers with probability gamma. The three worlds differ only in WHO the 4 contacts are:

* "mixed":     4 people drawn at random from the whole population (the assumption behind the
               textbook Kermack-McKendrick equations);
* "lattice":   the 4 nearest neighbours on a periodic grid;
* "shortcuts": the 4 nearest neighbours, but each contact is redirected to a random person
               with probability p (default 0.01), as in a small-world network.

Infection is applied simultaneously from the start-of-step state. A susceptible person reached
by m infectious contacts escapes with probability (1 - beta)**m.

Every run starts with 9 infectious people in a 3 x 3 block at the centre.

  python epidemic.py runs OUT.jsonl        10 seeds x 3 worlds, 200 x 200, beta 0.15, gamma 0.1
  python epidemic.py threshold OUT.jsonl   final size vs beta (0.02-0.20), 5 seeds x 3 worlds
"""
import json
import sys

import numpy as np

S, I, R = 0, 1, 2
OFFS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Epidemic:
    def __init__(self, n, world, beta=0.15, gamma=0.1, p=0.01, seed=0):
        self.n, self.world, self.beta, self.gamma, self.p = n, world, beta, gamma, p
        self.rng = np.random.default_rng(seed)
        self.x = np.zeros((n, n), dtype=np.int8)
        c = n // 2
        self.x[c - 1:c + 2, c - 1:c + 2] = I  # nine infectious people in a 3 x 3 block
        self.t = 0

    def _random_hits(self, count):
        """Contacts landing on uniformly random people: returns hits per cell."""
        hits = np.zeros(self.n * self.n, dtype=np.int64)
        if count:
            np.add.at(hits, self.rng.integers(0, self.n * self.n, count), 1)
        return hits.reshape(self.n, self.n)

    def step(self):
        inf = self.x == I
        n_inf = int(inf.sum())
        if self.world == "mixed":
            m = self._random_hits(4 * n_inf)
        else:
            if self.world == "lattice":
                local = inf.astype(np.int64)
                m = sum(np.roll(local, o, (0, 1)) for o in OFFS)
            else:  # shortcuts: each of the 4 contacts of each infectious person rewired w.p. p
                m = np.zeros_like(inf, dtype=np.int64)
                rewired = 0
                for o in OFFS:
                    keep = inf & (self.rng.random(inf.shape) >= self.p)
                    rewired += int(inf.sum() - keep.sum())
                    m += np.roll(keep.astype(np.int64), o, (0, 1))
                m += self._random_hits(rewired)
        sus = self.x == S
        catch = sus & (self.rng.random(self.x.shape) >= (1 - self.beta) ** m)
        recover = inf & (self.rng.random(self.x.shape) < self.gamma)
        self.x[catch] = I
        self.x[recover] = R
        self.t += 1
        return self.x

    def counts(self):
        return np.bincount(self.x.ravel(), minlength=3) / self.x.size


WORLDS = ["mixed", "lattice", "shortcuts"]
N, SEEDS, TMAX = 200, 10, 3000
BETAS = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2]


def simulate(world, seed, beta=0.15):
    E = Epidemic(N, world, beta=beta, seed=seed)
    series = [E.counts()[1]]
    while E.counts()[1] > 0 and E.t < TMAX:
        E.step()
        series.append(E.counts()[1])
    return E, np.array(series)


def run_threshold(path):
    with open(path, "w") as f:
        for world in WORLDS:
            for j, beta in enumerate(BETAS):
                for seed in range(5):
                    sd = [2026, 11, 15, 4, j, seed]
                    E, series = simulate(world, sd, beta)
                    row = dict(world=world, beta=beta, seed=sd, steps=E.t,
                               final_size=float(E.counts()[1] + E.counts()[2]),
                               peak=float(series.max()))
                    f.write(json.dumps(row) + "\n")
                    print(world, beta, seed, round(row["final_size"], 4))


def run_all(path):
    with open(path, "w") as f:
        for world in WORLDS:
            for seed in range(SEEDS):
                E = Epidemic(N, world, seed=[2026, 11, 15, 3, seed])
                series = [E.counts()[1]]
                while E.counts()[1] > 0 and E.t < TMAX:
                    E.step()
                    series.append(E.counts()[1])
                series = np.array(series)
                row = dict(world=world, seed=seed, n=N, beta=E.beta, gamma=E.gamma, p=E.p,
                           steps=E.t, peak=float(series.max()), t_peak=int(series.argmax()),
                           final_size=float(E.counts()[2] + E.counts()[1]),
                           still_infected=float(E.counts()[1]),
                           infected=[round(float(v), 6) for v in series])
                f.write(json.dumps(row) + "\n")
                print(world, seed, row["steps"], round(row["peak"], 4), row["t_peak"],
                      round(row["final_size"], 4))


if __name__ == "__main__":
    if sys.argv[1] == "runs":
        run_all(sys.argv[2])
    elif sys.argv[1] == "threshold":
        run_threshold(sys.argv[2])
