#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import subprocess

def generate_topic_pages(start_topic=1, end_topic=60):
    """Generate analysis pages for topics."""
    base_dir = Path(__file__).parent.absolute()
    
    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate network and enrichment data for each topic
    for topic in range(start_topic, end_topic + 1):
        print(f"\nProcessing Topic {topic}...")
        
        # Generate network and enrichment data
        cmd = [
            "python", 
            str(base_dir / "create_string_network.py"),
            str(base_dir.parent / "FB_combined_loading_gene_k60_top300.csv"),
            str(topic)
        ]
        subprocess.run(cmd)
        
        # Create HTML file from template
        template_path = base_dir / "topic1_direct.html"
        output_path = base_dir / f"topic{topic}_direct.html"
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Replace topic numbers and titles
            new_content = template.replace("Topic 1", f"Topic {topic}")
            new_content = new_content.replace("topic1", f"topic{topic}")
            
            with open(output_path, 'w') as f:
                f.write(new_content)
            print(f"Created {output_path}")
        else:
            print(f"Template file not found: {template_path}")

if __name__ == "__main__":
    generate_topic_pages() 