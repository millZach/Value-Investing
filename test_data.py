import json
import pandas as pd
from format_dataframe import format_df
from web_scraper import get_sp500_companies, sp500_dropdown
# pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)


sp500_df = get_sp500_companies()
# bg_companies = []


def warren_companies(sp500_df):
    warren_tickers = []

    for ticker in sp500_df.index:
        # Loading stock data from sp500_json
        profile_df = pd.read_json(
            json.load(open('data/sp500.json'))[ticker][0])
        annual_df = pd.read_json(json.load(open('data/sp500.json'))[ticker][1])
        quarterly_df = pd.read_json(
            json.load(open('data/sp500.json'))[ticker][2])

        # Rearranging the index values for the stock profile as they were loaded wrong
        profile_df = profile_df.loc[['Date Retrieved', 'Name', 'Description', 'Industry', 'Sector',
                                     'P/Bv Ratio', 'P/E Ratio', 'Short Ratio', 'Trailing Dividend Yield', 'Current Ratio']]

        # Formating the numbers from strings to floats
        profile_df = profile_df.apply(format_df)
        annual_df = annual_df.apply(format_df).T
        quarterly_df = quarterly_df.apply(format_df).T

        if annual_df['Net Income'].all() > 0:
            # print(ticker)
            annual_df['ROE'] = round(annual_df['Net Income'] /
                                     annual_df['Total Sharholders Equity'], 2)
            annual_df['ROA'] = round(annual_df['Net Income'] /
                                     annual_df['Total Assets'], 2)
            annual_df['Debt Load'] = round(
                annual_df['Total Liabilities'] / annual_df['Current Assets'], 2)

            if annual_df['Interest Expense'].all() > 0:
                annual_df['Interest Coverage Ratio'] = round(
                    annual_df['EBITDA'] / annual_df['Interest Expense'], 2)
            else:
                annual_df['Interest Coverage Ratio'] = [0 for _ in range(5)]

            # if annual_df['ROE'].mean() > .15:
            #     if all(annual_df['EPS (Basic)'] > 0.0):
            #         # if profile_df.loc['P/Bv Ratio'].all() < 1.2:
            #         if all(profile_df.loc['P/E Ratio'] < 20.0):
            #             if all(profile_df.loc['Trailing Dividend Yield'] > 0.01):
            #                 if all(profile_df.loc['Current Ratio'] > 1.5):
            #                     if annual_df['ROA'].mean() > 0.07 and annual_df['ROA'].iloc[-1] > 0.07:
            #                         if annual_df['Debt Load'].iloc[-1] < 1.1:
            #                             bg_companies.append(ticker)

            if annual_df['ROE'].mean() > 0.15:
                if all(annual_df['EPS (Basic)'] > 0.0):
                    if annual_df['ROA'].mean() > 0.07 and annual_df['ROA'].iloc[-1] > 0.07:
                        if annual_df['Long-Term Debt'].iloc[-1] < 5 * annual_df['Net Income'].iloc[-1]:
                            if annual_df['Interest Coverage Ratio'].iloc[-1] > 3.0:
                                warren_tickers.append(ticker)

    save_tickers = {'goodCompanies': warren_tickers}
    with open('data/warren_companies.json', 'w') as f:
        json.dump(save_tickers, f)


with open('data/warren_companies.json', 'r') as f:
    b = json.load(f)

dict_list = []
for dic in a:
    for tic in b['goodCompanies']:
        if tic == dic['value']:
            dict_list.append({'value': tic, 'label': dic['label']})
