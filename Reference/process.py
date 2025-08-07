from vnstock import Vnstock
import pandas as pd
from vnstock.core.utils.transform import flatten_hierarchical_index
stock = Vnstock().stock(symbol='ACB', source='VCI')
ratios = stock.finance.ratio(period='year', lang='vi',dropna=True)

#from vnstock.core.utils.transform import flatten_hierarchical_index
# Apply to MultiIndex DataFrame
flattened_df = flatten_hierarchical_index(
    ratios, #multi-index df
    separator="_", #separator for flattened columns
    handle_duplicates=True, #handle duplicate column names
    drop_levels=0  # or specify levels to drop
)

flattened_df.to_excel('ratios.xlsx')