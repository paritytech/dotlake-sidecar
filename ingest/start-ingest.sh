#!/bin/bash

# Default values
DB_PATH="blocks.db"

# Start the main.py script
echo "Starting main.py script..."
python3 main.py --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" --wss "$WSS" --db_path "$DB_PATH" &

sleep 15

# Start the Streamlit app
echo "Starting Streamlit app..."
python3 -m streamlit run Home.py --server.port 8501 -- --db_path "$DB_PATH" --chain "$CHAIN" --relay_chain "$RELAY_CHAIN" &

# Wait for all background processes to finish
wait
