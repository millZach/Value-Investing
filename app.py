import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
import all_stock_display as asd
from web_scraper import sp500_dropdown


app = dash.Dash()

app.layout = html.Div('HELLO WORLD')


if __name__ == '__main__':
    app.run_server(debug=True)
