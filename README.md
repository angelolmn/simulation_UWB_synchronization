# UWB Clock Synchronization — Simulations

Python simulations for the TFM *"Sincronización temporal en redes UWB distribuidas mediante rigidez de relojes"* (University of Granada). The code covers two distributed clock-synchronization approaches over network topologies:

- **Clock rigidity** — gradient-descent estimation of per-node clock parameters (skew $\alpha$, offset $\beta$).
- **PI control law** — a proportional–integral consensus algorithm for distributed clock synchronization.

## Requirements

- Python ≥ 3.10
- [uv](https://docs.astral.sh/uv/) as the package/environment manager

Dependencies (NumPy, NetworkX, Matplotlib, pandas) are declared in `pyproject.toml` and pinned in `uv.lock`.

## Setup

```bash
git clone <repo-url>
cd simulacion
uv sync
```

> Run all commands from the repository root. Scripts use paths relative to it (`graphs/`, `results/`, `src/`).

The simulation outputs (`results/`) and the graph topologies (`graphs/`) are generated and are not tracked in git. Generate the topologies before running any simulation (see step 1 below).

## Usage

### 1. Generate graph topologies

Creates complete graphs $K_n$ and path graphs $P_n$ up to $n$ nodes, saved as GraphML files in `graphs/`:

```bash
uv run src/graph_utils/generate_basics_graphs.py -n 10
```

Plot a single topology:

```bash
uv run src/graph_utils/plot_graph.py -f graphs/k4.graphml
```

### 2. Run a single simulation

**Clock rigidity:**

```bash
uv run src/clockrigidity/clock_rigidity.py -g k4.graphml -i 10000 -kg 0.25 --plot --val
```

**PI control law:**

```bash
uv run src/control_law_pi/control_law_pi.py -g k4.graphml -i 1000 -k 0.1 --gamma 0.01 --plot
```

`--plot` generates figures after the run; `--val` (clock rigidity only) checks convergence to a trivial variation. Results are written to `results/<module>/<graph>/<run-params>/` as `errors.csv` and `params.json`.

## Project structure

```
.
├── graphs/                          # GraphML topologies (Kn, Pn) — generated, gitignored
├── results/                         # Generated CSVs, JSON, figures (gitignored)
├── src/
│   ├── clockrigidity/
│   │   ├── clock_rigidity.py        # Gradient-descent clock rigidity simulation
│   │   ├── plot_results.py          # Parameter-space and error plots
│   │   └── validate.py              # Trivial-variation convergence check
│   ├── control_law_pi/
│   │   ├── control_law_pi.py        # PI consensus simulation
│   │   └── plot_results.py          # Clock-state and error plots
│   └── graph_utils/
│       ├── generate_basics_graphs.py  # Generate Kn / Pn GraphML topologies
│       └── plot_graph.py              # Visualize a single topology
├── pyproject.toml
└── uv.lock
```

## License

Released under the MIT License. See [LICENSE](LICENSE).
