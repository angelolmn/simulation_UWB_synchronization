import os
import sys
import json
import argparse
import numpy as np
import networkx as nx
import subprocess

parser = argparse.ArgumentParser(description="Proportional Control Law Simulation for clock synchronization.")

parser.add_argument("-g", "--graph", type=str, default="k4.graphml",
    help="GraphML file in graphs directory (Default: 'k4.graphml').")

parser.add_argument("-i", "--iterations", type=int, default=100,
    help="Number of iterations (Default: 100).")

parser.add_argument("-k", "--gain", type=float, default=0.1,
    help="Proportional gain k. Stability requires k < 1/max_degree (Default: 0.1).")

parser.add_argument("--gamma", type=float, default=0.0,
    help="Integral gain gamma. Set to 0 to disable (proportional only) (Default: 0.0).")

parser.add_argument("--plot", action="store_true", help="Run plot script after simulation.")

args = parser.parse_args()

graph_file = "graphs/" + args.graph
time_steps = args.iterations
kappa = args.gain
gamma = args.gamma

np.random.seed(42)

if not os.path.exists(graph_file):
    print(f"Error: The file '{graph_file}' does not exist.")
    sys.exit(1)

# Load graph and build scaled Laplacian
G = nx.read_graphml(graph_file)
node_list = list(G.nodes())
n_nodes = len(node_list)

L = nx.laplacian_matrix(G).toarray().astype(float)
max_degree = max(dict(G.degree()).values())

if kappa >= 1.0 / max_degree:
    print(f"Warning: k={kappa} violates stability condition k < 1/max_degree = {1.0/max_degree:.4f}")

# Initial conditions: random offsets x and skews d
x = np.random.uniform(0, 10, size=n_nodes)
d = np.random.uniform(0.9, 1.1, size=n_nodes)

# Initial integral state
w = np.zeros(n_nodes)

x_init = x.copy()
d_ave  = np.mean(d)
x_ave0 = np.mean(x)

# Storage
x_history     = np.zeros((time_steps, n_nodes))
error_history = np.zeros(time_steps)

# Main loop (Proportional control: x(i+1) = (I - kL)x(i) + d)
A = np.eye(n_nodes) - kappa * L

for step in range(time_steps):
    t_ave = d_ave * step + x_ave0
    y     = x - t_ave * np.ones(n_nodes)

    x_history[step, :]  = x
    error_history[step] = np.linalg.norm(y)
    
    Lx    = L @ x
    x     = A @ x - w + d
    w     = w + args.gamma * Lx

# --- Save results ---
save_dir = f"results/control_law_pi/{os.path.splitext(args.graph)[0]}/i{time_steps}_k{kappa}_gamma{gamma}"
os.makedirs(save_dir, exist_ok=True)

# errors.csv
header = "step," + ",".join([f"x_{v}" for v in node_list]) + ",error_norm"
data   = np.column_stack([np.arange(time_steps), x_history, error_history])
np.savetxt(f"{save_dir}/errors.csv", data, delimiter=",", header=header, comments="")
print(f"Saved: {save_dir}/errors.csv")

# params.json
params = {
    "graph":      args.graph,
    "iterations": time_steps,
    "gain":       kappa,
    "gamma":      gamma,
    "nodes":      node_list,
    "x_init":     x_init.tolist(),
    "d":          d.tolist(),
    "d_ave":      float(d_ave),
    "x_ave0":     float(x_ave0),
}
with open(f"{save_dir}/params.json", "w") as f:
    json.dump(params, f, indent=2)
print(f"Saved: {save_dir}/params.json")

flags = ["-g", args.graph, "-i", str(time_steps), "-k", str(kappa), "--gamma", str(gamma)]

if args.plot:
    subprocess.run(["uv", "run", "src/control_law_pi/plot_results.py", *flags], check=True)