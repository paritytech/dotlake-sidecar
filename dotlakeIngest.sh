#!/bin/bash

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "yq is not installed. Please install it to parse YAML files."
    exit 1
fi

# Read configuration from config.yaml
RELAY_CHAIN=$(yq eval '.relay_chain' config.yaml)
CHAIN=$(yq eval '.chain' config.yaml)
WSS=$(yq eval '.wss' config.yaml)

# Database configuration
DB_HOST=$(yq eval '.database.host' config.yaml)
DB_PORT=$(yq eval '.database.port' config.yaml)
DB_NAME=$(yq eval '.database.name' config.yaml)
DB_USER=$(yq eval '.database.user' config.yaml)
DB_PASSWORD=$(yq eval '.database.password' config.yaml)

# Start Substrate API Sidecar
echo "Starting Substrate API Sidecar..."
docker run -d --rm --read-only -e SAS_SUBSTRATE_URL="$WSS" -p 8080:8080 parity/substrate-api-sidecar:latest
if [ $? -eq 0 ]; then
    echo "Substrate API Sidecar started successfully."
else
    echo "Failed to start Substrate API Sidecar."
    exit 1
fi

# Start Block Ingest Service
echo "Starting Block Ingest Service..."
docker run -d --rm \
    -e CHAIN="$CHAIN" \
    -e RELAY_CHAIN="$RELAY_CHAIN" \
    -e WSS="$WSS" \
    -e DB_HOST="$DB_HOST" \
    -e DB_PORT="$DB_PORT" \
    -e DB_NAME="$DB_NAME" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -p 8501:8501 eu.gcr.io/parity-data-infra-evaluation/block-ingest:0.2
if [ $? -eq 0 ]; then
    echo "Block Ingest Service started successfully."
else
    echo "Failed to start Block Ingest Service."
    exit 1
fi

echo "Starting the services....this will take a minute...."
sleep 60
echo "Both services are now running. You can access Substrate API Sidecar at http://localhost:8080 and Block Ingest Service at http://localhost:8501"
