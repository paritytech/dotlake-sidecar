import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import argparse

def connect_to_db(db_path='blocks.db'):
    return duckdb.connect(db_path, read_only=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Block ingestion script for Substrate-based chains")
    parser.add_argument("--chain", required=True)
    parser.add_argument("--relay_chain", required=True)
    parser.add_argument("--db_path", required=True)
    return parser.parse_args()


args = parse_arguments()

st.set_page_config(
    page_title="Search Block",
    page_icon="🔍",
)

st.title("Search Block")

st.sidebar.header("Search Blocks")

# Text input for block number
block_number = st.text_input("Enter Block Number:", "")

if block_number:
    try:
        # Convert input to integer
        block_number = int(block_number)
        
        # Connect to DuckDB
        conn = connect_to_db(args.db_path)

        # Query to fetch the block
        query = f"""
        SELECT *
        FROM blocks_{args.relay_chain}_{args.chain}
        WHERE number = '{block_number}'
        LIMIT 1
        """
        
        # Execute query and fetch results
        result = conn.execute(query).fetchdf()

        if not result.empty:
            st.subheader(f"Block Details: {block_number}")
            
            # Display basic block information
            st.write("Basic Information:")
            basic_info = result[['number', 'hash', 'parentHash', 'stateRoot', 'extrinsicsRoot', 'authorId', 'timestamp', 'finalized']]
            data = np.array([basic_info.columns, basic_info.iloc[0].to_list()])
            data = data.transpose()
            data_df = pd.DataFrame(data)
            st.dataframe(data_df, hide_index=True)

            # Display extrinsics
            st.write("Extrinsics:")
            extrinsics = pd.DataFrame(result['extrinsics'].iloc[0])
            st.dataframe(extrinsics)

            # Display events
            st.write("Events:")
            events = pd.DataFrame([
                event for extrinsic in result['extrinsics'].iloc[0]
                for event in extrinsic['events']
            ])
            st.dataframe(events)

        else:
            st.warning(f"No block found with number {block_number}")

        # Close the connection
        conn.close()

    except ValueError:
        st.error("Please enter a valid integer for the block number.")
    except Exception as e:
        st.error(f"An error occurred: please refresh the page")
