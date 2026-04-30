import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import math
import json
import os

# Get path relative to the script directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Read CSVS
profiles = pd.read_csv(os.path.join(DATA_DIR, 'profiles_rows.csv'))
trades = pd.read_csv(os.path.join(DATA_DIR, 'trades_rows.csv'))

# Filter out Test Account
profiles = profiles[~profiles['society_name'].str.contains('Test Account', case=False, na=False)]

# Fix missing timestamps
trades['filled_at'] = pd.to_datetime(trades['filled_at'], format='mixed', utc=True)
trades['placed_at'] = pd.to_datetime(trades['placed_at'], format='mixed', utc=True)
trades['filled_at'] = trades['filled_at'].fillna(trades['placed_at'])

# Filter out ADMN administrative trades
trades = trades[trades['symbol'] != 'ADMN']

symbols = trades['symbol'].dropna().unique().tolist()
symbols = [s for s in symbols if isinstance(s, str)]
data = yf.download(symbols, start="2026-02-01", end="2026-05-01", interval="1h", progress=False)

if isinstance(data.columns, pd.MultiIndex): prices = data['Close'].copy()
else: prices = pd.DataFrame({symbols[0]: data['Close'].copy()})

prices.index = prices.index.tz_convert('UTC')
prices = prices.ffill().bfill()
now = pd.Timestamp("2026-04-30 20:30:00", tz='UTC') 
comp_start = pd.Timestamp("2026-02-02", tz='UTC')

