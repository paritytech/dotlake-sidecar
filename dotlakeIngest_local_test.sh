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
DB_TYPE=$(yq eval '.databases[0].type' config.yaml)
DB_PROJECT=$(yq eval '.databases[0].project_id' config.yaml)
DB_CRED_PATH=$(yq eval '.databases[0].credentials_path' config.yaml)
DB_DATASET=$(yq eval '.databases[0].dataset' config.yaml)
DB_TABLE=$(yq eval '.databases[0].table' config.yaml)

# Start Substrate API Sidecar
# echo "Starting Substrate API Sidecar..."
# docker run -d --rm --read-only -e SAS_SUBSTRATE_URL="$WSS" -p 8080:8080 parity/substrate-api-sidecar:latest
# if [ $? -eq 0 ]; then
#     echo "Substrate API Sidecar started successfully."
# else
#     echo "Failed to start Substrate API Sidecar."
#     exit 1
# fi


# Default values
DB_PATH="blocks.db"

cd ingest/

# Start the main.py script
echo "Starting main.py script..."
/usr/bin/python3 main.py --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --wss "$WSS" --db_path "$DB_PATH" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" &

sleep 30

# Start the Streamlit app
# echo "Starting Streamlit app..."
# /usr/bin/python3 -m streamlit run Home.py --server.port 8501 -- --db_path "$DB_PATH" --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" &

# # Wait for all background processes to finish
# wait

# echo "Starting the services....this will take a minute...."
# sleep 60
# echo "Both services are now running. You can access Substrate API Sidecar at http://localhost:8080 and Block Ingest Service at http://localhost:8501"
