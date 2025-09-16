from vnstock import Vnstock


# Default stock symbol for standalone execution
stock_symbol = "REE"

start_date = "2024-01-01"
end_date = "2024-12-31"
interval = "1D"

# Initialize with a default stock symbol and data source
stock = Vnstock().stock(symbol=stock_symbol, source="VCI")
stock_price = stock.quote.history(
    symbol=stock_symbol, start=start_date, end=end_date, interval=interval
)
print(stock_price)
