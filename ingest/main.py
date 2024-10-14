import argparse
import os
import json
import time
import requests
import traceback
import subprocess
from write_block import writeBlock

def parse_arguments():
    parser = argparse.ArgumentParser(description="Block ingestion script for Substrate-based chains")
    parser.add_argument("--chain", required=True, help="Name of the chain to process")
    parser.add_argument("--relay_chain", required=True, help="Name of the relay chain")
    parser.add_argument("--backfill", action="store_true", help="Enable backfill mode")
    parser.add_argument("--live", action="store_true", help="Enable live ingestion mode")
    parser.add_argument("--wss", required=True, help="WebSocket URL for the chain")
    parser.add_argument("--database", required=True, help="Name of the database")
    parser.add_argument("--db_path", required=True)
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


def main():
    args = parse_arguments()
    
    database_info = {
        'database': args.database,
        'database_project': args.db_project,
        'database_dataset': args.db_dataset,
        'database_table': args.db_table,
        'database_cred_path': args.db_cred_path,
        'database_path': args.db_path,
        'database_host': args.db_host,
        'database_port': args.db_port,
        'database_user': args.db_user,
        'database_password': args.db_password,
        'database_name': args.db_name
    }

    # Connect to the database
    if args.database == 'postgres':
        from postgres_utils import connect_to_postgres, close_connection, create_tables
        db_connection = connect_to_postgres(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
        create_tables(db_connection, args.chain, args.relay_chain)
        close_connection(db_connection)
    elif args.database == 'mysql':
        from mysql_utils import connect_to_mysql, close_connection, create_tables
        db_connection = connect_to_mysql(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
        if db_connection:
            create_tables(db_connection, args.chain, args.relay_chain)
            close_connection(db_connection)
            print(f"Connected to MySQL and created tables for {args.chain} on {args.relay_chain}")
        else:
            print("Failed to connect to MySQL database")
    elif args.database == 'duckdb':
        from duckdb_utils import connect_to_db, close_connection, create_blocks_table
        db_connection = connect_to_db(args.db_path)
        create_blocks_table(db_connection, args.chain, args.relay_chain)
        close_connection(db_connection)
    elif args.database == 'bigquery':
        from bigquery_utils import connect_to_bigquery, create_blocks_table
        db_connection = connect_to_bigquery(args.db_project, args.db_cred_path)
        create_blocks_table(db_connection, args.db_dataset, args.db_table)
        print(f"Connected to {args.database} and created {args.db_dataset}.{args.db_table} for {args.chain} on {args.relay_chain}")


    # sidecar_url = "http://172.17.0.1:8080"
    sidecar_url = "http://localhost:8080"
    last_block = -1

    while True:
        try:
            # Fetch the latest block number from the chain
            chain_head = fetch_chain_head(sidecar_url)
            
            if chain_head == last_block:
                # No new blocks since last check
                print("No new blocks to process. Retrying in 6 seconds.")
            elif last_block == -1:
                # First run, start from the block before the current head
                last_block = chain_head - 1
            elif chain_head is not None:
                # Process new blocks
                for block_id in range(last_block + 1, chain_head + 1):
                    # Prepare the request for writing a block
                    block_write_request = {
                        "chainName": args.chain,
                        "relayChain": args.relay_chain,
                        "blockId": block_id,
                        "endpoint": sidecar_url,
                        "bucket": "test-polka-data"
                    }
                    # Attempt to write the block, retry if unsuccessful
                    write_status = writeBlock(block_write_request, args.db_path)
                    while not write_status:
                        write_status = writeBlock(block_write_request, database_info)
                    print(f"Processed block {block_id}")
                # Update last processed block
                last_block = chain_head
            else:
                # Failed to fetch chain head
                print("Failed to fetch chain head. Retrying in 6 seconds.")
            
            # Fetch the latest block number from the database
            if args.database == 'postgres':
                from postgres_utils import connect_to_postgres, close_connection, query
                db_connection = connect_to_postgres(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
                fetch_last_block_query = f"SELECT number FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 1"
                df = query(db_connection, fetch_last_block_query)
                close_connection(db_connection)
            elif args.database == 'mysql':
                from mysql_utils import connect_to_mysql, close_connection, query_block_data
                db_connection = connect_to_mysql(args.db_host, args.db_port, args.db_name, args.db_user, args.db_password)
                fetch_last_block_query = f"SELECT number FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 1"
                df = query_block_data(db_connection, fetch_last_block_query)
                close_connection(db_connection)
            elif args.database == 'duckdb':
                from duckdb_utils import connect_to_db, close_connection, query
                db_connection = connect_to_db(args.db_path)
                fetch_last_block_query = f"SELECT number FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 1"
                df = query(db_connection, fetch_last_block_query)
                close_connection(db_connection)
            elif args.database == 'bigquery':
                from bigquery_utils import connect_to_bigquery, query
                db_connection = connect_to_bigquery(args.db_project, args.db_cred_path)
                fetch_last_block_query = f"SELECT number FROM {args.db_dataset}.{args.db_table} ORDER BY number DESC LIMIT 1"
                df = query(db_connection, fetch_last_block_query)

            last_block = int(df['number'].iloc[0])
        except Exception as e:
            # Handle any exceptions that occur during processing
            print(f"An error occurred: {e}. Retrying in 6 seconds.")
            print(traceback.format_exc())
        
        # Wait before next iteration
        time.sleep(6)
    

def fetch_chain_head(sidecar_url):
    try:
        response = requests.get(f"{sidecar_url}/blocks/head")
        response.raise_for_status()
        head_data = response.json()
        return int(head_data['number'])
    except requests.RequestException as e:
        print(f"Error fetching chain head: {e}")
        return None
    

if __name__ == "__main__":
    main()

# TODO: Add logging
# TODO: Add error handling
# TODO: Add tests
# TODO: Add type hints
# TODO: Add docstrings
