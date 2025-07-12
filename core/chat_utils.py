import matplotlib
matplotlib.use('Agg')
import io
import base64
import yfinance as yf
import matplotlib.pyplot as plt
from transformers import pipeline

# Helper to fetch stock data and plot technical curve

def fetch_and_plot_stock(ticker):
    data = yf.download(ticker, period='6mo', interval='1d')
    if data.empty:
        return None, None
    # Simple technical: 20-day moving average
    data['MA20'] = data['Close'].rolling(window=20).mean()
    plt.figure(figsize=(10,4))
    plt.plot(data['Close'], label='Close Price')
    plt.plot(data['MA20'], label='MA20')
    plt.title(f'{ticker} Price & MA20')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plot_url = f"data:image/png;base64,{image_base64}"
    return data, plot_url

# Helper to get chat response from Hugging Face

_hf_pipe = None

def get_chat_advice(message, stock_data, ticker, role='analyst'):
    global _hf_pipe
    if _hf_pipe is None:
        _hf_pipe = pipeline('text2text-generation', model='google/flan-t5-base')
    prompt = f"You are a financial assistant for {role}s. A user asked: {message}\nHere is the recent price data for {ticker} (last 5 days):\n{stock_data.tail(5).to_string()}\nBased on technicals, should the user sell, hold, or buy? If selling, what % of their portfolio should be sold to maximize profit? Give a brief explanation."
    result = _hf_pipe(prompt, max_new_tokens=120)[0]['generated_text']
    return result.strip()
