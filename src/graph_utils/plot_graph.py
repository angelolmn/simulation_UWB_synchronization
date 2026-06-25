import os
import networkx as nx
import argparse
import matplotlib.pyplot as plt 

parser = argparse.ArgumentParser(description="Plot a graph from a GraphML file using NetworkX and Matplotlib.")

parser.add_argument("-f","--file", type=str, required=True, help="Path to the graph file to plot")

args = parser.parse_args()

if not os.path.exists(args.file):
    print(f"Error: The file '{args.file}' does not exist.")
    exit(1)

G = nx.read_graphml(args.file)

fig, ax = plt.subplots(figsize=(6, 6))

pos = nx.circular_layout(G)

nx.draw(
    G, pos, ax=ax,
    with_labels=True,
    node_color="steelblue",
    edge_color="gray",
    node_size=800,
    font_color="white",
    font_size=12,
)

plt.show()