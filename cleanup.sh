#!/bin/bash

# Stop and remove containers started by docker-compose
echo "Stopping docker-compose services..."
cd ingest
if [ -f "docker-compose.yaml" ]; then
    docker-compose down
    echo "Docker compose services stopped successfully."
else
    echo "docker-compose.yaml not found in ingest directory."
fi
cd ..

# Remove the docker network if it exists
if docker network ls | grep -q "dotlake_network"; then
    docker network rm dotlake_network
    echo "Removed dotlake_network."
else 
    echo "dotlake_network not found."
fi

echo "Cleanup complete."
