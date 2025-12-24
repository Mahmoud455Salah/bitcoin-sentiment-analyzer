import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style
plt.style.use('bmh')
print("Libraries imported successfully! 🚀")


# ==========================================
# PHASE 1: DATA INGESTION
# ==========================================
print("1. 📡 Connecting to CoinGecko API...")
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {'vs_currency': 'usd', 'days': '180', 'interval': 'daily'}

try:
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    print(f"✅ Data fetched successfully! ({len(prices)} days)")
except Exception as e:
    print(f"❌ Error Fetching Data: {e}")
    prices = []

# Create DataFrame
df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])


# ==========================================
# PHASE 2: CLEANING
# ==========================================
print("2. 🧹 Cleaning data...")

# Convert Unix timestamp to readable Date
df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Date', inplace=True)
df.drop('Timestamp', axis=1, inplace=True)

# Preview
print(df.tail(3))


# ==========================================
# PHASE 3: CALCULATING INDICATORS
# ==========================================
print("3. 🧠 Calculating Indicators (SMA & RSI)...")

# 1. 50-Day SMA (Trend)
df['SMA_50'] = df['Price'].rolling(window=50).mean()

# 2. RSI (Momentum)
delta = df['Price'].diff()

# Separate Gains and Losses
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
# Note: We put a negative sign here to make losses positive for the formula
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean() 

rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# Drop NaN values created by the window calculations
df.dropna(inplace=True)

print("✅ Indicators Calculated.")


# ==========================================
# PHASE 4: VISUALIZATION
# ==========================================
print('4. 📊 Generating Dashboard...')
plt.figure(figsize=(14, 10))

# Top Chart: Price vs Trend
plt.subplot(2, 1, 1)
plt.plot(df.index, df['Price'], label='Bitcoin Price', color='#333333', linewidth=1.5) 
plt.plot(df.index, df['SMA_50'], label='50-Day Trend (SMA)', color='#e67e22', linestyle='--', linewidth=2)
plt.title('Bitcoin Price vs Long-Term Trend', fontsize=16)
plt.ylabel('Price (USD)')
plt.legend()

# Bottom Chart: RSI
plt.subplot(2, 1, 2)
plt.plot(df.index, df['RSI'], label='RSI Momentum', color='#8e44ad', linewidth=1.5)

# Danger Zones
plt.axhline(70, color='red', linestyle='--', alpha=0.5, label='Overbought (>70)')
plt.axhline(30, color='green', linestyle='--', alpha=0.5, label='Oversold (<30)')
plt.fill_between(df.index, 70, 30, color='gray', alpha=0.1)

plt.title('Relative Strength Index (RSI)', fontsize=16)
plt.ylabel('RSI Score (0-100)')
plt.legend(loc='upper left')

plt.tight_layout()
plt.show()


# ==========================================
# PHASE 5: ANALYST DECISION ENGINE
# ==========================================

print('\n' + '='*40)
print("🤖 AUTOMATED ANALYST REPORT")
print('='*40)

# Get latest data
current_price = df['Price'].iloc[-1]
current_rsi = df['RSI'].iloc[-1]
current_sma = df['SMA_50'].iloc[-1]

print(f'Current Price:   ${current_price:,.2f}')
print(f'50-Day Average:  ${current_sma:,.2f}')
print(f'Current RSI:     {current_rsi:.2f}')
print("-" * 40)

# Logic Tree
decision = 'HOLD (Wait)'
reason = 'The market is neutral.'

if current_rsi > 70:
    decision = 'SELL / TAKE PROFIT'
    reason = 'RSI > 70. Asset is Overbought. Risk of correction is high.'
elif current_rsi < 30:
    decision = 'BUY THE DIP'
    reason = 'RSI < 30. Asset is Oversold. Good entry point.'
elif current_price > current_sma and current_rsi < 60:
    decision = 'BUY (Trend Following)'
    reason = 'Price is in an Uptrend (Above SMA) and RSI is healthy.'
elif current_price < current_sma:
    decision = 'CAUTION / SELL'
    reason = "Price is below 50-day average (Downtrend)."

print(f"📢 RECOMMENDATION: {decision}")
print(f"📝 REASON:         {reason}")
print('='*40)
