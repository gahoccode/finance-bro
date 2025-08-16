import matplotlib.pyplot as plt
from vnstock import Screener

# Create screener for banking sector
source = "TCBS"  # 'TCBS' or 'VCI'
bank_params = {
    "exchangeName": "HOSE,HNX,UPCOM",
    # "industryName": "Banks",
    # "marketCap": (50000, 900000),  # Large banks only
    # "roe": (10, 50)                  # Good profitability
    "industryName": "Banks",
}
industry_list = [
    "Personal & Household Goods",
    "Chemicals",
    "Basic Resources",
    "Food & Beverage",
    "Financial Services",
    "Real Estate",
    "Industrial Goods & Services",
    "Banks",
    "Telecommunications",
    "Insurance",
    "Construction & Materials",
    "Media",
    "Retail",
    "Health Care",
    "Utilities",
    "Travel & Leisure",
    "Oil & Gas",
    "Technology",
    "Automobiles & Parts",
]  # 19 industries


screener = Screener(source=source)
banks = screener.stock(params=bank_params, limit=1700, lang="en")

# 4. Compare ROE of the banks
plt.figure(figsize=(12, 6))
plt.bar(banks["ticker"], banks["roe"])
plt.title("ROE Comparison of Vietnamese Banks")
plt.xlabel("Bank Ticker")
plt.ylabel("Return on Equity (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"bank_roe_comparison_{source}.png")
