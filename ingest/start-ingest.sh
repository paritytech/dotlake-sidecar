#!/bin/bash

# Default values
DB_PATH="blocks.db"

# Parse command line arguments
# while [[ $# -gt 0 ]]; do
#     key="$1"
#     case $key in
#         --chain)
#         CHAIN="$2"
#         shift
#         shift
#         ;;
#         --relay-chain)
#         RELAY_CHAIN="$2"
#         shift
#         shift
#         ;;
#         --wss)
#         WSS="$2"
#         shift
#         shift
#         ;;
#         *)
#         echo "Unknown option: $1"
#         exit 1
#         ;;
#     esac
# done

# Check if required arguments are provided
# if [ -z "$CHAIN" ] || [ -z "$RELAY_CHAIN" ] || [ -z "$WSS" ]; then
#     echo "Usage: $0 --chain <chain> --relay-chain <relay_chain> --wss <wss_endpoint>"
#     exit 1
# fi

# Start the sidecar docker container
# echo "Starting sidecar docker container..."
# docker run -d --rm --read-only -e SAS_SUBSTRATE_URL="$WSS" -p 8080:8080 parity/substrate-api-sidecar:latest

# Start the main.py script
echo "Starting main.py script..."
python3 main.py --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --wss "$WSS" --db_path "$DB_PATH" &

sleep 15

# Start the Streamlit app
echo "Starting Streamlit app..."
python3 -m streamlit run Home.py --server.port 8501 -- --db_path "$DB_PATH" --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" &

# Wait for all background processes to finish
wait
