import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
import all_stock_display as asd
from web_scraper import sp500_dropdown
from dash.dependencies import Input, Output



app_colors = {
    'background': '#FFFFFF',
    'text': '#606060',
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [   html.Div(
            className='row',
            children=[
                html.Div(
                    className='col-md-6',
                    children=[
                        html.H1('Value Investing', style={'font-size': '50px'}),
                        html.H1('Choose A Company', style={'font-size': '36px'}),
                        dcc.Dropdown(
                            id='company-dropdown',
                            options=sp500_dropdown() + [{'value': 'SPY', 'label': 'SPY - ETF'}],
                            value='AAPL',
                            ),
                        dcc.Graph(id='stock-price')
                    ],
                    style={'float': 'left','width': '50%', 'display': 'inline-block'}),

                html.Div(
                    className='col-md-6',
                    children=[
                        html.H1('Annual Financials', style={'font-size': '40px'}),
                        html.Table(id='annual-table')],
                        style={'float': 'left','width': '45%', 'display': 'inline-block', 'padding-top': '10px', 'padding-left': '30px',}
                    )]),
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='col-md-6',
                    children=[
                        html.H1('Company Profile', style={'font-size': '40px'}),
                        html.Table(id='profile-table')],
                    style={'float': 'left', 'width': '50%', 'padding-top': '10px', 'display': 'inline-block'}
                    ),

                html.Div(
                    className='col-md-6',
                    children=[
                        html.H1('Warning Flags', style={'font-size': '40px'}),
                        html.Table(id='warning-signs'),
                        html.H1('Price Prediction', style={'font-size': '40px', 'padding-top': '10px'}),
                        html.Table(id='price-prediction')],
                    style={'float': 'left', 'width': '45%', 'padding-top': '10px', 'padding-left':'30px', 'display': 'inline-block'}
                    )
                ]
            ),

    ],


    style={'margin-top': '30px', 'height': '2000px', }

)

def generate_table(dataframe, max_rows=16):
    return [html.Tr([html.Th(col) for col in dataframe.columns])] + [html.Tr([
        html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
    ]) for i in range(min(len(dataframe), max_rows))]

annual_df = 0
profile_df = 0


@app.callback(
    Output('stock-price', 'figure'),
    [Input('company-dropdown', 'value')])
def stock_price_plot(stock_ticker):
    price_df = asd.stock_price_data(stock_ticker)

    return {
        'data': [
            {'x': price_df.index, 'y': price_df.Close, 'name': 'Close'},
            {'x': price_df.index, 'y': price_df.Close.rolling(window=200, min_periods=0).mean(), 'name': '200 SMA'}
        ],
        'layout': dict(
            title=f'5 Year Stock Price Data For {stock_ticker}',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Close'},
        )
    }

@app.callback(
    Output('profile-table', 'children'),
    [Input('company-dropdown', 'value')])
def profile_data(stock_ticker):
    profile_df = asd.display_profile(stock_ticker).reset_index()

    return generate_table(profile_df)

@app.callback(
    Output('annual-table', 'children'),
    [Input('company-dropdown', 'value')])
def annual_data(stock_ticker):
    annual_df = asd.display_annual_financials(stock_ticker).reset_index()

    return generate_table(annual_df)

@app.callback(
    Output('warning-signs', 'children'),
    [Input('company-dropdown', 'value')])
def warning_flags(stock_ticker):
    warning_signs_list = asd.warning_signs(stock_ticker)

    return [html.Tr(html.Td(flag)) for flag in warning_signs_list]

@app.callback(
    Output('price-prediction', 'children'),
    [Input('company-dropdown', 'value')])
def price_prediction_table(stock_ticker):
    prediction_df = asd.present_value_calc(stock_ticker)

    return generate_table(prediction_df)


if __name__ == '__main__':
    app.run_server(debug=True)
