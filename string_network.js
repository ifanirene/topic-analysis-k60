function loadStringNetwork(topicNum) {
    fetch(`topic${topicNum}_string_network.json`)
        .then(response => response.json())
        .then(data => {
            const nodes = new Set();
            const edges = [];
            
            // Process interactions
            data.forEach(interaction => {
                nodes.add(interaction.preferredName_A);
                nodes.add(interaction.preferredName_B);
                edges.push({
                    source: interaction.preferredName_A,
                    target: interaction.preferredName_B,
                    score: interaction.score
                });
            });

            // Create network visualization using vis.js
            const container = document.getElementById('network-container');
            
            const nodesArray = Array.from(nodes).map(node => ({
                id: node,
                label: node,
                shape: 'dot',
                size: 10
            }));

            const edgesArray = edges.map(edge => ({
                from: edge.source,
                to: edge.target,
                width: edge.score / 1000,  // Scale down the score for visual purposes
                color: {
                    color: '#848484',
                    highlight: '#3498db'
                }
            }));

            const data = {
                nodes: new vis.DataSet(nodesArray),
                edges: new vis.DataSet(edgesArray)
            };

            const options = {
                physics: {
                    barnesHut: {
                        gravitationalConstant: -2000,
                        centralGravity: 0.3,
                        springLength: 95,
                        springConstant: 0.04
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 200
                }
            };

            new vis.Network(container, data, options);
        })
        .catch(error => {
            console.error('Error loading network data:', error);
            document.getElementById('network-container').innerHTML = 
                `<p>Error loading network data. Please check the console for details.</p>`;
        });
} 