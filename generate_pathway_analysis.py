#!/usr/bin/env python3

import os
import pandas as pd
from pathlib import Path
import subprocess
import json

def read_gene_list(topic_num, base_dir):
    """Read genes for a specific topic."""
    gene_file = base_dir / f"topic{topic_num}_genes.txt"
    if gene_file.exists():
        with open(gene_file, 'r') as f:
            return [line.strip() for line in f]
    return []

def generate_claude_prompt(genes, topic_num):
    """Generate a prompt for Claude to analyze pathway enrichment."""
    prompt = f"""Analyze the following gene list from Topic {topic_num} and provide a comprehensive pathway analysis. 
Focus on biological functions, molecular pathways, and cellular processes.
Organize the analysis into these sections:
1. Key Pathway Components (with detailed subsections)
2. Functional Integration
3. Biological States
4. Clinical Relevance

Genes: {', '.join(genes)}

Format the response in HTML with proper headings and structure."""
    return prompt

def save_pathway_analysis(topic_num, analysis_text, base_dir):
    """Save the pathway analysis to an HTML file."""
    output_file = base_dir / f"topic{topic_num}_pathway_analysis.html"
    
    html_content = f"""
    <div class="pathway-analysis">
        <h3>Comprehensive Pathway Analysis for Topic {topic_num}</h3>
        {analysis_text}
    </div>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    return output_file

def run_claude_analysis(prompt):
    """Run Claude analysis using the LLM API."""
    cmd = [
        "python",
        "./tools/llm_api.py",
        "--prompt", prompt
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def process_topics(start_topic=1, end_topic=60):
    """Process pathway analysis for each topic."""
    base_dir = Path(__file__).parent.absolute()
    
    for topic in range(start_topic, end_topic + 1):
        print(f"\nProcessing Topic {topic}...")
        
        # Read genes
        genes = read_gene_list(topic, base_dir)
        if not genes:
            print(f"No genes found for topic {topic}")
            continue
            
        # Generate and run analysis
        prompt = generate_claude_prompt(genes, topic)
        analysis = run_claude_analysis(prompt)
        
        # Save results
        output_file = save_pathway_analysis(topic, analysis, base_dir)
        print(f"Analysis saved to {output_file}")
        
        # Update the topic's HTML file to include the pathway analysis
        topic_html = base_dir / f"topic{topic}_direct.html"
        if topic_html.exists():
            with open(topic_html, 'r') as f:
                content = f.read()
            
            # Find the position to insert the pathway analysis
            insert_pos = content.find('<div class="pathway-analysis">')
            if insert_pos != -1:
                # Replace the existing pathway analysis
                end_pos = content.find('</div>', insert_pos) + 6
                new_content = content[:insert_pos] + analysis + content[end_pos:]
            else:
                # Add new pathway analysis before the closing body tag
                insert_pos = content.find('</body>')
                new_content = content[:insert_pos] + analysis + content[insert_pos:]
            
            with open(topic_html, 'w') as f:
                f.write(new_content)
            print(f"Updated {topic_html}")

if __name__ == "__main__":
    process_topics() 