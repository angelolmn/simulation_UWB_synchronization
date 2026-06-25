import os
import sys
import json
import argparse
import numpy as np

parser = argparse.ArgumentParser(description="Verify Clock Rigidity Simulation results.")
parser.add_argument("-g", "--graph", type=str, default="k4.graphml",
    help="GraphML file name used in the simulation (Default: 'k4.graphml').")
parser.add_argument("-i", "--iterations", type=int, default=10000,
    help="Number of iterations used in the simulation (Default: 10000).")
parser.add_argument("-kg", "--gain", type=float, default=0.25,
    help="Gain parameter used in the simulation (Default: 0.25).")
args = parser.parse_args()

save_dir = f"results/clock_rigidity/{os.path.splitext(args.graph)[0]}/i{args.iterations}_kg{args.gain}"
params_path = f"{save_dir}/params.json"

if not os.path.exists(params_path):
    print(f"Error: '{params_path}' does not exist. Please run the simulation first.")
    sys.exit(1)

with open(params_path) as f:
    params = json.load(f)

alpha_true = np.array(params["alpha_true"])
beta_true   = np.array(params["beta_true"])
alpha_est   = np.array(params["alpha_est"])
beta_est    = np.array(params["beta_est"])

ks = np.mean(alpha_est / alpha_true)
k_beta = np.mean(beta_est - ks * beta_true)

alpha_var_trivial = ks * alpha_true
beta_var_trivial   = ks * beta_true + k_beta

error_alpha = np.linalg.norm(alpha_est - alpha_var_trivial)
error_beta  = np.linalg.norm(beta_est  - beta_var_trivial)

print("Trivial variation estimated.")
print(f"ks:    {ks:.6f}")
print(f"k_beta: {k_beta:.6f}")
print(f"Skew variation error  (alpha): {error_alpha:.2e}")
print(f"Offset variation error (beta): {error_beta:.2e}")