from db import get_tickers
from lib import RestMarket 

if __name__ == '__main__':
    market = RestMarket()

    data = market.get_market_ticker(instId='BTC-USDT-SWAP')
    print(data[0])



