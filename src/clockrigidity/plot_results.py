import os
import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

parser = argparse.ArgumentParser(description="Plot Clock Rigidity Simulation results.")

parser.add_argument("-g", "--graph", type=str, default="k4.graphml",
    help="GraphML file name used in the simulation (Default: 'k4.graphml').")

parser.add_argument("-i", "--iterations", type=int, default=10000,
    help="Number of iterations used in the simulation (Default: 10000).")

parser.add_argument("-kg", "--gain", type=float, default=0.25,
    help="Gain parameter used in the simulation (Default: 0.25).")

args = parser.parse_args()

graph_file = "graphs/" + args.graph
time_steps = args.iterations
kg = args.gain


save_dir = f"results/clock_rigidity/{os.path.splitext(args.graph)[0]}/i{args.iterations}_kg{args.gain}"

if not os.path.exists(save_dir):
    print(f"Error: The results directory '{save_dir}' does not exist. Please run the simulation first.")
    sys.exit(1)

params_path = f"{save_dir}/params.json"
errors_path = f"{save_dir}/errors.csv"

if not os.path.exists(params_path):
    print(f"Error: '{params_path}' does not exist. Please run the simulation first.")
    sys.exit(1)
if not os.path.exists(errors_path):
    print(f"Error: '{errors_path}' does not exist. Please run the simulation first.")
    sys.exit(1)

G = nx.read_graphml(graph_file)
node_list = list(G.nodes())
n_nodes   = len(node_list)
edges     = [(node_list.index(u), node_list.index(v)) for u, v in G.edges()]
n_edges   = len(edges)

with open(params_path) as f:
    params = json.load(f)

data = np.loadtxt(errors_path, delimiter=",", skiprows=1)
time_axis     = data[:, 1]
error_history = data[:, 2:]

alpha_true = np.array(params["alpha_true"])
beta_true  = np.array(params["beta_true"])
alpha_init = np.array(params["alpha_init"])
beta_init  = np.array(params["beta_init"])
alpha_est  = np.array(params["alpha_est"])
beta_est   = np.array(params["beta_est"])


# Plot (a): Parameters space (True, Initial, Estimated Final)
fig1, ax1 = plt.subplots(figsize=(7, 5))

ax1.scatter(alpha_true, beta_true, color='black', marker='o', s=60, label='True', zorder=5)
ax1.scatter(alpha_est, beta_est, color='gray', marker='^', s=60, label='Estimated', zorder=4)
ax1.scatter(alpha_init, beta_init, color='silver', marker='d', s=50, label='Initial', zorder=3)

# Plot the lines graph for the true and estimated parameters
for (i, j) in edges:
    ax1.plot([alpha_true[i], alpha_true[j]], [beta_true[i], beta_true[j]], 'k-', alpha=0.8, lw=1)
    ax1.plot([alpha_est[i], alpha_est[j]], [beta_est[i], beta_est[j]], 'g--', alpha=0.6, lw=1)

# Arrows that indicate the total displacement from the initial to the final estimation for each node
for node in range(n_nodes):
    ax1.annotate('', xy=(alpha_est[node], beta_est[node]), xytext=(alpha_init[node], beta_init[node]),
                 arrowprops=dict(arrowstyle="->", color='red', lw=0.8, alpha=0.7))

ax1.set_xlabel('Clock skew ($\\alpha$)')
ax1.set_ylabel('Clock offset ($\\beta$)')
ax1.grid(True, linestyle=':')
ax1.legend()
fig1.tight_layout()

output_path_a = f"{save_dir}/simulation_i{time_steps}_kg{kg}_params.png"
fig1.savefig(output_path_a, dpi=300)
print(f"Saved: {output_path_a}")

# Plot (b): Error evolution for each edge over time
fig2, ax2 = plt.subplots(figsize=(7, 5))

for k in range(n_edges):
    u_label = node_list[edges[k][0]]
    v_label = node_list[edges[k][1]]
    ax2.plot(time_axis, error_history[:, k], label=f'Edge ({u_label}, {v_label})', lw=1.5)

ax2.set_yscale('log')
ax2.set_xlabel('Iteration (k)')
ax2.set_ylabel('Absolute Error (log scale)')
ax2.grid(True, linestyle=':')
#ax2.legend(loc='upper right', fontsize='small', ncol=2)

fig2.tight_layout()

# Save the image of the results in the "results" directory
output_path_b = f"{save_dir}/simulation_i{time_steps}_kg{kg}_errors.png"
fig2.savefig(output_path_b, dpi=300)
print(f"Saved: {output_path_b}")

plt.show()