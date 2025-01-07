#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def load_data(data_path):
    """Load and preprocess the perturbation data."""
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows of data")
    # Extract topic number from response_id
    df['topic'] = df['response_id'].str.extract('X(\d+)').astype(int)
    return df

def create_perturbation_heatmap(df, output_dir):
    """Create a heatmap of perturbation effects across topics."""
    print("Creating perturbation heatmap...")
    
    # Pivot data to create matrix of genes x topics
    pivot_df = df.pivot(index='grna_target', 
                       columns='topic',
                       values='log_2_fold_change')
    
    # Filter for genes that are significant in at least one topic
    sig_mask = df.pivot(index='grna_target', 
                       columns='topic',
                       values='significant')
    sig_genes = sig_mask.index[sig_mask.any(axis=1)]
    pivot_df = pivot_df.loc[sig_genes]
    
    print(f"Found {len(sig_genes)} genes with significant effects")
    
    # Create figure
    plt.figure(figsize=(20, 12))
    
    # Create heatmap
    g = sns.clustermap(pivot_df,
                      cmap='RdBu_r',
                      center=0,
                      vmin=-2, vmax=2,
                      xticklabels=True,
                      yticklabels=True,
                      dendrogram_ratio=(.1, .2),
                      cbar_pos=(.02, .32, .03, .2),
                      figsize=(20, 12))
    
    # Rotate x-axis labels
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha='right')
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
    
    g.fig.suptitle('Perturbation Effects Across Topics', y=1.02, fontsize=16)
    
    # Save plot
    output_path = os.path.join(output_dir, 'perturbation_heatmap.pdf')
    print(f"Saving heatmap to: {output_path}")
    g.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def analyze_gene_patterns(df):
    """Analyze patterns in gene perturbation effects."""
    print("Analyzing gene patterns...")
    # Count number of topics each gene affects
    gene_effects = df[df['significant']].groupby('grna_target').agg({
        'topic': 'count',
        'log_2_fold_change': ['mean', 'std']
    }).round(3)
    gene_effects.columns = ['n_topics_affected', 'mean_effect', 'effect_std']
    gene_effects = gene_effects.sort_values('n_topics_affected', ascending=False)
    
    return gene_effects

def create_topic_similarity_matrix(df, output_dir):
    """Create a similarity matrix between topics based on their perturbation profiles."""
    print("Creating topic similarity matrix...")
    
    # Create matrix of perturbation effects
    pivot_df = df.pivot(index='topic', 
                       columns='grna_target',
                       values='log_2_fold_change').fillna(0)
    
    # Calculate correlation matrix
    corr_matrix = pivot_df.corr()
    
    # Plot correlation matrix
    plt.figure(figsize=(12, 10))
    g = sns.clustermap(corr_matrix,
                      cmap='RdBu_r',
                      center=0,
                      vmin=-1, vmax=1,
                      xticklabels=True,
                      yticklabels=True)
    
    # Rotate labels
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha='right')
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
    
    g.fig.suptitle('Topic Similarity Based on Perturbation Profiles', y=1.02, fontsize=16)
    
    # Save plot
    output_path = os.path.join(output_dir, 'topic_similarity_matrix.pdf')
    print(f"Saving similarity matrix to: {output_path}")
    g.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return corr_matrix

def analyze_topic_clusters(corr_matrix, threshold=0.7):
    """Identify clusters of related topics."""
    print("Analyzing topic clusters...")
    # Find highly correlated topic pairs
    high_corr = np.where(np.triu(corr_matrix > threshold, k=1))
    topic_clusters = []
    
    for i, j in zip(*high_corr):
        topic_clusters.append({
            'topic1': corr_matrix.index[i],
            'topic2': corr_matrix.index[j],
            'correlation': corr_matrix.iloc[i, j]
        })
    
    return pd.DataFrame(topic_clusters)

def create_top_genes_barplot(gene_effects, output_dir, top_n=20):
    """Create a bar plot of the top genes affecting multiple topics."""
    print(f"Creating bar plot of top {top_n} genes...")
    
    plt.figure(figsize=(15, 8))
    top_genes = gene_effects.head(top_n)
    
    # Create bar plot
    sns.barplot(data=top_genes.reset_index(),
                x='grna_target',
                y='n_topics_affected',
                color='skyblue')
    
    # Customize plot
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Gene')
    plt.ylabel('Number of Topics Affected')
    plt.title(f'Top {top_n} Genes by Number of Topics Affected')
    
    # Save plot
    output_path = os.path.join(output_dir, 'top_genes_barplot.pdf')
    print(f"Saving bar plot to: {output_path}")
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    data_path = os.path.join(parent_dir, 'FP_moi15_thresho20_60k_-celltype_default.csv')
    output_dir = os.path.join(script_dir, 'analysis_results')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    # Load data
    df = load_data(data_path)
    
    # Generate visualizations and analyses
    create_perturbation_heatmap(df, output_dir)
    
    gene_patterns = analyze_gene_patterns(df)
    gene_patterns.to_csv(os.path.join(output_dir, 'gene_patterns.csv'))
    
    create_top_genes_barplot(gene_patterns, output_dir)
    
    corr_matrix = create_topic_similarity_matrix(df, output_dir)
    
    topic_clusters = analyze_topic_clusters(corr_matrix)
    topic_clusters.to_csv(os.path.join(output_dir, 'topic_clusters.csv'), index=False)
    
    print("Analysis complete! Results saved in:", output_dir)

if __name__ == '__main__':
    main() 