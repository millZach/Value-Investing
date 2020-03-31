from format_dataframe import format_df
import web_scraper as ws
import pandas as pd
import pandas_datareader as web
import datetime
from dateutil.relativedelta import relativedelta
import time
import json
# pd.set_option('display.max_columns', None)


def stock_price_data(ticker):
    try:
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(years=5)
        df = web.DataReader(ticker, 'yahoo', start_date, end_date)

    except:
        df = pd.DataFrame(
            {'Close': 100000, 'Adj Close': 100000}, index=[ticker])

    return df


def display_profile(ticker):

    # scrape data for profile data from market watch and yahoo
    profile_df = ws.profile(ticker)

    return profile_df


def display_annual_financials(ticker):

    # scraping annual finicial data from marketwatch
    annual_df = ws.annual_data(ticker)

    # Changing data type of strings to floats for numbers
    number_df = annual_df.apply(format_df).T
    annual_df = annual_df.T

    # logic for not dividing by zero
    if all(number_df['Total Sharholders Equity'] != 0):
        annual_df['ROE'] = round(number_df['Net Income'] /
                                 number_df['Total Sharholders Equity'], 2)
    else:
        annual_df['ROE'] = [0 for _ in range(5)]

    if all(number_df['Total Assets'] != 0):
        annual_df['ROA'] = round(number_df['Net Income'] /
                                 number_df['Total Assets'], 2)
    else:
        annual_df['ROA'] = [0 for _ in range(5)]

    if all(number_df['Current Assets'] != 0):
        annual_df['Debt Load'] = round(number_df['Total Liabilities'] /
                                       number_df['Current Assets'], 2)
    else:
        annual_df['Debt Load'] = [0 for _ in range(5)]

    if all(number_df['Interest Expense'] != 0):
        annual_df['Interest Coverage Ratio'] = round(number_df['EBITDA'] /
                                                     number_df['Interest Expense'], 2)
    else:
        annual_df['Interest Coverage Ratio'] = [0 for _ in range(5)]

    return annual_df.T


def display_quarterly_financials(ticker):

    # Scraping quarterly finicial data from marketwatch
    quarterly_df = ws.quarterly_data(ticker)

    return quarterly_df


def warning_signs(ticker):
    annual_df = display_annual_financials(ticker)
    profile_df = ws.profile(ticker)

    annual_df = annual_df.apply(format_df)
    profile_df = profile_df.apply(format_df)

    warning_flags = []

    if annual_df.loc['ROE'].mean() < 0.15:
        warning_flags.append(
            'The mean Return On Equity, over the last 5 years, is less than 15%')

    if all(annual_df.loc['EPS (Basic)'] < 0.0):
        warning_flags.append(
            'EPS growth was negative at one or more points within the last 5 years')

    if annual_df.loc['ROA'].mean() < 0.07:
        warning_flags.append(
            'The mean Return On Assets, over the last 5 years, is less than 7%')

    if all(profile_df.loc['P/E Ratio'] > 20.0):
        warning_flags.append(f'{ticker} has high P/E Ratio')

    if all(profile_df.loc['Current Ratio'] < 1.5):
        warning_flags.append(
            f'{ticker} has a large amount of short-term debt when compared to current assets')

    if annual_df.loc['Long-Term Debt'].iloc[-1] > 5 * annual_df.loc['Net Income'].iloc[-1]:
        warning_flags.append(f'{ticker} Long-Term debt is 5 times Net Income')

    if all(profile_df.loc['Trailing Dividend Yield'] < 0.01):
        warning_flags.append(f'{ticker} pays less than 1% divideds')

    return warning_flags


def present_value_calc(ticker, discount_rate=0.20, margin_safety=0.15):
    annual_df = ws.annual_data(ticker)
    profile_df = ws.profile(ticker)
    price_df = stock_price_data(ticker)

    annual_df = annual_df.apply(format_df).T
    profile_df = profile_df.apply(format_df).T
    estimation_dict = {}

    # Calculating Annual Compounded Growth Rate of EPS
    if all(annual_df['EPS (Basic)'] != 0):
        present_eps = annual_df['EPS (Basic)'][-1]
        past_eps = annual_df['EPS (Basic)'][0]

        # Calculating Annual Compounded Growth Rate of EPS
        # based on 5 years of growth
        cagr = (present_eps / past_eps)**(1 / 4) - 1

        # Estimating EPS 5 years from present day using
        # Compound interest from cagr
        future_eps = present_eps * (1 + cagr)**5
        estimation_dict['CAGR'] = str(round(cagr * 100, 2)) + '%'
        estimation_dict['Future EPS'] = round(future_eps, 2)

        # Estimating future value of company price 5 years from now
        if all(profile_df['P/E Ratio'] != 0):
            price_earnings = profile_df['P/E Ratio'][0]
            future_value = future_eps * price_earnings

            # Determining what a fair price to pay is given expected return
            # which is discount rate and margin of safety
            present_value = future_value / ((1 + margin_safety)**5)
            present_value_safe = present_value - margin_safety * present_value

            estimation_dict['Future Value'] = round(future_value, 2)
            estimation_dict['Purchase Price'] = round(present_value_safe, 2)
            estimation_dict['Current Price'] = round(price_df['Close'][-1], 2)

            if (present_value_safe > price_df['Close'][-1]):
                estimation_dict['Buy or Sell'] = 'Buy'
            else:
                estimation_dict['Buy or Sell'] = 'Sell'

        else:
            estimation_dict['Future Value'] = 'Unknown'
            estimation_dict['Purchase Price'] = 'Unknown'
            estimation_dict['Buy or Sell'] = 'Unknown'
    else:
        estimation_dict['CAGR'] = 'Unknown'
        estimation_dict['Future EPS'] = 'Unknown'
        estimation_dict['Future Value'] = 'Unknown'
        estimation_dict['Purchase Price'] = 'Unknown'
        estimation_dict['Buy or Sell'] = 'Unknown'

    estimation_df = pd.DataFrame(estimation_dict, index=[ticker])

    return estimation_df


# with open('data/warren_companies.json', 'r') as f:
#     ticker_dict = json.load(f)

# tickers = ticker_dict['goodCompanies']
# buy_lst = []

# for ticker in tickers:
#     profile_df = display_profile(ticker)
#     annual_df = display_annual_financials(ticker)
#     price_df = stock_price_data(ticker)
#     warning = warning_signs(ticker, annual_df, profile_df)
#     prediction = present_value_calc(
#         ticker, price_df, profile_df, annual_df, discount_rate=0.20, margin_safety=0.15)

#     print(ticker)
#     if prediction['Buy or Sell'][0] == 'Buy':
#         buy_lst.append(prediction)
#         print(prediction)
#         time.sleep(2)


# print(buy_lst)

# ticker = 'Axp'
# profile_df = display_profile(ticker)
# annual_df = display_annual_financials(ticker)
# price_df = stock_price_data(ticker)
# warning = warning_signs(ticker, annual_df, profile_df)
# prediction = present_value_calc(
#     ticker, price_df, profile_df, annual_df, discount_rate=0.20, margin_safety=0.15)

# # print(profile_df)
# # print(annual_df)
# # print(price_df)

# print(warning)
# # print(prediction)
