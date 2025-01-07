#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os
from adjustText import adjust_text
import matplotlib as mpl

# Set publication style
plt.style.use(['seaborn-v0_8-paper', 'seaborn-v0_8-deep'])
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial']
mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.linewidth'] = 1.5
mpl.rcParams['xtick.major.width'] = 1.5
mpl.rcParams['ytick.major.width'] = 1.5
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['ytick.major.size'] = 5

def create_gene_volcano_plot(df_gene, gene_name, output_dir):
    """Create a publication-quality volcano plot for a specific gene."""
    # Create figure
    plt.figure(figsize=(8, 7))
    
    # Calculate -log10(p-value)
    df_gene.loc[:, 'neg_log10_p'] = -np.log10(df_gene['p_value'])
    
    # Set significance thresholds
    p_threshold = -np.log10(0.05)  # -log10(0.05)
    fc_threshold = 0.5  # log2 fold change threshold
    
    # Create the scatter plot for non-significant points
    plt.scatter(df_gene[~df_gene['significant']]['log_2_fold_change'], 
               df_gene[~df_gene['significant']]['neg_log10_p'],
               alpha=0.4,
               s=40,
               c='#404040',
               label='Not Significant')
    
    # Highlight significant points
    sig_points = df_gene[df_gene['significant']]
    colors = np.where(sig_points['log_2_fold_change'] > 0, '#d62728', '#1f77b4')
    plt.scatter(sig_points['log_2_fold_change'],
               sig_points['neg_log10_p'],
               alpha=0.7,
               s=50,
               c=colors)
    
    # Add significance threshold lines
    plt.axhline(y=p_threshold, color='grey', linestyle='--', alpha=0.3)
    plt.axvline(x=fc_threshold, color='grey', linestyle='--', alpha=0.3)
    plt.axvline(x=-fc_threshold, color='grey', linestyle='--', alpha=0.3)
    
    # Add topic labels for significant points with text repulsion
    texts = []
    for _, row in sig_points.iterrows():
        topic_num = row['response_id'].replace('X', '')
        texts.append(plt.text(row['log_2_fold_change'],
                            row['neg_log10_p'],
                            f'Topic {topic_num}',
                            fontsize=10,
                            alpha=0.8))
    
    # Adjust text positions to avoid overlaps
    if texts:  # Only adjust if there are texts to adjust
        adjust_text(texts,
                   arrowprops=dict(arrowstyle='-', color='grey', alpha=0.5),
                   expand_points=(1.5, 1.5))
    
    # Customize the plot
    plt.xlabel('log$_2$(Fold Change)', fontsize=12, labelpad=10)
    plt.ylabel('-log$_{10}$(p-value)', fontsize=12, labelpad=10)
    plt.title(f'Gene: {gene_name} Effects on Topics', fontsize=14, pad=15)
    
    # Add gridlines
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot with high DPI
    output_path = os.path.join(output_dir, f'{gene_name}_volcano.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    # Also save as PDF for publication
    pdf_path = os.path.join(output_dir, f'{gene_name}_volcano.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    
    plt.close()
    
    # Generate statistics
    n_total = len(df_gene)
    n_sig = len(sig_points)
    n_up = len(sig_points[sig_points['log_2_fold_change'] > 0])
    n_down = len(sig_points[sig_points['log_2_fold_change'] < 0])
    
    stats = {
        'gene': gene_name,
        'total_topics': n_total,
        'significant_topics': n_sig,
        'upregulated_topics': n_up,
        'downregulated_topics': n_down
    }
    
    return output_path, stats

def main():
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    data_path = os.path.join(parent_dir, 'FP_moi15_thresho20_60k_-celltype_default.csv')
    output_dir = os.path.join(script_dir, 'gene_volcano_plots')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    # Load data
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows of data")
    
    # Get unique genes
    genes = df['grna_target'].unique()
    print(f"Found {len(genes)} unique genes")
    
    # Store statistics for all genes
    all_stats = []
    
    # Process each gene
    for gene_name in genes:
        print(f"Generating volcano plot for gene: {gene_name}")
        gene_data = df[df['grna_target'] == gene_name].copy()
        _, stats = create_gene_volcano_plot(gene_data, gene_name, output_dir)
        all_stats.append(stats)
    
    # Save statistics to CSV
    stats_df = pd.DataFrame(all_stats)
    stats_path = os.path.join(output_dir, 'gene_volcano_statistics.csv')
    stats_df.to_csv(stats_path, index=False)
    print(f"Statistics saved to: {stats_path}")
    
    print("Gene volcano plots generation complete!")

if __name__ == '__main__':
    main() 