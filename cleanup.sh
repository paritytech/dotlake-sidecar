#!/bin/bash

# Stop and remove all containers created by dotlakeIngest.sh
echo "Stopping and removing Docker containers..."

# Stop and remove specific containers
containers_to_remove=("dotlake_sidecar_instance" "dotlake_ingest" "superset")

for container in "${containers_to_remove[@]}"; do
    if docker ps -aq --filter "name=$container" | grep -q .; then
        docker stop $container
        docker rm $container
        echo "Container $container stopped and removed successfully."
    else
        echo "Container $container not found."
    fi
done

# Check if any containers were removed
if [ "$(docker ps -aq --filter "name=dotlake_sidecar_instance|dotlake_ingest|superset")" ]; then
    echo "Specified Docker containers stopped and removed successfully."
else
    echo "No specified Docker containers were found."
fi


echo "Cleanup complete."
