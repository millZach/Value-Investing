import pandas as pd
import requests
import bs4 as bs
import datetime
import json
import time
from data.data_to_json import JSONEncoder
# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_columns', None)


def get_sp500_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        request = requests.get(url)
        grab_sp500_data = pd.read_html(url)[0].set_index('Symbol')
        sp500_df = grab_sp500_data[['Security']]
        tickers = []
        display = []
        dropdown_dict = {}
        i = 0
        for index in sp500_df.index:
            tickers.append(index)
            display.append(index + ' - ' + sp500_df.Security.values[i])
            i += 1

        dropdown_dict = {'value': tickers, 'label': display}

        return dropdown_dict

    except requests.ConnectionError:
        print("There was an error with trying to connect to the URL")


def profile(ticker):

    profile_dict = {
        'Date Retrieved': f'{datetime.date.today()}',
        'Ticker': ticker.upper(),
        'Name': '-',
        'Description': '-',
        'Sector': '-',
        'Industry': '-',
        'P/E Ratio': '-',
        'P/Bv Ratio': '-',
        'Current Ratio': '-',
        'Trailing Dividend Yield': '-',
        'Short Ratio': '-'
    }

    mw_base_url = "https://www.marketwatch.com/investing/stock"
    yahoo_base_url = "https://finance.yahoo.com/quote/"
    try:
        profile_url = mw_base_url + f'/{ticker.lower()}/profile'
        profile_response = requests.get(profile_url)
        yahoo_url = yahoo_base_url + \
            f'{ticker.upper()}/key-statistics?p={ticker.upper()}'
        yahoo_response = requests.get(yahoo_url)

    except:
        profile_df = pd.DataFrame(profile_dict, index=[f'{ticker}'])
        return profile_df.T

    profile_soup = bs.BeautifulSoup(profile_response.text, 'lxml')
    yahoo_soup = bs.BeautifulSoup(yahoo_response.text, 'lxml')

    try:
        profile_dict['Name'] = profile_soup.find_all(
            'p', {'class': 'companyname'})[0].text
    except:
        profile_dict['Name'] = 'Not Found'

    try:
        profile_dict['Description'] = str(profile_soup.find_all('div', {'class': 'full'})[
                                          0].text).split('\n\r\n                ')[1].split('\r\n            \n')[0]
    except:
        profile_dict['Description'] = 'Not Found'

    profile_titles = profile_soup.find_all('p', {'class': 'column'})
    for title in profile_titles:
        if 'Sector' in title.text:
            profile_dict['Sector'] = [title.find_next_siblings(
                'p', {'class': 'data lastcolumn'})[0].text]

        if 'Industry' in title.text:
            profile_dict['Industry'] = [title.find_next_siblings(
                'p', {'class': 'data lastcolumn'})[0].text]

        if 'P/E Current' in title.text:
            profile_dict['P/E Ratio'] = [title.find_next_siblings(
                'p', {'class': 'data lastcolumn'})[0].text]

        if 'Price to Book Ratio' in title.text:
            profile_dict['P/Bv Ratio'] = [title.find_next_siblings(
                'p', {'class': 'data lastcolumn'})[0].text]

        if 'Current Ratio' in title.text:
            profile_dict['Current Ratio'] = [title.find_next_siblings(
                'p', {'class': 'data lastcolumn'})[0].text]

    yahoo_title = yahoo_soup.find_all('td')

    for title in yahoo_title:
        if 'Short Ratio' in title.text:
            profile_dict['Short Ratio'] = title.find_next_siblings('td')[
                0].text
        if 'Trailing Annual Dividend Yield' in title.text:
            profile_dict['Trailing Dividend Yield'] = title.find_next_siblings('td')[
                0].text

    profile_df = pd.DataFrame(profile_dict, index=[f'{ticker}'])

    return profile_df.T


