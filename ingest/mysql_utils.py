# MySQL Database Connection Utilities
import mysql.connector
from mysql.connector import Error

def connect_to_mysql(host, port, database, user, password):
    """
    Establish a connection to the MySQL database.

    Args:
        host (str): The database host.
        port (int): The database port.
        database (str): The name of the database.
        user (str): The database user.
        password (str): The database password.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return None

def create_tables(connection):
    """
    Create necessary tables in the MySQL database if they don't exist.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                relay_chain VARCHAR(255),
                chain VARCHAR(255),
                timestamp INT,
                number VARCHAR(255) PRIMARY KEY,
                hash VARCHAR(255),
                parentHash VARCHAR(255),
                stateRoot VARCHAR(255),
                extrinsicsRoot VARCHAR(255),
                authorId VARCHAR(255),
                finalized BOOLEAN
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extrinsics (
                block_number VARCHAR(255),
                pallet VARCHAR(255),
                method VARCHAR(255),
                signature VARCHAR(255),
                signer_id VARCHAR(255),
                FOREIGN KEY (block_number) REFERENCES blocks(number)
            )
        """)
        connection.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def insert_block_data(connection, block_data):
    """
    Insert processed block data into the MySQL database.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
        block_data (dict): The block data to be inserted.
    """
    try:
        cursor = connection.cursor()
        
        # Insert block data
        block_insert_query = """
        INSERT INTO blocks (relay_chain, chain, timestamp, number, hash, parentHash, stateRoot, extrinsicsRoot, authorId, finalized)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        block_values = (
            block_data['relay_chain'], block_data['chain'], block_data['timestamp'],
            block_data['number'], block_data['hash'], block_data['parentHash'],
            block_data['stateRoot'], block_data['extrinsicsRoot'], block_data['authorId'],
            block_data['finalized']
        )
        cursor.execute(block_insert_query, block_values)

        # Insert extrinsics data
        extrinsic_insert_query = """
        INSERT INTO extrinsics (block_number, pallet, method, signature, signer_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        for extrinsic in block_data['extrinsics']:
            extrinsic_values = (
                block_data['number'], extrinsic['method']['pallet'], extrinsic['method']['method'],
                extrinsic['signature'].get('signature'), extrinsic['signature'].get('signer', {}).get('id')
            )
            cursor.execute(extrinsic_insert_query, extrinsic_values)

        connection.commit()
        print(f"Block {block_data['number']} inserted successfully")
    except Error as e:
        print(f"Error inserting block data: {e}")

# def query_block_data(connection, query_type, value):
#     """
#     Retrieve stored block data from the MySQL database.

#     Args:
#         connection (mysql.connector.connection.MySQLConnection): The database connection object.
#         query_type (str): The type of query (e.g., 'number', 'hash').
#         value: The value to query for.

#     Returns:
#         dict: The retrieved block data if found, None otherwise.
#     """
#     try:
#         cursor = connection.cursor(dictionary=True)
        
#         if query_type == 'number':
#             query = "SELECT * FROM blocks WHERE number = %s"
#         elif query_type == 'hash':
#             query = "SELECT * FROM blocks WHERE hash = %s"
#         else:
#             print(f"Unsupported query type: {query_type}")
#             return None

#         cursor.execute(query, (value,))
#         block = cursor.fetchone()

#         if block:
#             # Fetch associated extrinsics
#             extrinsics_query = "SELECT * FROM extrinsics WHERE block_number = %s"
#             cursor.execute(extrinsics_query, (block['number'],))
#             extrinsics = cursor.fetchall()
#             block['extrinsics'] = extrinsics

#         return block
#     except Error as e:
#         print(f"Error querying block data: {e}")
#         return None

def close_connection(connection):
    """
    Safely close the MySQL database connection.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
    """
    if connection.is_connected():
        connection.commit()
        connection.close()
        print("MySQL connection closed")
