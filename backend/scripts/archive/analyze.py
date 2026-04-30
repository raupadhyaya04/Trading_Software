import pandas as pd

profiles = pd.read_csv('profiles_rows.csv')
snapshots = pd.read_csv('portfolio_snapshots_rows.csv')

snapshots['timestamp'] = pd.to_datetime(snapshots['timestamp'])

for pid, group in snapshots.groupby('profile_id'):
    group = group.sort_values('timestamp')
    name = profiles[profiles['id'] == pid]['society_name'].iloc[0]
    print(f"\n--- {name} ---")
    
    # print max daily jump in equity
    group['equity_diff'] = group['total_equity'].diff()
    max_jump = group['equity_diff'].max()
    max_drop = group['equity_diff'].min()
    
    # Look for missing days or huge jumps
    print(f"Num Snapshots: {len(group)}, Max Jump: {max_jump}, Max Drop: {max_drop}")
    print(f"Start: {group['timestamp'].min().date()} to End: {group['timestamp'].max().date()}")

