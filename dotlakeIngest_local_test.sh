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
INGEST_MODE=$(yq eval '.ingest_mode' config.yaml)
START_BLOCK=$(yq eval '.start_block' config.yaml)
END_BLOCK=$(yq eval '.end_block' config.yaml)

# Database configuration
DB_TYPE=$(yq eval '.databases[0].type' config.yaml)
DB_HOST=$(yq eval '.databases[0].host' config.yaml)
DB_PORT=$(yq eval '.databases[0].port' config.yaml)
DB_NAME=$(yq eval '.databases[0].name' config.yaml)
DB_USER=$(yq eval '.databases[0].user' config.yaml)
DB_PASSWORD=$(yq eval '.databases[0].password' config.yaml)
DB_PROJECT=$(yq eval '.databases[0].project_id' config.yaml)
DB_CRED_PATH=$(yq eval '.databases[0].credentials_path' config.yaml)
DB_DATASET=$(yq eval '.databases[0].dataset' config.yaml)
DB_TABLE=$(yq eval '.databases[0].table' config.yaml)

echo "Chain: $CHAIN"
echo "Relay Chain: $RELAY_CHAIN"
echo "WebSocket URL: $WSS"
echo "Database Type: $DB_TYPE"
echo "Database Path: $DB_PATH"
echo "Database Project: $DB_PROJECT"
echo "Database Credentials Path: $DB_CRED_PATH"
echo "Database Dataset: $DB_DATASET"
echo "Database Table: $DB_TABLE"
echo "Database Host: $DB_HOST"
echo "Database Port: $DB_PORT"
echo "Database User: $DB_USER"
echo "Database Password: $DB_PASSWORD"
echo "Database Name: $DB_NAME"


# Start Substrate API Sidecar
# echo "Starting Substrate API Sidecar..."
# docker run -d --rm --read-only -e SAS_SUBSTRATE_URL="$WSS" -p 8080:8080 parity/substrate-api-sidecar:latest
# if [ $? -eq 0 ]; then
#     echo "Substrate API Sidecar started successfully."
# else
#     echo "Failed to start Substrate API Sidecar."
#     exit 1
# fi

cd ingest/

# Start the main.py script
echo "Starting main.py script..."
/usr/bin/python3 main.py --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --wss "$WSS" --db_path "$DB_PATH" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" --db_host "$DB_HOST" --db_port "$DB_PORT" --db_user "$DB_USER" --db_password "$DB_PASSWORD" --db_name "$DB_NAME" --ingest_mode "$INGEST_MODE" --start_block "$START_BLOCK" --end_block "$END_BLOCK" &

sleep 15

# Start the Streamlit app
echo "Starting Streamlit app..."
/usr/bin/python3 -m streamlit run Home.py --server.port 8501 -- --db_path "$DB_PATH" --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" --db_host "$DB_HOST" --db_port "$DB_PORT" --db_user "$DB_USER" --db_password "$DB_PASSWORD" --db_name "$DB_NAME" &

# # Wait for all background processes to finish
# wait

# echo "Starting the services....this will take a minute...."
# sleep 60
# echo "Both services are now running. You can access Substrate API Sidecar at http://localhost:8080 and Block Ingest Service at http://localhost:8501"
