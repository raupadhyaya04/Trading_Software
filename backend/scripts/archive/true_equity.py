import pandas as pd
import yfinance as yf

profiles = pd.read_csv('profiles_rows.csv')
trades = pd.read_csv('trades_rows.csv')

symbols = trades['symbol'].unique().tolist()
print(f"Fetching data for {len(symbols)} symbols...")
data = yf.download(symbols, period='5d')

if isinstance(data.columns, pd.MultiIndex):
    prices = data['Close']
else:
    prices = pd.DataFrame({symbols[0]: data['Close']})

prices = prices.ffill().bfill()
latest_prices = prices.iloc[-1].to_dict()

results = []
for _, profile in profiles.iterrows():
    pid = profile['id']
    ptrades = trades[(trades['profile_id'] == pid) & (trades['status'] == 'filled')]
    
    cash = 100000.0
    holdings = {}
    
    for _, trade in ptrades.sort_values('filled_at').iterrows():
        sym = trade['symbol']
        qty = trade['quantity']
        price = trade['price']
        side = trade['side']
        if side == 'buy':
            cash -= qty * price
            holdings[sym] = holdings.get(sym, 0) + qty
        elif side == 'sell':
            cash += qty * price
            holdings[sym] = holdings.get(sym, 0) - qty
            
        if sym in holdings and abs(holdings[sym]) < 1e-6:
            del holdings[sym]
            
    portfolio_val = sum(qty * latest_prices.get(sym, 0) for sym, qty in holdings.items())
    true_equity = cash + portfolio_val
    record_equity = profile['total_equity']
    score = profile['competition_score']
    
    results.append({
        'society': profile['society_name'],
        'true_equity': round(true_equity, 2),
        'record_equity': round(record_equity, 2),
        'diff': round(true_equity - record_equity, 2),
        'score': score
    })

df = pd.DataFrame(results).sort_values('score', ascending=False)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 100)
print(df)
