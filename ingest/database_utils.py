from typing import Dict, Any

def connect_to_database(database_info: Dict[str, Any]):
    if database_info['database'] == 'postgres':
        from postgres_utils import connect_to_postgres
        return connect_to_postgres(
            database_info['database_host'],
            database_info['database_port'],
            database_info['database_name'],
            database_info['database_user'],
            database_info['database_password']
        )
    elif database_info['database'] == 'mysql':
        from mysql_utils import connect_to_mysql
        return connect_to_mysql(
            database_info['database_host'],
            database_info['database_port'],
            database_info['database_name'],
            database_info['database_user'],
            database_info['database_password']
        )
    elif database_info['database'] == 'bigquery':
        from bigquery_utils import connect_to_bigquery
        return connect_to_bigquery(database_info['database_project'], database_info['database_cred_path'])
    else:
        raise ValueError(f"Unsupported database type: {database_info['database']}")

def create_tables(db_connection, database_info: Dict[str, Any], chain: str, relay_chain: str):
    if database_info['database'] == 'postgres':
        from postgres_utils import create_tables as create_postgres_tables
        create_postgres_tables(db_connection, chain, relay_chain)
    elif database_info['database'] == 'mysql':
        from mysql_utils import create_tables as create_mysql_tables
        create_mysql_tables(db_connection, chain, relay_chain)
    elif database_info['database'] == 'bigquery':
        from bigquery_utils import create_blocks_table as create_bigquery_tables
        create_bigquery_tables(db_connection, database_info['database_dataset'], database_info['database_table'])
    else:
        raise ValueError(f"Unsupported database type: {database_info['database']}")


def insert_block_data(database_info, db_connection, block_data, chain_name, relay_chain):
    if database_info['database'] == 'postgres':
        from postgres_utils import connect_to_postgres, close_connection, insert_block_data
        insert_block_data(db_connection, block_data, chain_name, relay_chain)
        close_connection(db_connection)
    elif database_info['database'] == 'mysql':
        from mysql_utils import connect_to_mysql, close_connection, insert_block_data
        insert_block_data(db_connection, block_data, chain_name, relay_chain)
        close_connection(db_connection)
    elif database_info['database'] == 'bigquery':
        from bigquery_utils import connect_to_bigquery, insert_block
        insert_block(db_connection, database_info['database_dataset'], database_info['database_table'], block_data)


def close_connection(db_connection, database_info: Dict[str, Any]):
    if database_info['database'] in ['postgres', 'mysql']:
        if database_info['database'] == 'postgres':
            from postgres_utils import close_connection as close_postgres
        elif database_info['database'] == 'mysql':
            from mysql_utils import close_connection as close_mysql
        
        close_function = locals()[f'close_{database_info["database"]}']
        close_function(db_connection)
    elif database_info['database'] == 'bigquery':
        # BigQuery doesn't require explicit connection closing
        pass
    else:
        raise ValueError(f"Unsupported database type: {database_info['database']}")

def query_last_block(db_connection, database_info: Dict[str, Any], chain: str, relay_chain: str, block_num = None):
    if database_info['database'] == 'postgres':
        from postgres_utils import query
    elif database_info['database'] == 'mysql':
        from mysql_utils import query_block_data as query
    elif database_info['database'] == 'bigquery':
        from bigquery_utils import query
    else:
        raise ValueError(f"Unsupported database type: {database_info['database']}")

    if block_num is None:
        if database_info['database'] == 'bigquery':
            fetch_last_block_query = f"SELECT * FROM {database_info['database_dataset']}.{database_info['database_table']} ORDER BY number DESC LIMIT 1"
        else:
            fetch_last_block_query = f"SELECT * FROM blocks_{relay_chain}_{chain} ORDER BY number DESC LIMIT 1"
    else:
        if database_info['database'] == 'bigquery':
            fetch_last_block_query = f"SELECT * FROM {database_info['database_dataset']}.{database_info['database_table']} WHERE number={block_num} LIMIT 1"
        elif database_info['database'] == 'postgres':
            fetch_last_block_query = f"SELECT * FROM blocks_{relay_chain}_{chain} WHERE number='{block_num}' LIMIT 1"
        else:
            fetch_last_block_query = f"SELECT * FROM blocks_{relay_chain}_{chain} WHERE number={block_num} LIMIT 1"
    return query(db_connection, fetch_last_block_query)

def query_recent_blocks(db_connection, database_info: Dict[str, Any], chain: str, relay_chain: str):
    if database_info['database'] == 'postgres':
        from postgres_utils import query
    elif database_info['database'] == 'mysql':
        from mysql_utils import query_block_data as query
    elif database_info['database'] == 'bigquery':
        from bigquery_utils import query
    else:
        raise ValueError(f"Unsupported database type: {database_info['database']}")

    if database_info['database'] == 'bigquery':
        fetch_last_block_query = f"SELECT * FROM {database_info['database_dataset']}.{database_info['database_table']} ORDER BY number DESC LIMIT 50"
    else:
        fetch_last_block_query = f"SELECT * FROM blocks_{relay_chain}_{chain} ORDER BY number DESC LIMIT 50"

    return query(db_connection, fetch_last_block_query)