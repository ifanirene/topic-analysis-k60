#!/usr/bin/env python3

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import scipy.cluster.hierarchy as hierarchy
from matplotlib.colors import LinearSegmentedColormap

# Set publication style
plt.style.use(['seaborn-v0_8-paper', 'seaborn-v0_8-deep'])
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 12

def load_ucell_data(file_path):
    """Load and process UCell score data."""
    df = pd.read_csv(file_path)
    
    # Filter for artery and pre-artery responses
    arterial_df = df[df['response_id'].isin(['artery', 'pre-art']) & df['significant']].copy()
    
    # Pivot to get gene x cell type matrix of log2FC
    pivot_df = arterial_df.pivot(index='grna_target', 
                                columns='response_id', 
                                values=['log_2_fold_change', 'p_value'])
    
    # Flatten column names
    pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]
    
    return pivot_df, arterial_df

def load_topic_data(topic_dir, sig_genes):
    """Load topic analysis data for significant genes."""
    topic_file = topic_dir / 'FP_moi15_thresho20_60k_-celltype_default.csv'
    topic_df = pd.read_csv(topic_file)
    
    # Filter for significant genes and create topic matrix
    topic_df = topic_df[topic_df['grna_target'].isin(sig_genes)].copy()
    
    # Create matrix of topic effects
    topic_matrix = pd.pivot_table(
        topic_df,
        values='log_2_fold_change',
        index='grna_target',
        columns='response_id',
        fill_value=0
    )
    
    # Create matrix of significance
    sig_matrix = pd.pivot_table(
        topic_df,
        values='significant',
        index='grna_target',
        columns='response_id',
        fill_value=False
    )
    
    return topic_matrix, sig_matrix

def create_custom_cmap():
    """Create a custom colormap with stronger saturation."""
    colors = ['#0000FF', '#FFFFFF', '#FF0000']  # Blue to White to Red
    return LinearSegmentedColormap.from_list('custom_diverging', colors)

def plot_clustered_heatmap(effect_matrix, significance_matrix, ucell_data, output_dir, topic_range=None):
    """Generate a clustered heatmap with significance annotations."""
    # Subset the matrices if topic_range is provided
    if topic_range is not None:
        start, end = topic_range
        effect_matrix = effect_matrix.iloc[:, start-1:end]
        significance_matrix = significance_matrix.iloc[:, start-1:end]
        output_suffix = f"_{start}-{end}"
    else:
        output_suffix = ""
    
    # Set up the figure
    plt.figure(figsize=(20, 12))
    
    # Compute hierarchical clustering
    row_linkage = hierarchy.linkage(effect_matrix, method='ward')
    col_linkage = hierarchy.linkage(effect_matrix.T, method='ward')
    
    # Get the maximum absolute value for symmetric color scaling
    max_abs_val = max(abs(effect_matrix.values.min()), abs(effect_matrix.values.max()))
    vmin, vmax = -max_abs_val, max_abs_val
    
    # Create custom colormap
    custom_cmap = create_custom_cmap()
    
    # Create clustered heatmap
    g = sns.clustermap(
        effect_matrix,
        row_linkage=row_linkage,
        col_linkage=col_linkage,
        center=0,
        cmap=custom_cmap,
        vmin=vmin,
        vmax=vmax,
        figsize=(20, 12),
        xticklabels=True,
        yticklabels=True,
        cbar_pos=(0.02, 0.8, 0.03, 0.2),
        dendrogram_ratio=(.1, .2),
        cbar_kws={'label': 'log2 Fold Change'}
    )
    
    # Add significance markers
    row_idx = g.dendrogram_row.reordered_ind
    col_idx = g.dendrogram_col.reordered_ind
    
    for i, row in enumerate(row_idx):
        for j, col in enumerate(col_idx):
            if significance_matrix.iloc[row, col]:
                x = j + 0.5
                y = i + 0.5
                g.ax_heatmap.text(x, y, '*', 
                                ha='center', va='center', 
                                color='black', fontsize=8)
    
    # Color gene labels based on arterial effect
    yticks = g.ax_heatmap.get_yticklabels()
    for tick in yticks:
        gene = tick.get_text()
        artery_effect = ucell_data.loc[gene, 'artery_log_2_fold_change']
        color = '#FF4B4B' if artery_effect > 0 else '#4B4BFF'
        tick.set_color(color)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#FF4B4B', label='Increases artery score'),
        Patch(facecolor='#4B4BFF', label='Decreases artery score')
    ]
    g.fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Save plot
    plt.savefig(output_dir / f'artery_genes_topic_heatmap{output_suffix}.pdf', 
                bbox_inches='tight', dpi=300)
    plt.close()

def analyze_arterial_genes(ucell_file, topic_dir, output_dir):
    """Analyze genes affecting arterial identity."""
    # Load UCell data
    ucell_df, raw_ucell = load_ucell_data(ucell_file)
    sig_genes = ucell_df.index.tolist()
    
    # Load topic data
    topic_matrix, sig_matrix = load_topic_data(topic_dir, sig_genes)
    
    # Generate heatmaps
    print("Generating full heatmap...")
    plot_clustered_heatmap(topic_matrix, sig_matrix, ucell_df, output_dir)
    
    print("Generating subset heatmaps...")
    plot_clustered_heatmap(topic_matrix, sig_matrix, ucell_df, output_dir, topic_range=(1, 27))
    plot_clustered_heatmap(topic_matrix, sig_matrix, ucell_df, output_dir, topic_range=(28, 55))
    
    # Save processed data
    ucell_df.to_csv(output_dir / 'arterial_genes_data.csv')
    topic_matrix.to_csv(output_dir / 'topic_effects.csv')
    
    return sig_genes

def main():
    # Set up paths
    script_dir = Path(__file__).parent
    ucell_file = script_dir.parent / 'FP_moi15_UCell_score_discovery.csv'
    output_dir = script_dir / 'analysis_results'
    output_dir.mkdir(exist_ok=True)
    
    # Run analysis
    sig_genes = analyze_arterial_genes(ucell_file, script_dir.parent, output_dir)
    
    print(f"Analysis complete. Found {len(sig_genes)} significant genes.")
    print(f"Results saved in {output_dir}")

if __name__ == "__main__":
    main() 