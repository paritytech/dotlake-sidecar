# dotlake-community

A data ingestion pipeline for Polkadot-based blockchains that combines Substrate API Sidecar with a custom block ingest service.

## Overview

dotlake-community enables comprehensive data extraction and processing from Polkadot-based networks through three key components:

- **Substrate API Sidecar**: REST service for blockchain data access
- **Custom Block Ingest Service**: Data processing and storage pipeline
- **Apache Superset**: Data visualization and analytics

## Prerequisites

- Docker and Docker Compose
- Access to a Substrate-based blockchain node (WSS endpoint)
- Sufficient storage space for blockchain data

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/dotlake-community.git
cd dotlake-community
```

2. Configure your settings in `config.yaml`:
```yaml
relay_chain: Polkadot
chain: Polkadot
wss: wss://polkadot-rpc.dwellir.com
create_db: true  # Set to true if database needs to be created
retain_db: true  # Set to true to retain database after the end of process.
# databases:
#   - type: postgres
#     host: xx.xx.xx.xx
#     port: 5432
#     name: dotlake
#     user: *****
#     password: ******
ingest_mode: live  # live/historical
start_block: 1
end_block: 100
```

3. Start the ingestion pipeline:
```bash
sh dotlakeIngest.sh
```

4. To stop the ingestion and cleanup resources:
```bash
sh cleanup.sh
```

## Architecture

### 1. Substrate API Sidecar
- Connects to blockchain node via WebSocket
- Exposes REST API on port 8080
- Provides standardized access to blockchain data

### 2. Custom Block Ingest Service
Processes blockchain data through multiple stages:
1. Data extraction from Sidecar API
2. Transformation and enrichment
3. Storage in PostgreSQL

### 3. Apache Superset Integration
- Custom visualization capabilities
- Direct connection to stored data

## Development

To contribute or modify:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

