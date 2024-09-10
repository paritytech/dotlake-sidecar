#!/bin/bash

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --chain)
        CHAIN="$2"
        shift
        shift
        ;;
        --relay-chain)
        RELAY_CHAIN="$2"
        shift
        shift
        ;;
        --wss)
        WSS="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if required arguments are provided
if [ -z "$CHAIN" ] || [ -z "$RELAY_CHAIN" ] || [ -z "$WSS" ]; then
    echo "Usage: $0 --chain <chain> --relay-chain <relay_chain> --wss <wss_endpoint>"
    exit 1
fi

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
docker run -d --rm -e CHAIN="$CHAIN" -e RELAY_CHAIN="$RELAY_CHAIN" -e WSS="$WSS" -p 8501:8501 eu.gcr.io/parity-data-infra-evaluation/block-ingest:0.2
if [ $? -eq 0 ]; then
    echo "Block Ingest Service started successfully."
else
    echo "Failed to start Block Ingest Service."
    exit 1
fi

echo "Starting the services....this will take a minute...."
sleep 60
echo "Both services are now running. You can access Substrate API Sidecar at http://localhost:8080 and Block Ingest Service at http://localhost:8501"
