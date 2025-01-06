# Take Home Assignment 

## Overview

This project allow you to place market buy/sell order on Binance and Bybit testnet. It also allows you to fetch the current price of a given symbol on Binance and Bybit testnet.
The client automatically select the best price for execution

## Key Features
- Market/Sell Orders: Automatically places buy or sell orders on the exchange with the best price.
- Best Price Aggregator: Compares prices across Binance and Bybit 
- Logging for actions and events taken 
- Design Extensibility: Easily add new exchanges or trading pairs by implementing the required interfaces.

## Known Limitations
### Current Design Decisions
1. Using Binance GET `/ticker/price` Instead of Bid/Ask Prices which simplifies development but may not reflect the true actionable price for buying or selling
2. We could fix this to Fetch bid/ask prices (`GET /depth`) to calculate actionable prices for more accurate decision-making.
3. The client uses REST APIs instead of WebSockets for simplicity
4. Only supports Binance and Bybit
5. Currently, the demo code does not dynamically calculate the optimal quantity based on account balances.
6. The system is single-threaded and does not leverage concurrency or parallelism for fetching prices or placing orders.

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


## Testing
- tests can be locally or using Docker Compose
- CI/CD Tests are run automatically on every push to the repository


## What I would have done with more time
- Add more test coverage 
- Add more granular error handling
- Integrate more exchanges
- Use Websocket for performance and reduce overhead of RESTAPI
- Demo are not dynamically calculate when it comes to placing order. A system would benefit from optimal quantity based on accout balances
- Store log locally by integrating into something like Kibana for observability  
- This system HFT ready but can be further optimized by introducing concurrency and parallelism

