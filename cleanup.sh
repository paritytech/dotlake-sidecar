#!/bin/bash
# Read configuration from config.yaml
CREATE_DB=$(yq eval '.create_db' config.yaml)
RETAIN_DB=$(yq eval '.retain_db' config.yaml)

# Stop and remove containers started by docker-compose
echo "Stopping docker-compose services..."
cd ingest/docker
if [ "$CREATE_DB" == "false" ]; then
    docker compose down
    echo "Docker compose services stopped successfully."
elif [ "$CREATE_DB" == "true" ]; then
    if [ "$RETAIN_DB" == "true" ]; then
        docker stop dotlake_sidecar_instance subindex-ingest superset
        docker rm dotlake_sidecar_instance subindex-ingest superset
        echo "Docker services stopped successfully (keeping postgres running)."
    else
        docker stop dotlake_sidecar_instance subindex-ingest superset postgres_db
        docker rm dotlake_sidecar_instance subindex-ingest superset postgres_db
        echo "All docker services including database stopped and removed."
    fi
else
    echo "No docker compose files found in ingest/docker directory."
fi
cd ../../

# Remove the docker network if it exists
if docker network ls | grep -q "dotlake_network"; then
    docker network rm dotlake_network
    echo "Removed dotlake_network."
else 
    echo "dotlake_network not found."
fi

echo "Cleanup complete."
