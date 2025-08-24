from vnstock.explorer.vci import Company
# or
from vnstock import Company

company = Company('TCB')  # Replace with your stock symbol
overview = company.overview()

outstanding_shares= overview['outstanding_share']

#   Column                       Non-Null Count  Dtype 
---  ------                       --------------  ----- 
 0   symbol                       1 non-null      object
 1   id                           1 non-null      object
 2   issue_share                  1 non-null      int64 
 3   history                      1 non-null      object
 4   company_profile              1 non-null      object
 5   icb_name3                    1 non-null      object
 6   icb_name2                    1 non-null      object
 7   icb_name4                    1 non-null      object
 8   financial_ratio_issue_share  1 non-null      int64 
 9   charter_capital              1 non-null      int64 

stock = Vnstock().stock(symbol='REE', source='VCI')
overview= stock.company.overview()