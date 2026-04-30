import pandas as pd
import yfinance as yf

profiles = pd.read_csv('profiles_rows.csv')
trades = pd.read_csv('trades_rows.csv')

soton_id = profiles[profiles['society_name'].str.contains('Southampton')]['id'].values[0]
soton_trades = trades[trades['profile_id'] == soton_id].sort_values('filled_at')

print("Southampton Trades:")
print(soton_trades[['filled_at', 'symbol', 'side', 'quantity', 'price']].to_string())

# Check ADMN trades specifically across everyone
admn_trades = trades[trades['symbol'] == 'ADMN']
print("\nADMN Trades:")
print(admn_trades[['profile_id', 'symbol', 'side', 'quantity', 'price']].to_string())
