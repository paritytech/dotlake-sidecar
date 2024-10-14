import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import argparse
import json

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

        if args.database == 'postgres':
            from postgres_utils import connect_to_postgres, close_connection, query
            db_connection = connect_to_postgres(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} WHERE number = '{block_number}' LIMIT 1"
            result = query(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'mysql':
            from mysql_utils import connect_to_mysql, close_connection, query_block_data
            db_connection = connect_to_mysql(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} WHERE number = '{block_number}' LIMIT 1"
            result = query_block_data(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'duckdb':
            from duckdb_utils import connect_to_db, close_connection, query
            db_connection = connect_to_db(args.db_path)
            fetch_last_block_query = f"SELECT * FROM blocks_{args.relay_chain}_{args.chain} WHERE number = '{block_number}' LIMIT 1"
            result = query(db_connection, fetch_last_block_query)
            close_connection(db_connection)
        elif args.database == 'bigquery':
            from bigquery_utils import connect_to_bigquery, query
            db_connection = connect_to_bigquery(args.db_project, args.db_cred_path)
            fetch_last_block_query = f"SELECT * FROM {args.db_dataset}.{args.db_table} WHERE number = '{block_number}' LIMIT 1"
            result = query(db_connection, fetch_last_block_query)

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
            if args.database == 'postgres' or args.database == 'mysql':
                extrinsics = pd.DataFrame(json.loads(result['extrinsics'].iloc[0]))
            elif args.database == 'duckdb':
                extrinsics = pd.DataFrame(result['extrinsics'].iloc[0])
            elif args.database == 'bigquery':
                extrinsics = pd.DataFrame(json.loads(result['extrinsics'].iloc[0]))
            else:
                extrinsics = pd.DataFrame()  # Default empty DataFrame if database type is not recognized
            st.dataframe(extrinsics)

            # Display events
            st.write("Events:")
            if args.database == 'postgres' or args.database == 'mysql':
                events = [
                    event for extrinsic in json.loads(result['extrinsics'].iloc[0])
                    for event in extrinsic['events']
                ] + json.loads(result['onInitialize'].iloc[0])['events'] + json.loads(result['onFinalize'].iloc[0])['events']
            elif args.database == 'duckdb':
                events = [
                    event for extrinsic in result['extrinsics'].iloc[0]
                    for event in extrinsic['events']
                ] + result['oninitialize'].iloc[0]['events'] + result['onfinalize'].iloc[0]['events']
            elif args.database == 'bigquery':
                events = [
                    event for extrinsic in json.loads(result['extrinsics'].iloc[0])
                    for event in extrinsic['events']
                ] + json.loads(result['oninitialize'].iloc[0])['events'] + json.loads(result['onfinalize'].iloc[0])['events']
            else:
                events = []  # Default empty list if database type is not recognized
            events = pd.DataFrame(events)
            st.dataframe(events)

        else:
            st.warning(f"No block found with number {block_number}")

    except ValueError:
        st.error("Please enter a valid integer for the block number.")
    except Exception as e:
        st.error(f"An error occurred: please refresh the page {e}")