results = []
for _, profile in profiles.iterrows():
    pid = profile['id']
    prof_trades = trades[(trades['profile_id'] == pid) & (trades['status'] == 'filled')].copy()
    prof_trades['filled_at'] = prof_trades['filled_at'].fillna(comp_start)

    ptrades = prof_trades.copy()
    cash = 100000.0
    holdings = {}
    equity_curve = []
    daily_equity_map = {}
    snapshots = []
    
    for ts in prices.index:
        past_trades = ptrades[ptrades['filled_at'] <= ts]
        ptrades = ptrades[ptrades['filled_at'] > ts]
        for _, trade in past_trades.iterrows():
            sym = trade['symbol']; qty = float(trade['quantity']); price = float(trade['price'])
            if trade['side'] == 'buy':
                cash -= qty * price; holdings[sym] = holdings.get(sym, 0.0) + qty
            elif trade['side'] == 'sell':
                cash += qty * price; holdings[sym] = holdings.get(sym, 0.0) - qty
                
        port_val = 0.0
        for sym, qty in holdings.items():
            if abs(qty) > 1e-6:
                cur_price = prices.loc[ts, sym]
                if not pd.isna(cur_price): port_val += float(cur_price) * float(qty)
        
        eq = cash + port_val
        equity_curve.append(eq)
        snapshots.append({'timestamp': ts, 'totalEquity': eq})
        day_key = ts.strftime('%Y-%m-%d'); ts_time = ts.timestamp() * 1000
        
        if day_key not in daily_equity_map:
            daily_equity_map[day_key] = {'first': eq, 'last': eq, 'firstTime': ts_time, 'lastTime': ts_time}
        else:
            existing = daily_equity_map[day_key]
            if ts_time < existing['firstTime']: existing['first'] = eq; existing['firstTime'] = ts_time
            if ts_time > existing['lastTime']: existing['last'] = eq; existing['lastTime'] = ts_time
    
    equity_s = pd.Series(equity_curve, index=prices.index)
    returns = equity_s.pct_change().dropna()
    significant_returns = returns[abs(returns) > 1e-8]
    non_zero = len(significant_returns) / len(returns) if len(returns) > 0 else 0
    std_dev = returns.std() if len(returns) > 0 else 0
    mean_ret = returns.mean() if len(returns) > 0 else 0
    
    trading_hours = 252 * 6.5
    volatility = std_dev * np.sqrt(trading_hours) * 100
    hourly_rf = 0.04 / trading_hours
    sharpe = 0.0
    if std_dev > 1e-8 and non_zero >= 0.2: sharpe = ((mean_ret - hourly_rf) / std_dev) * np.sqrt(trading_hours)
    elif std_dev > 1e-8: sharpe = ((mean_ret - hourly_rf) / std_dev) * np.sqrt(trading_hours) * non_zero
    sharpe = max(-10, min(10, sharpe))
    peak = equity_s.cummax()
    drawdown = (peak - equity_s) / peak
    max_dd = drawdown.max() * 100 if len(drawdown) > 0 else 0
    true_equity = equity_curve[-1] if len(equity_curve) > 0 else 100000.0
    totalReturn = ((true_equity - 100000.0) / 100000.0) * 100
    
    returnScore = min(100.0, 50.0 + totalReturn * 3.0) if totalReturn >= 0 else max(0.0, 50.0 + totalReturn * 6.0)
    
    snapshotCount = len(snapshots)
    minSignificantSamples = 120; highConfidenceSamples = 504
    confidenceFactor = 0.0
    if snapshotCount < minSignificantSamples: confidenceFactor = min(snapshotCount / minSignificantSamples, 1.0) * 0.3
    elif snapshotCount < highConfidenceSamples: confidenceFactor = 0.3 + ((snapshotCount - minSignificantSamples) / (highConfidenceSamples - minSignificantSamples)) * 0.5
    else: confidenceFactor = 0.8 + min((snapshotCount - highConfidenceSamples) / highConfidenceSamples, 0.5) * 0.2
        
    rawSharpeScore = min((math.log(1 + max(sharpe, 0)) / math.log(1 + 3.0)) * 50, 50)
    sharpeScore = rawSharpeScore * (0.75 + 0.25 * confidenceFactor)
    rawDrawdownScore = max(0, 30 * math.exp(-max_dd / 15))
    drawdownScore = rawDrawdownScore
    if max_dd < 1.0 and confidenceFactor < 0.3: drawdownScore = rawDrawdownScore * 0.85
    rawVolatilityScore = max(0, 20 * math.exp(-volatility / 20))
    volatilityScore = rawVolatilityScore
    if volatility < 5 and confidenceFactor < 0.3: volatilityScore = rawVolatilityScore * 0.7
    riskScore = max(0, min(100, sharpeScore + drawdownScore + volatilityScore))
    
    sortedDays = sorted(list(daily_equity_map.keys()))
    dailyReturns, dailyEquities = [], []
    for i, day in enumerate(sortedDays):
        day_data = daily_equity_map[day]; dailyEquities.append(day_data['last'])
        if i == 0: ret = ((day_data['last'] - day_data['first']) / day_data['first']) * 100 if day_data['first'] > 0 else 0
        else:
            prevClose = daily_equity_map[sortedDays[i-1]]['last']
            ret = ((day_data['last'] - prevClose) / prevClose) * 100 if prevClose > 0 else 0
        dailyReturns.append(ret)
        
    greenDays = sum(1 for r in dailyReturns if r > 0)
    totalDays = len(dailyReturns)
    dailyWinRate = greenDays / totalDays if totalDays > 0 else 0
    winRateScore = max(0, min(40, ((dailyWinRate - 0.3) / 0.4) * 40))
    
    rSquared = 0.0
    if len(dailyEquities) >= 3:
        n_eq = len(dailyEquities); xMean = (n_eq - 1) / 2; yMean = sum(dailyEquities) / n_eq
        ssTotal = ssResidual = sxy = sxx = 0
        for i in range(n_eq):
            sxy += (i - xMean) * (dailyEquities[i] - yMean); sxx += (i - xMean) * (i - xMean); ssTotal += (dailyEquities[i] - yMean) ** 2
        slope = sxy / sxx if sxx > 0 else 0; intercept = yMean - slope * xMean
        for i in range(n_eq):
            predicted = intercept + slope * i; ssResidual += (dailyEquities[i] - predicted) ** 2
        rSquared = max(0, 1 - ssResidual / ssTotal) if ssTotal > 0 else 0
        if slope <= 0: rSquared *= 0.2
    smoothnessScore = rSquared * 15
    bigDropPenalty = sum((abs(r) - 3) ** 1.5 * 3 for r in dailyReturns if r < -3)
    noDropScore = max(0, 25 - bigDropPenalty)
    
    currentStreak, longestStreak = 0, 0
    for r in dailyReturns:
        if r > 0: currentStreak += 1; longestStreak = max(longestStreak, currentStreak)
        else: currentStreak = 0
    streakScore = min(20, (longestStreak / 4) * 20)
    consistencyScore = max(0, min(100, winRateScore + smoothnessScore + noDropScore + streakScore))
    
    tradeDays = set(); symbolsBought = set(); symbolsSold = set()
    for _, t in prof_trades.iterrows():
        t_time = t['placed_at'] if pd.notna(t['placed_at']) else (t['filled_at'] if pd.notna(t['filled_at']) else now)
        tradeDays.add(t_time.strftime('%Y-%m-%d'))
        sym = str(t['symbol']).upper().strip(); side = str(t['side']).lower()
        if side == 'buy': symbolsBought.add(sym)
        else: symbolsSold.add(sym)
            
    allTimeUniqueSymbols = len(symbolsBought.union(symbolsSold))
    breadthScore = min(35, (allTimeUniqueSymbols / 10.0) * 35)
    daysSinceStart = max(1, math.floor((now.timestamp() * 1000 - comp_start.timestamp() * 1000) / (24 * 60 * 60 * 1000)))
    approxTradingDays = max(1, math.floor(daysSinceStart * (5.0 / 7.0)))
    activeDayRatio = min(1, len(tradeDays) / approxTradingDays)
    engagementScore = max(0, min(35, ((activeDayRatio - 0.3) / 0.6) * 35))
    
    sellTrades = sum(1 for _, t in prof_trades.iterrows() if str(t['side']).lower() == 'sell')
    buySellScore = 0
    if len(prof_trades) > 0 and sellTrades > 0:
        sellRatio = sellTrades / len(prof_trades)
        if 0.15 <= sellRatio <= 0.7: buySellScore = 15
        elif sellRatio < 0.15: buySellScore = (sellRatio / 0.15) * 10
        else: buySellScore = max(0, 15 - ((sellRatio - 0.7) / 0.3) * 15)
    elif len(prof_trades) > 0 and sellTrades == 0: buySellScore = 3
    sellDiversityScore = min(15, (len(symbolsSold) / 3.0) * 15)
    rebalancingScore = buySellScore + sellDiversityScore
    activityScore = min(100, breadthScore + engagementScore + rebalancingScore)
    final_score = (returnScore * 0.5) + (riskScore * 0.25) + (consistencyScore * 0.15) + (activityScore * 0.1)
    
    results.append({
        'society_name': profile['society_name'],
        'competition_score': round(final_score),
        'return_score': round(returnScore),
        'risk_score': round(riskScore),
        'consistency_score': round(consistencyScore),
        'activity_score': round(activityScore),
        'realized_pnl': round(true_equity - 100000, 2),
        'total_pnl': round(true_equity - 100000, 2)
    })

df = pd.DataFrame(results)
df = df.sort_values('competition_score', ascending=False)
output_path = os.path.join(DATA_DIR, 'calculated_standings.json')
with open(output_path, 'w') as f:
    json.dump(df.to_dict(orient='records'), f, indent=2)
print(f"✅ Calculation complete. Updated standings saved to {output_path}")
