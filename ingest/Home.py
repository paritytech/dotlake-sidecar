import streamlit as st
import argparse
import duckdb
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Function to connect to DuckDB
def connect_to_db(db_path='/Users/pranaypatil/data_eng_repos/data-applications/blocks.db'):
    return duckdb.connect(db_path, read_only=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Block ingestion script for Substrate-based chains")
    parser.add_argument("--chain", required=True)
    parser.add_argument("--relay_chain", required=True)
    parser.add_argument("--db_path", required=True)
    return parser.parse_args()


args = parse_arguments()

st.set_page_config(
    page_title="Dotlake Explorer",
    page_icon="🚀",
)

# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
# count = st_autorefresh(interval=30000, limit=100, key="fizzbuzzcounter")

placeholder = st.empty()

chain = args.chain
relay_chain = args.relay_chain

with placeholder.container():

    try:
        # Connect to DuckDB
        conn = connect_to_db(args.db_path)

        query = f"""
        SELECT *
        FROM blocks_{relay_chain}_{chain}
        ORDER BY number DESC
        LIMIT 50
        """
        recent_blocks = conn.execute(query).fetchdf()
        recent_blocks['timestamp'] = recent_blocks['timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S") )

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
        num_extrinsics = len(recent_blocks['extrinsics'].iloc[0])
        extrinsics_col.metric("Extrinsics", num_extrinsics)

        # Calculate the total number of events in the most recent block
        num_events = (
            len(recent_blocks['onFinalize'].iloc[0]['events']) +
            len(recent_blocks['onInitialize'].iloc[0]['events']) +
            sum(len(ex['events']) for ex in recent_blocks['extrinsics'].iloc[0])
        )
        
        # Display the total number of events
        events_col.metric("Events", num_events)

        # Display a table of the most recent blocks
        st.header("Recent Blocks")

        st.dataframe(recent_blocks[['number', 'timestamp', 'hash', 'finalized']])
        
        # Close the connection
        conn.close()
    except Exception as e:
        st.error("Oops...something went wrong, please refresh the page")

