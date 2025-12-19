import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# PHASE 1: DATA INGESTION (Getting the raw data)
# ==========================================
print("1. 📡 Connecting to CoinGecko API...")
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
# We grab 180 days (6 months) to get a solid trend
params = {'vs_currency': 'usd', 'days': '180', 'interval': 'daily'}

try:
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
except Exception as e:
    print(f'Error Fetching Data: {e}')
    prices = []

# Create the DataFrame
df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])

# ==========================================
# PHASE 2: CLEANING & TRANSFORMATION
# ==========================================

print("2. 🧹 Cleaning and preparing data...")

# Convert Unix timestamp to readable Date
df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Date', inplace=True)
df.drop('Timestamp',axis=1, inplace=True)
# print(df.head())


# ==========================================
# PHASE 3: FEATURE ENGINEERING (The Analyst Work)
# ==========================================
print("3. 🧠 Calculating Indicators (SMA & RSI)...")

# Indicator 1: 50-Day Simple Moving Average (SMA)
# If Price is ABOVE this line, the long-term trend is UP.
df['SMA_50'] = df['Price'].rolling(window=50).mean()

# Indicator 2: Relative Strength Index (RSI) - The "Overbought/Oversold" meter
# (A).Calculate the daily change
delta = df['Price'].diff()
# (B).Separate Gains and Losses
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (delta.where(delta < 0, 0)).rolling(window=14).mean()

# (C).The RSI Formula
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))
# "RSI" > 70 : Usually means 'Overbought'(Selling Opportunity)
# "RSI" < 30 : Usually means 'Oversold'(Buying Opportunity)

# Remove the first 50 rows because they will have NaN (null) values due to the calculation
df.dropna(inplace=True)
print(df['RSI'])

# ==========================================
# PHASE 4: VISUALIZATION (The Evidence)
# ==========================================
print('4. 📊 Generating the Dashbord...')
plt.figure(figsize=(14, 10))
plt.style.use('bmh') # Use a professional style

# Top Chart: Price vs Trend
plt.subplot(2, 1, 1)
plt.plot(df.index, df['Price'], label='Bitcoin Price', color='#333333', linewidth=1.5 ) 
plt.plot(df.index, df['SMA_50'], label='50-Day Trend (SMA)', color='#e67e22', linestyle='--', linewidth=2)
plt.title('Bitcoin Price vs Long-Term Trend', fontsize=16)
plt.ylabel('Price (USD)')
plt.legend()

# Bottom Chart: RSI (The Decision Maker)
plt.subplot(2, 1, 2)
plt.plot(df.index, df['RSI'], label= 'RSI Momentum', color= '#8e44ad', linewidth=1.5)

# Add "Danger Zones"
plt.axhline(70, color='red', linestyle='--', alpha=0.5, label='Overbought (>70)')
plt.axhline(30, color='green', linestyle='--', alpha=0.5, label='Oversold (<30)')
plt.fill_between(df.index, 70, 30, color='gray', alpha=0.1) # The "Safe Zone"

plt.title('Relative Strength Index (RSI)', fontsize=16)
plt.ylabel('RSI Score (0-100)')
plt.legend(loc='upper left')

plt.tight_layout()
plt.show()


# ==========================================
# PHASE 5: AUTOMATED INSIGHTS & DECISION
# ==========================================

print('\n' + '='*40)
print("🤖 ANALYST DECISION ENGINE")
print('='*40)

# Get the latest data point (Today)
current_price = df['Price'].iloc[-1]
current_rsi = df['RSI'].iloc[-1]
current_sma = df['SMA_50'].iloc[-1]

print(f'Current Price: ${current_price:,.2f}')
print(f'50-Day Average: ${current_sma:,.2f}')
print(f'Current RSI: ${current_rsi:,.2f}')
print("-"*40)

# THE LOGIC TREE (How we make the decision)
decision = 'HOLD (Wait)'
reason = 'The market is neytral.'

if current_rsi > 70:
    decision = 'SELL / TAKE PROFIT '
    reason = 'RSI is above 70. Bitcoin is expensive (OverBought). Risk of crash is high.'
elif current_rsi < 30:
    decision = 'BUY THE DIP'
    reason = 'RSI is below 30. Bitcoin is cheap (Oversold). Good entry point.'
elif current_price > current_sma and current_rsi < 60:
    decision = 'BUY (Trend Following)'
    reason = 'Price is above the 50-day average (Uptrend) and RSI is not too high yet.'
elif current_price < current_sma:
    decision = 'CAUTION / SELL'
    reason = "Price is below the 50-day average. We are in a downtrend."

print(f"📢 RECOMMENDATION: {decision}")
print(f"📝 REASON:         {reason}")
print('='*40)