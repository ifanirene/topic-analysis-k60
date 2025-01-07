#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os
from adjustText import adjust_text

# Set publication style
plt.style.use(['seaborn-v0_8-paper', 'seaborn-v0_8-deep'])
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 12

def load_data(topic_data_path, knockdown_data_path):
    """Load and preprocess both datasets."""
    print("Loading data...")
    
    # Load topic perturbation data
    topic_df = pd.read_csv(topic_data_path)
    print(f"Loaded {len(topic_df)} topic perturbation measurements")
    
    # Load knockdown efficiency data
    kd_df = pd.read_csv(knockdown_data_path)
    print(f"Loaded {len(kd_df)} knockdown efficiency measurements")
    
    return topic_df, kd_df

def analyze_gene_impact(topic_df):
    """Calculate overall impact metrics for each gene."""
    # Count significant effects per gene
    gene_impact = topic_df[topic_df['significant']].groupby('grna_target').agg({
        'response_id': 'count',  # Number of topics affected
        'log_2_fold_change': ['mean', 'std', 'min', 'max']  # Effect size statistics
    }).round(3)
    
    gene_impact.columns = ['n_topics_affected', 'mean_effect', 'effect_std', 'min_effect', 'max_effect']
    return gene_impact

def create_efficiency_impact_plot(gene_impact, kd_df, output_dir):
    """Create scatter plot of knockdown efficiency vs. gene impact."""
    # Merge knockdown efficiency with gene impact
    merged_df = gene_impact.merge(kd_df[['grna_target', 'log_2_fold_change', 'significant']], 
                                left_index=True, 
                                right_on='grna_target')
    
    # Rename columns for clarity
    merged_df = merged_df.rename(columns={
        'log_2_fold_change': 'knockdown_efficiency',
        'significant': 'significant_knockdown'
    })
    
    # Create figure
    plt.figure(figsize=(12, 10))
    
    # Create scatter plot
    sns.scatterplot(data=merged_df,
                   x='knockdown_efficiency',
                   y='n_topics_affected',
                   hue='significant_knockdown',
                   size='effect_std',
                   sizes=(50, 200),
                   alpha=0.7)
    
    # Add gene labels for top impactful genes with text repulsion
    top_genes = merged_df.nlargest(30, 'n_topics_affected')
    texts = []
    for _, row in top_genes.iterrows():
        texts.append(plt.text(row['knockdown_efficiency'],
                            row['n_topics_affected'],
                            row['grna_target'],
                            fontsize=10,
                            alpha=0.8))
    
    # Adjust text positions to avoid overlaps
    adjust_text(texts,
               arrowprops=dict(arrowstyle='-', color='grey', alpha=0.5),
               expand_points=(1.5, 1.5),
               force_points=(0.5, 0.5))
    
    # Customize plot
    plt.xlabel('Knockdown Efficiency (log2 fold change)', fontsize=12)
    plt.ylabel('Number of Topics Affected', fontsize=12)
    plt.title('Gene Knockdown Efficiency vs. Topic Impact', fontsize=14, pad=15)
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'efficiency_vs_impact.pdf')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def create_effect_size_plot(gene_impact, kd_df, output_dir):
    """Create scatter plot of knockdown efficiency vs. effect size."""
    # Merge data
    merged_df = gene_impact.merge(kd_df[['grna_target', 'log_2_fold_change', 'significant']], 
                                left_index=True, 
                                right_on='grna_target')
    
    # Rename columns
    merged_df = merged_df.rename(columns={
        'log_2_fold_change': 'knockdown_efficiency',
        'significant': 'significant_knockdown'
    })
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Create scatter plot
    sns.scatterplot(data=merged_df,
                   x='knockdown_efficiency',
                   y='mean_effect',
                   hue='significant_knockdown',
                   size='n_topics_affected',
                   sizes=(50, 200),
                   alpha=0.7)
    
    # Add gene labels for extreme effects
    extreme_genes = pd.concat([
        merged_df.nsmallest(5, 'mean_effect'),
        merged_df.nlargest(5, 'mean_effect')
    ])
    
    for _, row in extreme_genes.iterrows():
        plt.annotate(row['grna_target'],
                    (row['knockdown_efficiency'], row['mean_effect']),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=10,
                    alpha=0.8)
    
    # Customize plot
    plt.xlabel('Knockdown Efficiency (log2 fold change)', fontsize=12)
    plt.ylabel('Mean Effect Size', fontsize=12)
    plt.title('Gene Knockdown Efficiency vs. Effect Size', fontsize=14, pad=15)
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'efficiency_vs_effect_size.pdf')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def calculate_correlations(gene_impact, kd_df):
    """Calculate correlations between knockdown efficiency and impact metrics."""
    # Merge data
    merged_df = gene_impact.merge(kd_df[['grna_target', 'log_2_fold_change']], 
                                left_index=True, 
                                right_on='grna_target')
    
    # Calculate correlations
    correlations = {
        'n_topics_vs_efficiency': merged_df['n_topics_affected'].corr(merged_df['log_2_fold_change']),
        'mean_effect_vs_efficiency': merged_df['mean_effect'].corr(merged_df['log_2_fold_change']),
        'effect_std_vs_efficiency': merged_df['effect_std'].corr(merged_df['log_2_fold_change'])
    }
    
    return correlations

def main():
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    topic_data_path = os.path.join(parent_dir, 'FP_moi15_thresho20_60k_-celltype_default.csv')
    knockdown_data_path = os.path.join(parent_dir, 'FP_moi15_knockdown_efficiency_sceptre.csv')
    
    output_dir = os.path.join(script_dir, 'knockdown_analysis')
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    topic_df, kd_df = load_data(topic_data_path, knockdown_data_path)
    
    # Analyze gene impact
    gene_impact = analyze_gene_impact(topic_df)
    
    # Create visualizations
    create_efficiency_impact_plot(gene_impact, kd_df, output_dir)
    create_effect_size_plot(gene_impact, kd_df, output_dir)
    
    # Calculate correlations
    correlations = calculate_correlations(gene_impact, kd_df)
    
    # Save results
    gene_impact.to_csv(os.path.join(output_dir, 'gene_impact_metrics.csv'))
    pd.DataFrame([correlations]).to_csv(os.path.join(output_dir, 'efficiency_correlations.csv'))
    
    # Print summary
    print("\nAnalysis Summary:")
    print("-----------------")
    print(f"Total genes analyzed: {len(gene_impact)}")
    print("\nCorrelations with knockdown efficiency:")
    for metric, corr in correlations.items():
        print(f"{metric}: {corr:.3f}")

if __name__ == '__main__':
    main() 