def annual_data(ticker):

    annual_dict = {
        'Year': [x for x in [1, 2, 3, 4, 5]],
        'EPS (Basic)': ['-' for _ in range(5)],
        'EPS Growth': ['-' for _ in range(5)],
        'Net Income': ['-' for _ in range(5)],
        'Interest Expense': ['-' for _ in range(5)],
        'Research & Development': ['-' for _ in range(5)],
        'EBITDA': ['-' for _ in range(5)],
        'Total Assets': ['-' for _ in range(5)],
        'Current Assets': ['-' for _ in range(5)],
        'Total Liabilities': ['-' for _ in range(5)],
        'Current Liabilities': ['-' for _ in range(5)],
        'Total Sharholders Equity': ['-' for _ in range(5)],
        'Long-Term Debt': ['-' for _ in range(5)]
    }

    mw_base_url_fs = "https://www.marketwatch.com/investing/stock"
    mw_base_url_bs = "https://www.marketwatch.com/investing/stock"

    try:
        fa_url = mw_base_url_fs + f'/{ticker.lower()}/financials'
        fa_response = requests.get(fa_url)
    except:
        annual_df = pd.DataFrame(annual_dict).set_index('Year')
        return annual_df.T

    try:
        bsa_url = mw_base_url_bs + \
            f'/{ticker.lower()}/financials/balance-sheet'
        bsa_response = requests.get(bsa_url)
    except:
        annual_df = pd.DataFrame(annual_dict).set_index('Year')
        return annual_df.T

    fa_soup = bs.BeautifulSoup(fa_response.text, 'lxml')
    bsa_soup = bs.BeautifulSoup(bsa_response.text, 'lxml')

    fa_date_table = fa_soup.find_all('th', {'scope': 'col'})
    annual_dict['Year'] = [
        date.text for date in fa_date_table if date.text][0:5]

    # Validates that data is present on the page
    if len(annual_dict['Year']) == 0:
        annual_dict['Year'] = [x for x in [1, 2, 3, 4, 5]]
        annual_df = pd.DataFrame(annual_dict).set_index('Year')
        return annual_df.T

    fa_table_data = fa_soup.find_all('td', {'class': 'rowTitle'})

    for title in fa_table_data:
        if ' EPS (Basic)' == title.text:
            annual_dict['EPS (Basic)'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if 'EPS (Basic) Growth' in title.text:
            annual_dict['EPS Growth'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' Net Income' == title.text:
            annual_dict['Net Income'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' Interest Expense' == title.text:
            annual_dict['Interest Expense'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' EBITDA' == title.text:
            annual_dict['EBITDA'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if 'Research &' in title.text:
            annual_dict['Research & Development'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

    bsa_title = bsa_soup.find_all('td', {'class': 'rowTitle'})

    for title in bsa_title:
        if title.text == ' Total Assets':
            annual_dict['Total Assets'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == 'Total Current Assets':
            annual_dict['Current Assets'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == ' Total Liabilities':
            annual_dict['Total Liabilities'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == ' Total Current Liabilities':
            annual_dict['Current Liabilities'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == " Total Shareholders' Equity":
            annual_dict['Total Sharholders Equity'] = [
                td.text for td in title.find_next_siblings(attrs={'class': 'valueCell'}) if td.text]

        if title.text == 'Long-Term Debt':
            annual_dict['Long-Term Debt'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

    annual_df = pd.DataFrame(annual_dict).set_index('Year')

    return annual_df.T


def quarterly_data(ticker):
    quarter_dict = {
        'Quarter': [x for x in [1, 2, 3, 4, 5]],
        'EPS (Basic)': ['-' for _ in range(5)],
        'EPS Growth': ['-' for _ in range(5)],
        'Net Income': ['-' for _ in range(5)],
        'Interest Expense': ['-' for _ in range(5)],
        'Research & Development': ['-' for _ in range(5)],
        'EBITDA': ['-' for _ in range(5)],
        'Total Assets': ['-' for _ in range(5)],
        'Current Assets': ['-' for _ in range(5)],
        'Total Liabilities': ['-' for _ in range(5)],
        'Current Liabilities': ['-' for _ in range(5)],
        'Total Sharholders Equity': ['-' for _ in range(5)],
        'Long-Term Debt': ['-' for _ in range(5)]
    }

    mw_base_url_fq = "https://www.marketwatch.com/investing/stock"
    mw_base_url_bs = "https://www.marketwatch.com/investing/stock"

    try:
        fq_url = mw_base_url_fq + \
            f'/{ticker.lower()}/financials/income/quarter'
        fq_response = requests.get(fq_url)
    except:
        quarter_df = pd.DataFrame(quarter_dict).set_index('Quarter')
        return quarter_df.T

    try:
        bsq_url = mw_base_url_bs + \
            f'/{ticker.lower()}/financials/balance-sheet/quarter'
        bsq_response = requests.get(bsq_url)
    except:
        quarter_df = pd.DataFrame(quarter_dict).set_index('Quarter')
        return quarter_df.T

    fq_soup = bs.BeautifulSoup(fq_response.text, 'lxml')
    bsq_soup = bs.BeautifulSoup(bsq_response.text, 'lxml')

    fq_date_table = fq_soup.find_all('th', {'scope': 'col'})
    quarter_dict['Quarter'] = [
        quart.text for quart in fq_date_table if quart.text][0:5]

    # Validates that data is present on the page
    if len(quarter_dict['Quarter']) == 0:
        quarter_dict['Quarter'] = [x for x in [1, 2, 3, 4, 5]]
        quarter_df = pd.DataFrame(quarter_dict).set_index('Quarter')
        return quarter_df.T

    fq_table_data = fq_soup.find_all('td', {'class': 'rowTitle'})
    for title in fq_table_data:
        if ' EPS (Basic)' == title.text:
            quarter_dict['EPS (Basic)'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if 'EPS (Basic) Growth' in title.text:
            quarter_dict['EPS Growth'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' Net Income' == title.text:
            quarter_dict['Net Income'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' Interest Expense' == title.text:
            quarter_dict['Interest Expense'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if ' EBITDA' == title.text:
            quarter_dict['EBITDA'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]
        if 'Research &' in title.text:
            quarter_dict['Research & Development'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

    bsq_title = bsq_soup.find_all('td', {'class': 'rowTitle'})

    for title in bsq_title:
        if title.text == ' Total Assets':
            quarter_dict['Total Assets'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == 'Total Current Assets':
            quarter_dict['Current Assets'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == ' Total Liabilities':
            quarter_dict['Total Liabilities'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == ' Total Current Liabilities':
            quarter_dict['Current Liabilities'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

        if title.text == " Total Shareholders' Equity":
            quarter_dict['Total Sharholders Equity'] = [
                td.text for td in title.find_next_siblings(attrs={'class': 'valueCell'}) if td.text]

        if title.text == 'Long-Term Debt':
            quarter_dict['Long-Term Debt'] = [td.text for td in title.find_next_siblings(
                attrs={'class': 'valueCell'}) if td.text]

    quarter_df = pd.DataFrame(quarter_dict).set_index('Quarter')

    return quarter_df.T

# print(annual_data('aapl'))
# print(quarterly_data('aapl'))


if __name__ == '__main__':
    start_time = time.time()

    sp_500_dict = get_sp500_companies()
    tickers = sp_500_dict['value']
    # tickers = ['aapl', 'wrk', 'tsla']
    stock_dict = {}
    i = 1
    for ticker in tickers:
        print(ticker + ' ' + f'{i}')
        stock_dict[f'{ticker}'] = [
            profile(ticker),
            annual_data(ticker),
            quarterly_data(ticker)
        ]

        with open('data/sp500_updated.json', 'w') as fp:
            json.dump(stock_dict, fp, cls=JSONEncoder)

        print("--- %s seconds ---" % (time.time() - start_time))
        print(stock_dict[f'{ticker}'][1].head())
        i += 1
        time.sleep(5)
    # print(stock_dict['tsla'])

    print("--- %s seconds ---" % (time.time() - start_time))
