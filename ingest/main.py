import argparse
import os
import json
import time
import requests
import subprocess
from write_block import writeBlock

def parse_arguments():
    parser = argparse.ArgumentParser(description="Block ingestion script for Substrate-based chains")
    parser.add_argument("--chain", required=True, help="Name of the chain to process")
    parser.add_argument("--relay_chain", required=True, help="Name of the relay chain")
    parser.add_argument("--backfill", action="store_true", help="Enable backfill mode")
    parser.add_argument("--live", action="store_true", help="Enable live ingestion mode")
    parser.add_argument("--wss", required=True, help="WebSocket URL for the chain")
    parser.add_argument("--db_path", required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    relay_chain = args.relay_chain
    print(f"Processing blocks for {relay_chain}")
    print(f"Chain: {args.chain}")
    print(f"Backfill mode: {args.backfill}")
    print(f"Live ingestion mode: {args.live}")
    print(f"WebSocket URL: {args.wss}")
    print(f"Database path: {args.db_path}")

    # Connect to DuckDB and create the table for the chain
    from duckdb_utils import connect_to_db, create_blocks_table, close_connection

    # Connect to the database
    db_connection = connect_to_db(args.db_path)

    # Create the blocks table for the specific chain and relay chain
    create_blocks_table(db_connection, args.chain, args.relay_chain)

    close_connection(db_connection)

    print(f"Connected to DuckDB and created table for {args.chain} on {args.relay_chain}")

    # TODO: Differentiate execution of backfill and live ingest
    # if args.backfill:
    #     # TODO: Implement backfill logic
    #     print("Backfill mode not yet implemented")
    # elif args.live:
    #     # TODO: Implement live ingestion logic
    #     print("Live ingestion mode not yet implemented")
    # else:
    #     print("Please specify either --backfill or --live mode")
    #     return

    sidecar_url = "http://172.17.0.1:8080"
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
                        write_status = writeBlock(block_write_request, args.db_path)
                    print(f"Processed block {block_id}")
                # Update last processed block
                last_block = chain_head
            else:
                # Failed to fetch chain head
                print("Failed to fetch chain head. Retrying in 6 seconds.")
            
            # Fetch the latest block number from the database
            df = db_connection.execute(f"SELECT number FROM blocks_{args.relay_chain}_{args.chain} ORDER BY number DESC LIMIT 1").fetchdf()
            last_block = df['number'].iloc[0]
        except Exception as e:
            # Handle any exceptions that occur during processing
            print(f"An error occurred: {e}. Retrying in 6 seconds.")
        
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
