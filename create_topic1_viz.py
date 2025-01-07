import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
plt.figure(figsize=(15, 12))

# Create graph
G = nx.Graph()

# Define node categories and their colors
categories = {
    'Notch': '#FF9999',  # Red
    'VEGF': '#99FF99',   # Green
    'TF': '#9999FF',     # Blue
    'Metabolism': '#FFFF99',  # Yellow
    'ECM': '#FF99FF',    # Pink
    'Migration': '#99FFFF'  # Cyan
}

# Add nodes with categories
nodes = {
    'Dll4': 'Notch',
    'Notch1': 'Notch',
    'Hey1': 'Notch',
    'Adam10': 'Notch',
    'Flt1': 'VEGF',
    'Esm1': 'VEGF',
    'Angpt2': 'VEGF',
    'Flt4': 'VEGF',
    'Erg': 'TF',
    'Ets1': 'TF',
    'Wwtr1': 'TF',
    'Prdm1': 'TF',
    'Slc7a5': 'Metabolism',
    'Hmgcs2': 'Metabolism',
    'Pcx': 'Metabolism',
    'Scd2': 'Metabolism',
    'Cxcr4': 'Migration',
    'Sema6d': 'Migration',
    'Slit3': 'Migration',
    'Spock2': 'ECM',
    'Serpine2': 'ECM',
    'Vwf': 'ECM'
}

# Add nodes
for node, category in nodes.items():
    G.add_node(node, category=category)

# Add edges based on known interactions
edges = [
    ('Dll4', 'Notch1'),
    ('Notch1', 'Hey1'),
    ('Adam10', 'Notch1'),
    ('Flt1', 'Angpt2'),
    ('Erg', 'Flt4'),
    ('Ets1', 'Flt1'),
    ('Wwtr1', 'Erg'),
    ('Cxcr4', 'Migration'),
    ('Sema6d', 'Migration'),
    ('Spock2', 'ECM'),
    ('Serpine2', 'ECM'),
    ('Vwf', 'ECM'),
    ('Slc7a5', 'Metabolism'),
    ('Hmgcs2', 'Metabolism'),
    ('Pcx', 'Metabolism')
]

G.add_edges_from(edges)

# Set layout
pos = nx.spring_layout(G, k=1, iterations=50)

# Draw nodes
for category, color in categories.items():
    nodelist = [node for node, attr in G.nodes(data=True) 
               if attr.get('category') == category]
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=nodelist,
                          node_color=color,
                          node_size=2000,
                          alpha=0.7)

# Draw edges
nx.draw_networkx_edges(G, pos, alpha=0.5)

# Add labels
nx.draw_networkx_labels(G, pos, font_size=10)

# Add legend
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                            markerfacecolor=color, markersize=15, label=cat)
                  for cat, color in categories.items()]
plt.legend(handles=legend_elements, loc='upper left', fontsize=12)

# Set title
plt.title('Topic 1: Pathway Interactions in Arterial Development', 
          fontsize=16, pad=20)

# Remove axes
plt.axis('off')

# Save figure
plt.savefig('Perturb-seq_manuscript/topic_analysis/topic1_network.png', 
            dpi=300, bbox_inches='tight')
plt.close() 