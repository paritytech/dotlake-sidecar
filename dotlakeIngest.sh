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
DB_HOST=$(yq eval '.databases[0].host' config.yaml)
DB_PORT=$(yq eval '.databases[0].port' config.yaml)
DB_NAME=$(yq eval '.databases[0].name' config.yaml)
DB_USER=$(yq eval '.databases[0].user' config.yaml)
DB_PASSWORD=$(yq eval '.databases[0].password' config.yaml)
DB_PROJECT=$(yq eval '.databases[0].project_id' config.yaml)
DB_CRED_PATH=$(yq eval '.databases[0].credentials_path' config.yaml)
DB_DATASET=$(yq eval '.databases[0].dataset' config.yaml)
DB_TABLE=$(yq eval '.databases[0].table' config.yaml)

# Start Substrate API Sidecar
echo "Starting Substrate API Sidecar..."
docker run -d --rm --read-only -e SAS_SUBSTRATE_URL="$WSS" -p 8080:8080 --name dotlake_sidecar_instance parity/substrate-api-sidecar:latest
if [ $? -eq 0 ]; then
    echo "Substrate API Sidecar started successfully."
else
    echo "Failed to start Substrate API Sidecar."
    exit 1
fi

# Start Block Ingest Service
echo "Starting Block Ingest Service..."
docker run -d --rm \
    --name dotlake_ingest \
    -e CHAIN="$CHAIN" \
    -e RELAY_CHAIN="$RELAY_CHAIN" \
    -e WSS="$WSS" \
    -e DB_TYPE="$DB_TYPE" \
    -e DB_HOST="$DB_HOST" \
    -e DB_PORT="$DB_PORT" \
    -e DB_NAME="$DB_NAME" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -p 8501:8501 eu.gcr.io/parity-data-infra-evaluation/block-ingest:0.2.1
if [ $? -eq 0 ]; then
    echo "Block Ingest Service started successfully."
else
    echo "Failed to start Block Ingest Service."
    exit 1
fi

echo "Starting the services....this will take a minute...."
sleep 60
echo "Both services are now running. You can access Substrate API Sidecar at http://localhost:8080 and Block Ingest Service at http://localhost:8501"

# Create SQLAlchemy URI for Postgres or MySQL
if [[ $(yq eval '.databases[0].type' config.yaml) == "postgres" ]]; then
    SQLALCHEMY_URI="postgres+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
elif [[ $(yq eval '.databases[0].type' config.yaml) == "mysql" ]]; then
    SQLALCHEMY_URI="mysql+mysqldb://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
else
    echo "Unsupported database type. Only postgres and mysql are supported."
    exit 1
fi

echo "SQLAlchemy URI created: ${SQLALCHEMY_URI}"

# Start Superset locally
echo "Starting Superset..."
cd superset-local
sh start_superset.sh "$SQLALCHEMY_URI"
if [ $? -eq 0 ]; then
    echo "Superset started successfully."
else
    echo "Failed to start Superset."
    exit 1
fi
