import pandas as pd
import yfinance as yf
import numpy as np

profiles = pd.read_csv('profiles_rows.csv')
trades = pd.read_csv('trades_rows.csv')
trades['filled_at'] = pd.to_datetime(trades['filled_at'], format='mixed', utc=True)

symbols = trades['symbol'].unique().tolist()
print(f"Fetching 1h data for {len(symbols)} symbols...")
data = yf.download(symbols, start="2026-02-01", end="2026-05-01", interval="1h", progress=False)

if isinstance(data.columns, pd.MultiIndex):
    prices = data['Close'].copy()
else:
    prices = pd.DataFrame({symbols[0]: data['Close'].copy()})

prices.index = prices.index.tz_convert('UTC')
prices = prices.ffill().bfill()

results = []
for _, profile in profiles.iterrows():
    pid = profile['id']
    ptrades = trades[(trades['profile_id'] == pid) & (trades['status'] == 'filled')].copy()
    
    cash = 100000.0
    holdings = {}
    
    equity_curve = []
    
    for ts in prices.index:
        past_trades = ptrades[ptrades['filled_at'] <= ts]
        ptrades = ptrades[ptrades['filled_at'] > ts]
        
        for _, trade in past_trades.iterrows():
            sym = trade['symbol']
            qty = trade['quantity']
            price = trade['price']
            if trade['side'] == 'buy':
                cash -= qty * price
                holdings[sym] = holdings.get(sym, 0) + qty
            elif trade['side'] == 'sell':
                cash += qty * price
                holdings[sym] = holdings.get(sym, 0) - qty
                
        port_val = 0
        for sym, qty in holdings.items():
            if abs(qty) > 1e-6:
                cur_price = prices.loc[ts, sym]
                if not pd.isna(cur_price):
                    port_val += float(cur_price) * float(qty)
        
        equity_curve.append(cash + port_val)
    
    equity_s = pd.Series(equity_curve, index=prices.index)
    returns = equity_s.pct_change().dropna()
    returns = returns[abs(returns) > 1e-8]
    
    non_zero = len(returns) / len(equity_s) if len(equity_s) > 0 else 0
    std_dev = returns.std() if len(returns) > 0 else 0
    mean_ret = returns.mean() if len(returns) > 0 else 0
    
    trading_hours = 252 * 6.5
    vol = std_dev * np.sqrt(trading_hours) * 100
    
    hourly_rf = 0.04 / trading_hours
    sharpe = 0
    if std_dev > 1e-8 and non_zero >= 0.2:
        sharpe = ((mean_ret - hourly_rf) / std_dev) * np.sqrt(trading_hours)
    elif std_dev > 1e-8:
        sharpe = ((mean_ret - hourly_rf) / std_dev) * np.sqrt(trading_hours) * non_zero
        
    peak = equity_s.cummax()
    drawdown = (peak - equity_s) / peak
    max_dd = drawdown.max() * 100 if len(drawdown) > 0 else 0
    
    true_equity = cash + port_val
    record_equity = profile['total_equity']
    score = profile['competition_score']
    diff = true_equity - record_equity

    results.append({
        'Society': profile['society_name'],
        'Real_Score': score,
        'Recorded_Eq': round(record_equity, 2),
        'True_Eq': round(true_equity, 2),
        'Sim_Sharpe': round(sharpe, 2),
        'Sim_Vol': round(vol, 2),
        'Sim_MaxDD': round(max_dd, 2)
    })

df = pd.DataFrame(results)
print(df.sort_values('Real_Score', ascending=False).to_string(index=False))
