import os
import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Plot Control Law Simulation results.")

parser.add_argument("-g", "--graph", type=str, default="k4.graphml",
    help="GraphML file name used in the simulation (Default: 'k4.graphml').")

parser.add_argument("-i", "--iterations", type=int, default=100,
    help="Number of iterations used in the simulation (Default: 100).")

parser.add_argument("-k", "--gain", type=float, default=0.1,
    help="Proportional gain used in the simulation (Default: 0.1).")

parser.add_argument("--gamma", type=float, default=0.0,
    help="Integral gain used in the simulation (Default: 0.0).")

args = parser.parse_args()

save_dir = f"results/control_law_pi/{os.path.splitext(args.graph)[0]}/i{args.iterations}_k{args.gain}_gamma{args.gamma}"

params_path = f"{save_dir}/params.json"
errors_path = f"{save_dir}/errors.csv"

if not os.path.exists(params_path):
    print(f"Error: '{params_path}' does not exist. Please run the simulation first.")
    sys.exit(1)
if not os.path.exists(errors_path):
    print(f"Error: '{errors_path}' does not exist. Please run the simulation first.")
    sys.exit(1)

with open(params_path) as f:
    params = json.load(f)

data          = np.loadtxt(errors_path, delimiter=",", skiprows=1)
steps         = data[:, 0].astype(int)
x_history     = data[:, 1:-1]
error_history = data[:, -1]

node_list = params["nodes"]

plt.rcParams.update({
    'font.size':        13,
    'axes.labelsize':   13,
    'xtick.labelsize':  12,
    'ytick.labelsize':  12,
    'legend.fontsize':  12,
    'lines.linewidth':  2.0,
})

# Plot (a): Clock state
fig1, ax1 = plt.subplots(figsize=(7, 5))

for i, v in enumerate(node_list):
    ax1.plot(steps, x_history[:, i], label=f'Node {v}', lw=1.5)

ax1.set_xlabel('Iteration (k)')
ax1.set_ylabel('x(k)')
ax1.grid(True, linestyle=':')
ax1.legend()
fig1.tight_layout()
 
output_path_a = f"{save_dir}/simulation_i{args.iterations}_k{args.gain}_gamma{args.gamma}_clock.png"
fig1.savefig(output_path_a, dpi=300)
print(f"Saved: {output_path_a}")


# Plot (b): Clock diffs
fig2, ax2 = plt.subplots(figsize=(7, 5))

x_centered = x_history - x_history.mean(axis=1, keepdims=True)
for i, v in enumerate(node_list):
    ax2.plot(steps, x_centered[:, i], label=f'Node {v}', lw=1.5)

ax2.set_xlabel('Iteration (k)')
ax2.set_ylabel('x(k) - mean(x(k))')
ax2.grid(True, linestyle=':')
ax2.legend()
fig2.tight_layout()
 
output_path_b = f"{save_dir}/simulation_i{args.iterations}_k{args.gain}_gamma{args.gamma}_clockdiffs.png"
fig2.savefig(output_path_b, dpi=300)
print(f"Saved: {output_path_b}")

# Plot (c): Synchronization error norm
fig3, ax3 = plt.subplots(figsize=(7, 5))

ax3.plot(steps, error_history, color='steelblue', lw=1.5)
ax3.set_xlabel('Iteration (k)')
ax3.set_yscale('log')
ax3.set_ylabel('Error norm (log scale)')
ax3.grid(True, linestyle=':')
fig3.tight_layout()

output_path_c = f"{save_dir}/simulation_i{args.iterations}_k{args.gain}_gamma{args.gamma}_errors.png"
fig3.savefig(output_path_c, dpi=300)
print(f"Saved: {output_path_c}")
plt.show()