import psycopg2
from psycopg2 import Error

def connect_to_postgres(host, port, database, user, password):
    """
    Establish a connection to the PostgreSQL database.

    Args:
        host (str): The database host.
        port (int): The database port.
        database (str): The name of the database.
        user (str): The database user.
        password (str): The database password.

    Returns:
        psycopg2.extensions.connection: A connection object if successful, None otherwise.
    """
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("Successfully connected to PostgreSQL database")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def create_tables(connection, chain, relay_chain):
    """
    Create necessary tables in the PostgreSQL database if they don't exist.

    Args:
        connection (psycopg2.extensions.connection): The database connection object.
        chain (str): The name of the chain.
        relay_chain (str): The name of the relay chain.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS blocks_{relay_chain}_{chain} (
                relay_chain VARCHAR(255),
                chain VARCHAR(255),
                timestamp INTEGER,
                number VARCHAR(255) PRIMARY KEY,
                hash VARCHAR(255),
                parentHash VARCHAR(255),
                stateRoot VARCHAR(255),
                extrinsicsRoot VARCHAR(255),
                authorId VARCHAR(255),
                finalized BOOLEAN,
                extrinsics JSONB
            )
        """)
        connection.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def insert_block_data(connection, block_data, chain, relay_chain):
    """
    Insert processed block data into the PostgreSQL database.

    Args:
        connection (psycopg2.extensions.connection): The database connection object.
        block_data (dict): The block data to be inserted.
        chain (str): The name of the chain.
        relay_chain (str): The name of the relay chain.
    """
    try:
        cursor = connection.cursor()
        
        insert_query = f"""
        INSERT INTO blocks_{relay_chain}_{chain} 
        (relay_chain, chain, timestamp, number, hash, parentHash, stateRoot, extrinsicsRoot, authorId, finalized, extrinsics)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (number) DO UPDATE SET
        relay_chain = EXCLUDED.relay_chain,
        chain = EXCLUDED.chain,
        timestamp = EXCLUDED.timestamp,
        hash = EXCLUDED.hash,
        parentHash = EXCLUDED.parentHash,
        stateRoot = EXCLUDED.stateRoot,
        extrinsicsRoot = EXCLUDED.extrinsicsRoot,
        authorId = EXCLUDED.authorId,
        finalized = EXCLUDED.finalized,
        extrinsics = EXCLUDED.extrinsics
        """
        
        values = (
            block_data['relay_chain'],
            block_data['chain'],
            block_data['timestamp'],
            block_data['number'],
            block_data['hash'],
            block_data['parentHash'],
            block_data['stateRoot'],
            block_data['extrinsicsRoot'],
            block_data['authorId'],
            block_data['finalized'],
            psycopg2.extras.Json(block_data['extrinsics'])
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Block {block_data['number']} inserted/updated successfully")
    except Error as e:
        print(f"Error inserting block data: {e}")

def close_connection(connection):
    """
    Safely close the PostgreSQL database connection.

    Args:
        connection (psycopg2.extensions.connection): The database connection object.
    """
    if connection:
        connection.close()
        print("PostgreSQL connection closed")

def query(connection, query_str):
    return ""
