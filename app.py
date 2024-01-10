from flask import Flask, render_template, request
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

NEWS_API_KEY = 'c780d4770db448339a8e280a94ed0fc9'

@app.route('/')
def index():
    return render_template('index.html')

def get_stock_news(symbol):
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles[:5]  # Return top 5 articles
    return []

def get_stock_data(symbol):
    api_key = '549FPESRWIQIIDLN'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data['Time Series (Daily)']).T

def plot_stock_chart(df, symbol):
    if df.empty:
        return None  # No chart if DataFrame is empty

    plt.figure()
    df['4. close'].astype(float).plot(title=f'{symbol} Stock Price')
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()  # Close the plot to release memory
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/search', methods=['GET'])
def search():
    symbol = request.args.get('symbol')
    chart = None
    news_articles = []
    if symbol:
        df = get_stock_data(symbol)
        if not df.empty:
            chart = plot_stock_chart(df, symbol)
        news_articles = get_stock_news(symbol)  # Fetch news articles
    return render_template('search.html', symbol=symbol, chart=chart, news_articles=news_articles)


if __name__ == '__main__':
    app.run(debug=True)
