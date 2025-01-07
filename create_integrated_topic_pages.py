import os
from pathlib import Path
import markdown
import base64
from pdf2image import convert_from_path

def convert_pdf_to_png(pdf_path, output_dir):
    """Convert PDF to PNG using poppler."""
    try:
        # Convert the first page of the PDF to PNG
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if images:
            output_path = output_dir / f"{pdf_path.stem}.png"
            images[0].save(str(output_path), 'PNG')
            return output_path
        return None
    except Exception as e:
        print(f"Error converting PDF to PNG: {str(e)}")
        return None

def read_markdown_file(file_path):
    """Read and convert markdown file to HTML."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return markdown.markdown(content)
    except FileNotFoundError:
        print(f"Warning: Markdown file not found: {file_path}")
        return "<p>Markdown content not available</p>"
    except Exception as e:
        print(f"Error reading markdown file {file_path}: {str(e)}")
        return "<p>Error reading markdown content</p>"

def embed_image(image_path):
    """Embed image file as base64 in HTML."""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_type = image_path.suffix[1:]  # Remove the dot from extension
            base64_image = base64.b64encode(image_data).decode()
            return f'<img src="data:image/{image_type};base64,{base64_image}" style="max-width:100%; height:auto; margin:10px 0;">'
    except FileNotFoundError:
        print(f"Warning: Image file not found: {image_path}")
        return f"<p class='error-message'>Image not found: {image_path}</p>"
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return f"<p class='error-message'>Error processing image: {image_path}</p>"

def create_topic_page(topic_num, base_dir):
    """Create an integrated HTML page for a topic."""
    print(f"Processing Topic {topic_num}...")
    
    # Define paths
    md_file = base_dir / f"topic{topic_num}_analysis.md"
    network_image = base_dir / f"topic{topic_num}_network.png"
    process_image = base_dir / f"topic{topic_num}_process.png"
    kegg_image = base_dir / f"topic{topic_num}_kegg.png"
    volcano_pdf = base_dir / "volcano_plots" / f"topic{topic_num}_volcano.pdf"
    output_file = base_dir / f"topic{topic_num}_integrated.html"
    
    # Convert volcano PDF to PNG
    if volcano_pdf.exists():
        volcano_png = convert_pdf_to_png(volcano_pdf, base_dir / "volcano_plots")
    else:
        volcano_png = None
        print(f"Warning: Volcano PDF not found: {volcano_pdf}")
    
    print(f"Looking for files:")
    print(f"- Markdown: {md_file}")
    print(f"- Network: {network_image}")
    print(f"- Process: {process_image}")
    print(f"- KEGG: {kegg_image}")
    print(f"- Volcano: {volcano_png if volcano_png else volcano_pdf}")
    
    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Topic {topic_num} Analysis</title>
        <style>
            :root {{
                --primary-color: #2c3e50;
                --secondary-color: #34495e;
                --accent-color: #3498db;
                --background-color: #f5f6fa;
                --text-color: #2c3e50;
            }}
            
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .content {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 30px;
            }}
            
            .markdown-content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .visualization-grid {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 30px;
            }}
            
            .network-section {{
                grid-column: 1 / -1;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .analysis-section {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            
            .visualization {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            
            h1, h2, h3 {{
                color: var(--primary-color);
            }}
            
            h2 {{
                margin-top: 0;
                padding-bottom: 10px;
                border-bottom: 2px solid var(--accent-color);
            }}
            
            img {{
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            
            img:hover {{
                transform: scale(1.02);
            }}
            
            .error-message {{
                color: #e74c3c;
                padding: 10px;
                background: #fde8e8;
                border-radius: 4px;
                margin: 10px 0;
            }}
            
            @media (max-width: 1200px) {{
                .analysis-section {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <div class="markdown-content">
                    <h1>Topic {topic_num} Analysis</h1>
                    {markdown_content}
                </div>
                
                <div class="visualization-grid">
                    <div class="network-section">
                        <h2>Network Analysis</h2>
                        {network_image}
                    </div>
                    
                    <div class="analysis-section">
                        <div class="visualization">
                            <h2>Process Analysis</h2>
                            {process_image}
                        </div>
                        <div class="visualization">
                            <h2>KEGG Pathways</h2>
                            {kegg_image}
                        </div>
                    </div>
                    
                    <div class="visualization">
                        <h2>Differential Expression</h2>
                        {volcano_plot}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Get content
    markdown_content = read_markdown_file(md_file)
    network_content = embed_image(network_image)
    process_content = embed_image(process_image)
    kegg_content = embed_image(kegg_image)
    volcano_content = embed_image(volcano_png if volcano_png else volcano_pdf)
    
    # Create HTML
    html_content = html_template.format(
        topic_num=topic_num,
        markdown_content=markdown_content,
        network_image=network_content,
        process_image=process_content,
        kegg_image=kegg_content,
        volcano_plot=volcano_content
    )
    
    # Save file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Created {output_file}")
    return output_file

def process_topics(base_dir, topic_numbers):
    """Process multiple topics and generate HTML pages."""
    base_dir = Path(base_dir)
    results = []
    
    for topic_num in topic_numbers:
        try:
            output_file = create_topic_page(topic_num, base_dir)
            results.append(f"Successfully created {output_file}")
        except Exception as e:
            results.append(f"Error processing topic {topic_num}: {str(e)}")
    
    return results

if __name__ == "__main__":
    # Test with a few topics
    base_dir = Path("/Users/fanxiaochen/cursor_rep/Perturb-seq_manuscript/topic_analysis")
    topic_numbers = [24, 25, 39]  # Test with topics we know have content
    results = process_topics(base_dir, topic_numbers)
    
    print("\nSummary:")
    for result in results:
        print(result) 