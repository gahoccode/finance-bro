from vnstock import Company
stock_symbol = 'REE'


# Initialize Company class directly
company = Company(symbol=stock_symbol)

# Get company officers information
management_team = company.officers(lang='en')
print(management_team)

from vnstock import Vnstock
stock = Vnstock().stock(symbol=stock_symbol, source='VCI')
company_info = stock.company
ownership = company_info.shareholders()
print(ownership)

from vnstock import Vnstock
# Initialize with a default stock symbol and data source
stock = Vnstock().stock(symbol=stock_symbol, source='VCI')
company_info = stock.company
ownership_percentage = company_info.shareholders()
print(ownership_percentage)
