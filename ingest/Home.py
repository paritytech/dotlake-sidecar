import streamlit as st
import argparse
import duckdb
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Function to connect to DuckDB
def connect_to_db(db_path='blocks.db'):
    return duckdb.connect(db_path, read_only=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Block ingestion script for Substrate-based chains")
    parser.add_argument("--chain", required=True, help="Name of the chain to process")
    parser.add_argument("--relay_chain", required=True, help="Name of the relay chain")
    parser.add_argument("--backfill", action="store_true", help="Enable backfill mode")
    parser.add_argument("--live", action="store_true", help="Enable live ingestion mode")
    parser.add_argument("--database", help="Name of the database")
    parser.add_argument("--db_path")
    parser.add_argument("--db_project")
    parser.add_argument("--db_cred_path")
    parser.add_argument("--db_dataset")
    parser.add_argument("--db_table")
    parser.add_argument("--db_host", required=False, help="Database host")
    parser.add_argument("--db_port", required=False, type=int, help="Database port")
    parser.add_argument("--db_user", required=False, help="Database user")
    parser.add_argument("--db_password", required=False, help="Database password")
    parser.add_argument("--db_name", required=False, help="Database name")
    return parser.parse_args()


args = parse_arguments()

st.set_page_config(
    page_title="Dotlake Explorer",
    page_icon="🚀",
)

# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=30000, limit=100, key="fizzbuzzcounter")

placeholder = st.empty()

chain = args.chain
relay_chain = args.relay_chain

with placeholder.container():

    try:

        if args.database == 'postgres':
            from postgres_utils import connect_to_postgres, close_connection, query
            db_connection = connect_to_postgres(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 50"
            recent_blocks = query(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'mysql':
            from mysql_utils import connect_to_mysql, close_connection, query_block_data
            db_connection = connect_to_mysql(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 50"
            recent_blocks = query_block_data(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'duckdb':
            from duckdb_utils import connect_to_db, close_connection, query
            db_connection = connect_to_db(args.db_path)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 50"
            recent_blocks = query(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'bigquery':
            from bigquery_utils import connect_to_bigquery, query
            db_connection = connect_to_bigquery(args.db_project, args.db_cred_path)
            fetch_last_block_query = f"SELECT * FROM {args.db_dataset}.{args.db_table} ORDER BY number DESC LIMIT 50"
            recent_blocks = query(db_connection, fetch_last_block_query)

        recent_blocks['timestamp'] = recent_blocks['timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000).strftime("%Y-%m-%d %H:%M:%S") )

        # Streamlit app
        st.title("Dotlake Explorer")
        st.sidebar.header("Home")

        # Display the chain and relay chain names
        st.markdown(f"**Chain**: *{chain}*      **Relay Chain**: *{relay_chain}*")

        # Display the most recent block
        st.subheader("Most Recent Block")
    
        bn, ts = st.columns(2)
        latest_block = recent_blocks['number'].iloc[0]
        bn.metric("Block Number", latest_block)

        # Get and display the timestamp of the last block
        last_timestamp = recent_blocks['timestamp'].iloc[0]
        ts.metric("Block Timestamp", f"{last_timestamp} (+UTC)")

        # Create two columns for displaying extrinsics and events metrics
        extrinsics_col, events_col = st.columns(2)

        # Display the number of extrinsics in the most recent block
        if args.database == 'postgres' or args.database == 'mysql':
            num_extrinsics = len(json.loads(recent_blocks['extrinsics'].iloc[0]))
        elif args.database == 'duckdb':
            num_extrinsics = len(recent_blocks['extrinsics'].iloc[0])
        elif args.database == 'bigquery':
            num_extrinsics = len(json.loads(recent_blocks['extrinsics'].iloc[0]))
        else:
            num_extrinsics = 0  # Default value if database type is not recognized
        extrinsics_col.metric("Extrinsics", num_extrinsics)

        # Calculate the total number of events in the most recent block
        if args.database == 'postgres' or args.database == 'mysql':
            num_events = (
                len(json.loads(recent_blocks['onFinalize'].iloc[0])['events']) +
                len(json.loads(recent_blocks['onInitialize'].iloc[0])['events']) +
                sum(len(ex['events']) for ex in json.loads(recent_blocks['extrinsics'].iloc[0]))
            )
        elif args.database == 'duckdb':
            num_events = (
                len(recent_blocks['onFinalize'].iloc[0]['events']) +
                len(recent_blocks['onInitialize'].iloc[0]['events']) +
                sum(len(ex['events']) for ex in recent_blocks['extrinsics'].iloc[0])
            )
        elif args.database == 'bigquery':
            num_events = (
                len(json.loads(recent_blocks['onFinalize'].iloc[0])['events']) +
                len(json.loads(recent_blocks['onInitialize'].iloc[0])['events']) +
                sum(len(ex['events']) for ex in json.loads(recent_blocks['extrinsics'].iloc[0]))
            )
        else:
            num_events = 0  # Default value if database type is not recognized
        
        # Display the total number of events
        events_col.metric("Events", num_events)

        # Display a table of the most recent blocks
        st.header("Recent Blocks")

        st.dataframe(recent_blocks[['number', 'timestamp', 'hash', 'finalized']])
        
    except Exception as e:
        st.error("Oops...something went wrong, please refresh the page")
        st.error(e)

