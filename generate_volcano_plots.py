#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os
from adjustText import adjust_text
from matplotlib.ticker import ScalarFormatter
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

def create_volcano_plot(df_topic, topic_id, output_dir):
    """Create a publication-quality volcano plot for a specific topic."""
    # Create figure
    plt.figure(figsize=(8, 7))
    
    # Calculate -log10(p-value)
    df_topic.loc[:, 'neg_log10_p'] = -np.log10(df_topic['p_value'])
    
    # Set significance thresholds
    p_threshold = -np.log10(0.05)  # -log10(0.05)
    fc_threshold = 0.5  # log2 fold change threshold
    
    # Create the scatter plot for non-significant points
    plt.scatter(df_topic[~df_topic['significant']]['log_2_fold_change'], 
               df_topic[~df_topic['significant']]['neg_log10_p'],
               alpha=0.4,
               s=40,
               c='#404040',
               label='Not Significant')
    
    # Highlight significant points
    sig_points = df_topic[df_topic['significant']]
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
    
    # Add gene labels for significant points with text repulsion
    texts = []
    for _, row in sig_points.iterrows():
        texts.append(plt.text(row['log_2_fold_change'],
                            row['neg_log10_p'],
                            row['grna_target'],
                            fontsize=10,
                            alpha=0.8))
    
    # Adjust text positions to avoid overlaps
    adjust_text(texts,
               arrowprops=dict(arrowstyle='-', color='grey', alpha=0.5),
               expand_points=(1.5, 1.5))
    
    # Customize the plot
    plt.xlabel('log$_2$(Fold Change)', fontsize=12, labelpad=10)
    plt.ylabel('-log$_{10}$(p-value)', fontsize=12, labelpad=10)
    plt.title(f'Topic {topic_id} Perturbation Effects', fontsize=14, pad=15)
    
    # Add gridlines
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot with high DPI
    output_path = os.path.join(output_dir, f'topic{topic_id}_volcano.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    # Also save as PDF for publication
    pdf_path = os.path.join(output_dir, f'topic{topic_id}_volcano.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    
    plt.close()
    
    # Generate statistics
    n_total = len(df_topic)
    n_sig = len(sig_points)
    n_up = len(sig_points[sig_points['log_2_fold_change'] > 0])
    n_down = len(sig_points[sig_points['log_2_fold_change'] < 0])
    
    stats = {
        'topic': topic_id,
        'total_genes': n_total,
        'significant_genes': n_sig,
        'upregulated': n_up,
        'downregulated': n_down
    }
    
    return output_path, stats

def main():
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # Read the data
    data_path = os.path.join(parent_dir, 'FP_moi15_thresho20_60k_-celltype_default.csv')
    print(f'Reading data from: {data_path}')
    df = pd.read_csv(data_path)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(script_dir, 'volcano_plots')
    os.makedirs(output_dir, exist_ok=True)
    print(f'Saving plots to: {output_dir}')
    
    # Store statistics for all topics
    all_stats = []
    
    # Process each topic
    for topic_id in range(1, 61):  # Topics 1-60
        topic_data = df[df['response_id'] == f'X{topic_id}'].copy()  # Create copy to avoid warning
        if not topic_data.empty:
            print(f'Generating volcano plot for Topic {topic_id}...')
            _, stats = create_volcano_plot(topic_data, topic_id, output_dir)
            all_stats.append(stats)
        else:
            print(f'No data found for Topic {topic_id}')
    
    # Save statistics to CSV
    stats_df = pd.DataFrame(all_stats)
    stats_path = os.path.join(output_dir, 'volcano_plot_statistics.csv')
    stats_df.to_csv(stats_path, index=False)
    print(f'Statistics saved to: {stats_path}')
    
    print('Volcano plots generation complete!')

if __name__ == '__main__':
    main() 