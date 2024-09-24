import duckdb
import os
import json

def connect_to_db(db_path='blocks.db'):
    """
    Connect to a DuckDB database.
    
    Args:
        db_path (str): Path to the database file. Defaults to 'blocks.db'.
    
    Returns:
        duckdb.DuckDBPyConnection: A connection to the DuckDB database.
    """
    if not os.path.exists(db_path):
        print(f"Creating new database at {db_path}")
    # print(f"Connecting to the database at path {db_path}")
    return duckdb.connect(db_path)

def create_blocks_table(conn, chain, relay_chain):
    """
    Create the blocks table if it doesn't exist.
    
    Args:
        conn (duckdb.DuckDBPyConnection): A connection to the DuckDB database.
    """

    # drop_table(conn, f"blocks_{relay_chain}_{chain}")

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS blocks_{relay_chain}_{chain} (
        relay_chain STRING ,
        chain STRING ,
        timestamp INTEGER ,
        number STRING ,
        hash STRING ,
        parentHash STRING ,
        stateRoot STRING ,
        extrinsicsRoot STRING ,
        authorId STRING ,
        finalized BOOLEAN ,
        extrinsics STRUCT(
            method STRUCT(
                pallet STRING ,
                method STRING 
            ),
            signature STRUCT(
                signature STRING ,
                signer STRUCT(
                    id STRING 
                )
            ),
            nonce STRING,
            args STRING ,
            tip STRING,
            hash STRING ,
            info STRING ,
            era STRUCT(
                immortalEra STRING
            ),
            events STRUCT(
                method STRUCT(
                    pallet STRING ,
                    method STRING 
                ),
                data STRING 
            )[],
            success BOOLEAN ,
            paysFee BOOLEAN 
        )[],
        onInitialize STRUCT(
            events STRUCT(
                method STRUCT(
                    pallet STRING ,
                    method STRING 
                ),
                data STRING 
            )[]
        ),
        onFinalize STRUCT(
            events STRUCT(
                method STRUCT(
                    pallet STRING ,
                    method STRING 
                ),
                data STRING 
            )[]
        ),
        logs STRUCT(
            log_type STRING ,
            index STRING ,
            value STRING 
        )[]
    );

    """)

def insert_block(conn, block_data):
    """
    Insert a block into the blocks table.
    
    Args:
        conn (duckdb.DuckDBPyConnection): A connection to the DuckDB database.
        block_data (dict): A dictionary containing the block data.
    """
    # Prepare the data for insertion
    extrinsics = []
    for extrinsic in block_data.get('extrinsics', []):
        extrinsic_events = []
        for event in extrinsic.get('events', []):
            extrinsic_events.append({
                'method': {
                    'pallet': event['method']['pallet'],
                    'method': event['method']['method']
                },
                'data': event['data']
            })

        signer_id = ''
        signature = extrinsic.get('signature', {})
        
        if isinstance(signature, dict):
            signer = signature.get('signer', '')
            if isinstance(signer, dict):
                signer_id = signer.get('id', '')
            elif isinstance(signer, str):
                signer_id = signer
                    
        extrinsics.append({
            'method': {
                'pallet': extrinsic['method']['pallet'],
                'method': extrinsic['method']['method']
            },
            'signature': {
                'signature':  '' if extrinsic['signature'] is None else extrinsic.get('signature', {}).get('signature', ''),
                'signer': {
                    'id':  signer_id #'' if extrinsic['signature'] is None else extrinsic.get('signature', {}).get('signer', {}).get('id', '')
                }
            },
            'nonce': extrinsic.get('nonce', ''),
            'args': extrinsic['args'],
            'tip': extrinsic.get('tip', ''),
            'hash': extrinsic['hash'],
            'info': extrinsic['info'],
            'era': {'immortalEra': extrinsic.get('era', {}).get('immortalEra', '')},
            'events': extrinsic_events,
            'success': extrinsic['success'],
            'paysFee': extrinsic['paysFee']
        })

    on_initialize_events = []
    for event in block_data.get('onInitialize', {}).get('events', []):
        on_initialize_events.append({
            'method': {
                'pallet': event['method']['pallet'],
                'method': event['method']['method']
            },
            'data': event['data']
        })

    on_finalize_events = []
    for event in block_data.get('onFinalize', {}).get('events', []):
        on_finalize_events.append({
            'method': {
                'pallet': event['method']['pallet'],
                'method': event['method']['method']
            },
            'data': event['data']
        })

    logs = []
    for log in block_data.get('logs', []):
        logs.append({
            'log_type': log['type'],
            'index': log['index'],
            'value': log['value']
        })

    # Execute the INSERT statement
    conn.execute(f"""
        INSERT INTO blocks_{block_data['relay_chain']}_{block_data['chain']} 
        (relay_chain, chain, timestamp, number, hash, parentHash, stateRoot, extrinsicsRoot, authorId, finalized, extrinsics, onInitialize, onFinalize, logs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        block_data['relay_chain'],
        block_data['chain'],
        block_data['timestamp'],
        block_data['number'],
        block_data.get('hash', ''),
        block_data.get('parentHash', ''),
        block_data.get('stateRoot', ''),
        block_data.get('extrinsicsRoot', ''),
        block_data.get('authorId', ''),
        block_data.get('finalized', ''),
        extrinsics,
        {'events': on_initialize_events},
        {'events': on_finalize_events},
        logs
    ))

def drop_table(conn, table_name):
    conn.execute(f"""
        DROP TABLE {table_name}
    """)

def query(conn, query_str):
    return conn.execute(query_str).fetchdf()

def close_connection(conn):
    """
    Close the database connection.
    
    Args:
        conn (duckdb.DuckDBPyConnection): A connection to the DuckDB database.
    """
    conn.close()
