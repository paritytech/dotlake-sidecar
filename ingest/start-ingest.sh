#!/bin/bash

# Default values
# DB_PATH="blocks.db"

echo "Connection Info"
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
echo "SQLAlchemy URI: $SQLALCHEMY_URI"
echo "Ingest Mode: $INGEST_MODE"
echo "Start Block: $START_BLOCK"
echo "End Block: $END_BLOCK"


# Start the main.py script
echo "Starting main.py script..."
python3 main.py --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --wss "$WSS" --db_path "$DB_PATH" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" --db_host "$DB_HOST" --db_port "$DB_PORT" --db_user "$DB_USER" --db_password "$DB_PASSWORD" --db_name "$DB_NAME" --ingest_mode "$INGEST_MODE" --start_block "$START_BLOCK" --end_block "$END_BLOCK" 2>&1 &


# Start the Streamlit app
echo "Starting Streamlit app..."
python3 -m streamlit run Home.py --server.port 8501 -- --db_path "$DB_PATH" --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --database "$DB_TYPE" --db_project "$DB_PROJECT" --db_cred_path "$DB_CRED_PATH" --db_dataset "$DB_DATASET" --db_table "$DB_TABLE" --db_host "$DB_HOST" --db_port "$DB_PORT" --db_user "$DB_USER" --db_password "$DB_PASSWORD" --db_name "$DB_NAME" &

# Wait for all background processes to finish
wait
