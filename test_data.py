import json
import pandas as pd

# with open('sp500.json', 'r') as fp:
# stock_json = json.load(fp)


a = pd.read_json(json.load(open('scraper/data/sp500.json'))['AAPL'][0])
a = a.loc[['Date Retrieved', 'Name', 'Description', 'Industry', 'Sector',
           'P/Bv Ratio', 'P/E Ratio', 'Short Ratio',
           'Trailing Dividend Yield', 'Current Ratio']]
print(a)
