import json
import os
import sys
import argparse
import numpy as np
import networkx as nx
import subprocess

parser = argparse.ArgumentParser(description="Clock Rigidity Simulation with NetworkX and Gradient Descent.")

parser.add_argument("-g", "--graph", type=str, default="k4.graphml", 
    help="GraphML file that contains the graph in graphs directory (Default: 'k4.graphml').")

parser.add_argument("-i", "--iterations", type=int, default=10000, 
    help="Number of iterations (resolution time is 0.1 ms) for the algorithm processing (Default: 10000).")

parser.add_argument("-kg", "--gain", type=float, default=0.25, 
    help="Gain parameter for the algorithm processing (Default: 0.25).")

parser.add_argument("--plot", action="store_true", help="Run plot script after simulation.")
parser.add_argument("--val",  action="store_true", help="Run verify script after simulation.")

args = parser.parse_args()

graph_file = "graphs/" + args.graph
time_steps = args.iterations
kg = args.gain

np.random.seed(42)

if not os.path.exists(graph_file):
    print(f"Error: The file '{graph_file}' does not exist.")
    sys.exit(1)

# Load the graph from the specified GraphML file
G = nx.read_graphml(graph_file)

# Map nodes to indices for easier handling in arrays
node_list = list(G.nodes())
n_nodes = len(node_list)
node_to_idx = {node: idx for idx, node in enumerate(node_list)}

# Index the edges as pairs of node indices 
edges = [(node_to_idx[u], node_to_idx[v]) for u, v in G.edges()]
n_edges = len(edges)

# Physics constant and parameters
c = 3e8  # Light speed (m/s)

# True clocks configuration: phi = [alpha, beta]
alpha_true = np.random.uniform(0.995, 1.005, size=n_nodes)
beta_true  = np.random.uniform(-0.005, 0.005, size=n_nodes)

# Distance and time stamps generation for each edge (i, j)
distances = np.random.uniform(10, 100, size=n_edges) 
T_send_i = np.random.uniform(0.1, 0.5, size=n_edges)
T_send_j = np.random.uniform(0.1, 0.5, size=n_edges)

T_recv_j = np.zeros(n_edges)
T_recv_i = np.zeros(n_edges)
T_bar_i = np.zeros(n_edges)
T_bar_j = np.zeros(n_edges)

for k, (i, j) in enumerate(edges):
    T_recv_j[k] = (distances[k]/c + alpha_true[i]*T_send_i[k] + beta_true[i] - beta_true[j]) / alpha_true[j]
    T_recv_i[k] = (distances[k]/c + alpha_true[j]*T_send_j[k] + beta_true[j] - beta_true[i]) / alpha_true[i]
    
    T_bar_i[k] = (T_send_i[k] + T_recv_i[k]) / 2.0
    T_bar_j[k] = (T_send_j[k] + T_recv_j[k]) / 2.0


# Initial parameter estimates with small random perturbations around the true values 
alpha_est = alpha_true + np.random.uniform(-0.002, 0.002, size=n_nodes)
beta_est  = beta_true + np.random.uniform(-0.002, 0.002, size=n_nodes)

alpha_init, beta_init = alpha_est.copy(), beta_est.copy()

error_history = np.zeros((time_steps, n_edges))
time_axis = np.arange(time_steps)

# Main loop simulation (Eq 33)
for step in range(time_steps):

    # Compute the error for each edge based on current estimates 
    e_c = np.zeros(n_edges)
    for k, (i, j) in enumerate(edges):
        e_c[k] = alpha_est[j]*T_bar_j[k] + beta_est[j] - (alpha_est[i]*T_bar_i[k] + beta_est[i])
    
    error_history[step, :] = np.abs(e_c)
    
    grad_alpha = np.zeros(n_nodes)
    grad_beta = np.zeros(n_nodes)
    
    # Parameter update based on the gradient of the error 
    for k, (i, j) in enumerate(edges):
        grad_alpha[j] += e_c[k] * T_bar_j[k]
        grad_beta[j]  += e_c[k] * 1.0
        grad_alpha[i] += e_c[k] * (-T_bar_i[k])
        grad_beta[i]  += e_c[k] * (-1.0)
    
    alpha_est -= kg * grad_alpha
    beta_est  -= kg * grad_beta

# Save the results
save_dir = f"results/clock_rigidity/{os.path.splitext(args.graph)[0]}/i{time_steps}_kg{kg}"
os.makedirs(save_dir, exist_ok=True)

# errors.csv
edge_labels = [f"edge_{node_list[i]}_{node_list[j]}" for i, j in edges]
header = "step,time," + ",".join(edge_labels)
data = np.column_stack([np.arange(time_steps), time_axis, error_history])
np.savetxt(f"{save_dir}/errors.csv", data, delimiter=",", header=header, comments="")
print(f"Saved: {save_dir}/errors.csv")

# params.json
params = {
    "graph":      args.graph,
    "iterations": time_steps,
    "gain":       kg,
    "alpha_true": alpha_true.tolist(),
    "beta_true":  beta_true.tolist(),
    "alpha_init": alpha_init.tolist(),
    "beta_init":  beta_init.tolist(),
    "alpha_est":  alpha_est.tolist(),
    "beta_est":   beta_est.tolist(),
}

with open(f"{save_dir}/params.json", "w") as f:
    json.dump(params, f, indent=2)
print(f"Saved: {save_dir}/params.json")


flags = ["-g", args.graph, "-i", str(time_steps), "-kg", str(kg)]

if args.plot:
    subprocess.run(["uv", "run", "src/clockrigidity/plot_results.py", *flags], check=True)

if args.val:
    subprocess.run(["uv", "run", "src/clockrigidity/validate.py", *flags], check=True)