#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import fisher_exact
from scipy.cluster import hierarchy
import networkx as nx

def load_topic_genes(topic_num):
    """Load genes for a specific topic."""
    base_dir = Path(__file__).parent.absolute()
    gene_file = base_dir / f"topic{topic_num}_genes.txt"
    if gene_file.exists():
        with open(gene_file, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def calculate_gene_overlap():
    """Calculate gene overlap between topics."""
    topic_genes = {i: load_topic_genes(i) for i in range(1, 61)}
    n_topics = len(topic_genes)
    
    # Calculate overlap matrix
    overlap_matrix = np.zeros((n_topics, n_topics))
    jaccard_matrix = np.zeros((n_topics, n_topics))
    
    for i in range(n_topics):
        for j in range(n_topics):
            genes_i = topic_genes[i+1]
            genes_j = topic_genes[j+1]
            
            if not genes_i or not genes_j:
                continue
                
            intersection = len(genes_i & genes_j)
            union = len(genes_i | genes_j)
            
            overlap_matrix[i,j] = intersection
            jaccard_matrix[i,j] = intersection / union if union > 0 else 0
    
    return overlap_matrix, jaccard_matrix, topic_genes

def plot_overlap_heatmap(matrix, output_file, title):
    """Plot heatmap of topic relationships."""
    plt.figure(figsize=(20, 16))
    sns.set(font_scale=0.8)
    sns.heatmap(matrix, 
                annot=True, 
                fmt='.2f' if matrix.max() <= 1 else '.0f',
                cmap='YlOrRd',
                xticklabels=[f'{i}' for i in range(1, 61)],
                yticklabels=[f'{i}' for i in range(1, 61)],
                square=True)
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel('Topic Number', fontsize=12)
    plt.ylabel('Topic Number', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def create_topic_network(jaccard_matrix, threshold=0.1):
    """Create network visualization of topic relationships."""
    G = nx.Graph()
    
    # Add nodes
    for i in range(jaccard_matrix.shape[0]):
        G.add_node(i+1, name=f'{i+1}')
    
    # Add edges for similar topics
    for i in range(jaccard_matrix.shape[0]):
        for j in range(i+1, jaccard_matrix.shape[0]):
            if jaccard_matrix[i,j] >= threshold:
                G.add_edge(i+1, j+1, weight=jaccard_matrix[i,j])
    
    # Create visualization
    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    
    # Draw nodes
    node_sizes = [500 for _ in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=node_sizes, alpha=0.7)
    
    # Draw edges with width proportional to weight
    edge_weights = [G[u][v]['weight']*3 for u,v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.4)
    
    # Add labels with smaller font
    labels = {node: str(node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title('Topic Relationship Network', fontsize=14, pad=20)
    plt.axis('off')
    base_dir = Path(__file__).parent.absolute()
    plt.savefig(base_dir / 'topic_network.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_topic_relationships():
    """Analyze and visualize relationships between topics."""
    print("Analyzing topic relationships...")
    
    # Calculate overlap and similarity matrices
    overlap_matrix, jaccard_matrix, topic_genes = calculate_gene_overlap()
    
    # Create output directory
    base_dir = Path(__file__).parent.absolute()
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    plot_overlap_heatmap(overlap_matrix, 
                        base_dir / 'topic_overlap_heatmap.png',
                        'Gene Overlap Between Topics')
    
    plot_overlap_heatmap(jaccard_matrix,
                        base_dir / 'topic_jaccard_heatmap.png',
                        'Jaccard Similarity Between Topics')
    
    create_topic_network(jaccard_matrix)
    
    # Save numerical results
    results = {
        'overlap_matrix': overlap_matrix.tolist(),
        'jaccard_matrix': jaccard_matrix.tolist(),
        'topic_sizes': {i: len(genes) for i, genes in topic_genes.items()}
    }
    
    with open(base_dir / 'topic_relationships.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Analysis complete. Results saved in topic_analysis directory.")

if __name__ == "__main__":
    analyze_topic_relationships() 