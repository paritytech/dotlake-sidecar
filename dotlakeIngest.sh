#!/bin/bash

# Check the operating system and install yq if not already installed
if [[ $(uname) == "Darwin" ]]; then
    # macOS
    if ! command -v yq &> /dev/null; then
        echo "yq is not installed. Installing yq..."
        brew install yq
    fi
elif [[ $(uname) == "Linux" ]]; then
    # Linux
    if ! command -v yq &> /dev/null; then
        echo "yq is not installed. Installing yq..."
        go install github.com/mikefarah/yq/v4@latest
    fi
else
    echo "Unsupported operating system. Please install yq manually."
    exit 1
fi

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

# Start Block Ingest Service
echo "Starting Block Ingest Service..."
export RELAY_CHAIN="$RELAY_CHAIN"
export CHAIN="$CHAIN"
export WSS="$WSS"
export DB_TYPE="$DB_TYPE"
export DB_HOST="$DB_HOST"
export DB_PORT="$DB_PORT"
export DB_NAME="$DB_NAME"
export DB_USER="$DB_USER"
export DB_PASSWORD="$DB_PASSWORD"
export PROJECT_ID="$DB_PROJECT"
export CREDENTIALS_PATH="$DB_CRED_PATH"
export DATASET="$DB_DATASET"
export TABLE="$DB_TABLE"
export SQLALCHEMY_URI="$SQLALCHEMY_URI"
export INGEST_MODE="$INGEST_MODE"
export START_BLOCK="$START_BLOCK" 
export END_BLOCK="$END_BLOCK"

cd ingest
docker-compose up -d
sleep 10
docker exec -it superset superset fab create-admin \
               --username admin \
               --firstname Superset \
               --lastname Admin \
               --email admin@superset.com \
               --password admin

docker exec -it superset superset db upgrade
docker exec -it superset superset set_database_uri -d my_mysql_db -u "$SQLALCHEMY_URI"

cd ..

if [ $? -eq 0 ]; then
    echo "Block Ingest Service started successfully."
else
    echo "Failed to start Block Ingest Service."
    exit 1
fi

echo "Starting the services....this will take couple of minutes...."
sleep 120
echo "All services are now running!"
echo "You can access:"
echo "  • Substrate API Sidecar: http://localhost:8080"
echo "  • Block Ingest Service: http://localhost:8501" 
echo "  • Apache Superset: http://localhost:8088"
