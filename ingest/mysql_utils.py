# MySQL Database Connection Utilities
import mysql.connector
from mysql.connector import Error
import json
import pandas as pd

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

def create_tables(connection, chain, relay_chain):
    """
    Create necessary tables in the MySQL database if they don't exist.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
    """
    try:
        delete_table(connection, f"blocks_{relay_chain}_{chain}")
        cursor = connection.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS blocks_{relay_chain}_{chain} (
                relay_chain VARCHAR(255),
                chain VARCHAR(255),
                timestamp BIGINT,
                number VARCHAR(255) PRIMARY KEY,
                hash VARCHAR(255),
                parenthash VARCHAR(255),
                stateroot VARCHAR(255),
                extrinsicsroot VARCHAR(255),
                authorid VARCHAR(255),
                finalized BOOLEAN,
                extrinsics JSON,
                onfinalize JSON,
                oninitialize JSON,
                logs JSON
            )
        """)
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS extrinsics (
        #         block_number VARCHAR(255),
        #         pallet VARCHAR(255),
        #         method VARCHAR(255),
        #         signature VARCHAR(255),
        #         signer_id VARCHAR(255),
        #         events JSON,
        #         FOREIGN KEY (block_number) REFERENCES blocks(number)
        #     )
        # """)
        connection.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def insert_block_data(connection, block_data, chain_name, relay_chain):
    """
    Insert processed block data into the MySQL database.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
        block_data (dict): The block data to be inserted.
    """
    try:
        cursor = connection.cursor()
        
        # Insert block data
        block_insert_query = f"""
        INSERT INTO blocks_{relay_chain}_{chain_name} (relay_chain, chain, timestamp, number, hash, parenthash, stateroot, extrinsicsroot, authorid, finalized, extrinsics, onfinalize, oninitialize, logs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        block_values = (
            block_data['relay_chain'], block_data['chain'], block_data['timestamp'],
            block_data['number'], block_data['hash'], block_data['parentHash'],
            block_data['stateRoot'], block_data['extrinsicsRoot'], block_data['authorId'],
            block_data['finalized'], json.dumps(block_data['extrinsics']),
            json.dumps(block_data['onFinalize']), json.dumps(block_data['onInitialize']),
            json.dumps(block_data['logs'])
        )
        cursor.execute(block_insert_query, block_values)

        # Insert extrinsics data
        # extrinsic_insert_query = """
        # INSERT INTO extrinsics (block_number, pallet, method, signature, signer_id)
        # VALUES (%s, %s, %s, %s, %s)
        # """
        # for extrinsic in block_data['extrinsics']:
        #     extrinsic_values = (
        #         block_data['number'], extrinsic['method']['pallet'], extrinsic['method']['method'],
        #         extrinsic['signature'].get('signature'), extrinsic['signature'].get('signer', {}).get('id')
        #     )
        #     cursor.execute(extrinsic_insert_query, extrinsic_values)

        connection.commit()
        print(f"Block {block_data['number']} inserted successfully")
    except Error as e:
        print(f"Error inserting block data: {e}")

def query_block_data(connection, query_str):
    """
    Execute a given SQL query on the MySQL database and return the results as a DataFrame.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
        query_str (str): The SQL query string to execute.

    Returns:
        pandas.DataFrame: The query results as a DataFrame, or None if an error occurs.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query_str)
        results = cursor.fetchall()
        df = pd.DataFrame(results)
        return df
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def delete_table(connection, table_name):
    """
    Delete a table from the MySQL database if it exists.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
        table_name (str): The name of the table to delete.
    """
    try:
        cursor = connection.cursor()
        drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(drop_table_query)
        connection.commit()
        print(f"Table '{table_name}' deleted successfully (if it existed)")
    except Error as e:
        print(f"Error deleting table '{table_name}': {e}")
    finally:
        if cursor:
            cursor.close()


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
