import os
from google.cloud import bigquery
from google.oauth2 import service_account
import json

def connect_to_bigquery(project_id, credentials_path):
    """
    Connect to BigQuery.
    
    Args:
        project_id (str): The Google Cloud project ID.
        credentials_path (str): Path to the service account credentials JSON file.
    
    Returns:
        google.cloud.bigquery.client.Client: A BigQuery client.
    """
    # if not os.path.exists(credentials_path):
    #     raise FileNotFoundError(f"Credentials file not found at {credentials_path}")

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(credentials_path)
    )

    return bigquery.Client(credentials=credentials, project=project_id)

def create_blocks_table(client, dataset_id, table_id, project_id):
    """
    Create the blocks table if it doesn't exist.
    
    Args:
        client (google.cloud.bigquery.client.Client): A BigQuery client.
        dataset_id (str): The ID of the dataset to create the table in.
        table_id (str): The ID of the table to create.
        chain (str): The name of the chain.
        relay_chain (str): The name of the relay chain.
    """
    schema = [
        bigquery.SchemaField("relay_chain", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("chain", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("number", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("hash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("parenthash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("stateroot", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("extrinsicsroot", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("authorid", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("finalized", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("extrinsics", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("method", "RECORD", fields=[
                bigquery.SchemaField("pallet", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("method", "STRING", mode="REQUIRED")
            ]),
            bigquery.SchemaField("signature", "RECORD", fields=[
                bigquery.SchemaField("signature", "STRING"),
                bigquery.SchemaField("signer", "STRING")
            ]),
            bigquery.SchemaField("nonce", "STRING"),
            bigquery.SchemaField("args", "STRING"),
            bigquery.SchemaField("tip", "STRING"),
            bigquery.SchemaField("hash", "STRING"),
            bigquery.SchemaField("info", "STRING"),
            bigquery.SchemaField("era", "RECORD", fields=[
                bigquery.SchemaField("immortalera", "STRING"),
                bigquery.SchemaField("mortalera", "STRING", mode='REPEATED')
            ]),
            bigquery.SchemaField("events", "RECORD", mode='REPEATED', fields=[
                bigquery.SchemaField("method", "RECORD", fields=[
                    bigquery.SchemaField("pallet", "STRING"),
                    bigquery.SchemaField("method", "STRING")
                ]),
                bigquery.SchemaField("data", "STRING")
            ]),
            bigquery.SchemaField("success", "BOOLEAN"),
            bigquery.SchemaField("paysfee", "BOOLEAN"),
        ]),
        bigquery.SchemaField("onfinalize", "RECORD", fields=[
            bigquery.SchemaField("events", "RECORD", mode='REPEATED', fields=[
                bigquery.SchemaField("method", "RECORD", fields=[
                    bigquery.SchemaField("pallet", "STRING"),
                    bigquery.SchemaField("method", "STRING")
                ]),
                bigquery.SchemaField("data", "STRING")
            ]),
        ]),
        bigquery.SchemaField("oninitialize", "RECORD", fields=[
            bigquery.SchemaField("events", "RECORD", mode='REPEATED', fields=[
                bigquery.SchemaField("method", "RECORD", fields=[
                    bigquery.SchemaField("pallet", "STRING"),
                    bigquery.SchemaField("method", "STRING")
                ]),
                bigquery.SchemaField("data", "STRING")
            ]),
        ]),
        bigquery.SchemaField("logs", "RECORD", mode='REPEATED', fields=[
            bigquery.SchemaField("type", "STRING"),
            bigquery.SchemaField("index", "STRING"),
            bigquery.SchemaField("value", "STRING")
        ])
    ]

    table = bigquery.Table(f"{project_id}.{dataset_id}.{table_id}", schema=schema)
    table = client.create_table(table, exists_ok=True)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

def insert_block(client, dataset_id, table_id, block_data):
    """
    Insert a block into the BigQuery table.
    
    Args:
        client (google.cloud.bigquery.client.Client): A BigQuery client.
        dataset_id (str): The ID of the dataset containing the table.
        table_id (str): The ID of the table to insert into.
        block_data (dict): The block data to insert.
    """
    table_ref = client.dataset(dataset_id).table(table_id)
    errors = client.insert_rows_json(table_ref, [block_data])
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print(f"Inserted 1 row into {dataset_id}.{table_id}")

def update_block(client, dataset_id, table_id, block_number, update_data):
    """
    Update a block in the BigQuery table.
    
    Args:
        client (google.cloud.bigquery.client.Client): A BigQuery client.
        dataset_id (str): The ID of the dataset containing the table.
        table_id (str): The ID of the table to update.
        block_number (str): The block number to update.
        update_data (dict): The data to update the block with.
    """
    query = f"""
    UPDATE `{client.project}.{dataset_id}.{table_id}`
    SET {', '.join([f"{k} = @{k}" for k in update_data.keys()])}
    WHERE number = @block_number
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("block_number", "STRING", block_number),
            *[bigquery.ScalarQueryParameter(k, "STRING", v) for k, v in update_data.items()]
        ]
    )
    
    query_job = client.query(query, job_config=job_config)
    query_job.result()
    
    print(f"Updated block {block_number} in {dataset_id}.{table_id}")


def query(client, query_str):
    """
    Execute a query on BigQuery and return the results as a dataframe.
    
    Args:
        client (google.cloud.bigquery.client.Client): A BigQuery client.
        query_str (str): The query string to execute.
        
    Returns:
        pandas.DataFrame: The query results as a DataFrame.
    """
    query_job = client.query(query_str)
    results = query_job.result()
    df = results.to_dataframe()
    
    return df

