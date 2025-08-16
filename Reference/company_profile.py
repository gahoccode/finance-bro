from vnstock import Company

stock_symbol = "REE"


# Initialize Company class directly
company = Company(symbol=stock_symbol)

# Get company officers information
management_team = company.officers()
print(management_team)

from vnstock import Vnstock

# Initialize with a default stock symbol and data source
stock = Vnstock().stock(symbol=stock_symbol, source="VCI")
company_info = stock.company
ownership_percentage = company_info.shareholders()
print(ownership_percentage)


from vnstock.explorer.vci import Company

company = Company("REE")
affiliate = company.affiliate()

trading_stats = company.trading_stats()


from vnstock import Company

company = Company(symbol="REE", source="TCBS")
insider_trading_info = company.insider_deals()
