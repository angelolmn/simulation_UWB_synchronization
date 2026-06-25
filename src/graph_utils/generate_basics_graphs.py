import os
import networkx as nx
import argparse

parser = argparse.ArgumentParser(description="Generate basic graphs (Kn and Pn) from 2 to n-max nodes and save them in GraphML format.")

parser.add_argument("-n","--n-max", type=int, default=6, help="Maximum number of nodes for generated Kn and Pn graphs (Default: 6)")

args = parser.parse_args()

graph_dir = "graphs"
os.makedirs(graph_dir, exist_ok=True)

Kn = nx.complete_graph(2)
ruta_k = os.path.join(graph_dir, f"k{2}.graphml")
nx.write_graphml(Kn, ruta_k)
print(f"Guardado: {ruta_k:<22} | Nodos: {2:<2} | Aristas: {Kn.number_of_edges()}")

for n in range(3, args.n_max + 1):
    # Kn Graph
    Kn = nx.complete_graph(n)
    ruta_k = os.path.join(graph_dir, f"k{n}.graphml")
    nx.write_graphml(Kn, ruta_k)
    print(f"Guardado: {ruta_k:<22} | Nodos: {n:<2} | Aristas: {Kn.number_of_edges()}")

    # Pn Graph
    Pn = nx.path_graph(n)
    ruta_p = os.path.join(graph_dir, f"p{n}.graphml")
    nx.write_graphml(Pn, ruta_p)
    print(f"Guardado: {ruta_p:<22} | Nodos: {n:<2} | Aristas: {Pn.number_of_edges()}")
