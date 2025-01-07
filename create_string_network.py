#!/usr/bin/env python3

import pandas as pd
import requests
import json
from pathlib import Path
import sys

def get_string_network_png(genes, species=10090, score_threshold=700):
    """Get network visualization as PNG from STRING."""
    string_api_url = "https://version-12-0.string-db.org/api"
    output_format = "image"
    method = "network"

    request_url = "/".join([string_api_url, output_format, method])

    params = {
        "identifiers": "\r".join(genes),  # your protein list
        "species": species,  # species NCBI identifier 
        "required_score": score_threshold,  # threshold of significance
        "network_flavor": "confidence",  # show confidence links
        "block_structure_pics_in_bubbles": 1,
        "hide_disconnected_nodes": 1,
        "hide_edge_labels": 1,
        "show_query_only": 1
    }

    try:
        response = requests.post(request_url, data=params)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error getting network PNG: {e}", file=sys.stderr)
        return None

def get_enrichment_figure(genes, species=10090, category="Process"):
    """Get enrichment figure from STRING."""
    string_api_url = "https://version-12-0.string-db.org/api"
    output_format = "image"
    method = "enrichmentfigure"

    request_url = "/".join([string_api_url, output_format, method])

    params = {
        "identifiers": "\r".join(genes),
        "species": species,
        "caller_identity": "topic_analysis",
        "group_by_similarity": 0.8,
        "x_axis": 'FDR',
        "category": category,
        "color_palette": "yellow_pink",
    }

    try:
        response = requests.post(request_url, data=params)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error getting enrichment figure: {e}", file=sys.stderr)
        return None

def process_topic_genes(csv_file, topic_num):
    """Process genes for a specific topic from the CSV file."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"Loaded CSV file. Columns found: {df.columns.tolist()}", file=sys.stderr)
        
        # Try different possible column names
        topic_col = None
        gene_col = None
        score_col = None
        
        # Check for topic column
        topic_candidates = ['topic', 'Topic', 'TOPIC']
        for col in topic_candidates:
            if col in df.columns:
                topic_col = col
                break
        
        # Check for gene column
        gene_candidates = ['gene', 'Gene', 'GENE', 'name', 'Name', 'NAME']
        for col in gene_candidates:
            if col in df.columns:
                gene_col = col
                break
                
        # Check for score column
        score_candidates = ['score', 'Score', 'SCORE']
        for col in score_candidates:
            if col in df.columns:
                score_col = col
                break
        
        if topic_col is None:
            raise ValueError(f"Could not find topic column. Available columns: {df.columns.tolist()}")
        if gene_col is None:
            raise ValueError(f"Could not find gene column. Available columns: {df.columns.tolist()}")
            
        print(f"Using columns: topic='{topic_col}', gene='{gene_col}'", file=sys.stderr)
        
        # Filter for the specific topic and sort by score if available
        topic_df = df[df[topic_col] == topic_num]
        if score_col:
            topic_df = topic_df.sort_values(score_col, ascending=False)
        
        topic_genes = topic_df[gene_col].tolist()
        print(f"Found {len(topic_genes)} genes for topic {topic_num}", file=sys.stderr)
        
        if not topic_genes:
            print(f"Warning: No genes found for topic {topic_num}. Available topics: {sorted(df[topic_col].unique())}", file=sys.stderr)
            return None
        
        # Create output directory
        output_dir = Path("Perturb-seq_manuscript/topic_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save gene list
        gene_list_file = output_dir / f"topic{topic_num}_genes.txt"
        with open(gene_list_file, 'w') as f:
            for gene in topic_genes:
                f.write(f"{gene}\n")
        print(f"Gene list saved to {gene_list_file}", file=sys.stderr)
        
        # Get network PNG
        network_data = get_string_network_png(topic_genes)
        if network_data:
            network_file = output_dir / f"topic{topic_num}_network.png"
            with open(network_file, 'wb') as f:
                f.write(network_data)
            print(f"Network image saved to {network_file}")
        
        # Get Process enrichment figure
        process_data = get_enrichment_figure(topic_genes, category="Process")
        if process_data:
            process_file = output_dir / f"topic{topic_num}_process.png"
            with open(process_file, 'wb') as f:
                f.write(process_data)
            print(f"Process enrichment saved to {process_file}")
            
        # Get KEGG enrichment figure
        kegg_data = get_enrichment_figure(topic_genes, category="KEGG")
        if kegg_data:
            kegg_file = output_dir / f"topic{topic_num}_kegg.png"
            with open(kegg_file, 'wb') as f:
                f.write(kegg_data)
            print(f"KEGG enrichment saved to {kegg_file}")
            
        return True
            
    except Exception as e:
        print(f"Error processing topic {topic_num}: {str(e)}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_string_network.py <csv_file> <topic_number>")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    topic_num = int(sys.argv[2])
    process_topic_genes(csv_file, topic_num) 