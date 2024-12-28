# Take Home Assignment 

## Overview

This project allow you to place market buy/sell order on Binance and Bybit testnet. It also allows you to fetch the current price of a given symbol on Binance and Bybit testnet.
The client automatically select the best price for execution

## Key Features
- 
- Logging for actions and events taken 

## How to Run

### Prerequisites
1. Docker
2. Python 3.9 or later (for running locally without Docker).
3. .env file to store following credentials
  - `BINANCE_TESTNET_API_KEY`
   - `BINANCE_TESTNET_SECRET_KEY`
   - `BYBIT_TESTNET_API_KEY`
   - `BYBIT_TESTNET_SECRET_KEY`
   - `TESTNET` (set to `"true"` for testnet usage)

### Steps to Run
#### Using Docker Compose (Recommended)
1. Build the Docker image (This run the tests result as well):
```bash
   docker-compose build
```
2. Run tests:
```bash
  docker-compose up
```
3. Run demo 
```
docker-compose run alice python src/demo.py
```
### Running (without Docker)
1. Install dependencies:
```bash
  pip install -r requirements.txt
```
2. Run tests:
```bash
  pytest tests/
```
3. Run demo:
```bash
  python src/demo.py
```

