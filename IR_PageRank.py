"""
PageRank Algorithm
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Define link structure
links = {
    'A': ['B', 'C'],
    'B': ['C'],
    'C': ['A'],
    'D': ['C']
}

# Get pages and initialize variables
pages = list(links.keys())
n = len(pages)

# Create transition matrix M
M = np.zeros((n, n))
for i, p in enumerate(pages):
    for q in links[p]:
        j = pages.index(q)
        M[j][i] = 1 / len(links[p])  # column-stochastic matrix

# PageRank parameters
d = 0.85
r = np.ones(n) / n #creates an array of all 1’s.divides each value by the total number of pages.
iterations = 100
epsilon = 1e-6

# Power iteration
for _ in range(iterations):
    new_r = (1 - d) / n + d * M.dot(r)
    if np.linalg.norm(new_r - r, 2) < epsilon:
        break
    r = new_r

# Display results
print("Final PageRank Scores:")
for i, p in enumerate(pages):
    print(f"Page {p}: {r[i]:.4f}")

# Visualization
G = nx.DiGraph()
for p, outlinks in links.items():
    for q in outlinks:
        G.add_edge(p, q)

pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightblue', arrows=True, node_size=2000)
plt.title("Page Link Graph")
plt.show()
