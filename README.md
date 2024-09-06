# dotlake-sidecar

This repository contains the necessary components to set up and run a data ingestion pipeline for Polkadot-based blockchains using Substrate API Sidecar and a custom block ingest service.

## Overview

The dotlake-sidecar project facilitates the extraction and processing of blockchain data from Polkadot-based networks. It uses two main components:

1. Substrate API Sidecar
2. Custom Block Ingest Service

These components work together to provide a robust solution for capturing and processing blockchain data.

## Components

### 1. Substrate API Sidecar

[Substrate API Sidecar](https://github.com/paritytech/substrate-api-sidecar) is an open-source REST service that runs alongside Substrate nodes. It provides a way to access blockchain data through a RESTful API, making it easier to query and retrieve information from the blockchain.

### 2. Custom Block Ingest Service

The custom block ingest service is a Docker container that processes and stores blockchain data. It is designed to work in conjunction with the Substrate API Sidecar to ingest blocks and related information from the specified blockchain. The service utilizes DuckDB, an embedded analytical database, as part of its data flow:

1. The service ingests blockchain data from the Substrate API Sidecar.
2. The ingested data is then processed and transformed as needed.
3. The processed data is stored in DuckDB.

## How It Works

The system operates using the following workflow:

1. The Substrate API Sidecar connects to a specified WebSocket endpoint (WSS) of a Substrate-based blockchain node.
2. The Sidecar exposes a RESTful API on port 8080, allowing easy access to blockchain data.
3. The custom block ingest service connects to the same WSS endpoint and begins processing blocks.
4. The ingest service stores the processed data, making it available for further analysis or querying.

## Usage

To run the dotlake-sidecar, use the provided `dotlakeIngest.sh` script. This script sets up both the Substrate API Sidecar and the custom block ingest service as Docker containers.

Example usage:

If you wish to start the ingest service for polkadot, you can use the following command:

```
sh dotlakeIngest.sh --chain polkadot --relay-chain polkadot --wss wss://rpc.ibp.network/polkadot
```


