# Competition Data Analysis

I've analyzed the CSV exports and the competition scoring logic in the codebase. You are completely correct that some users benefited unfairly from not logging in. Here is the exact breakdown of the exploit and how it inflated scores.

## The Flaw: Client-Side "Lazy" Snapshots
In `frontend/src/pages/Dashboard/Dashboard.tsx`, the application only creates a new `portfolio_snapshot` if it has been >1 hour since the last one... **but only while the user has the dashboard open**. 

If a user buys stocks and then doesn't log in for 3 weeks:
1. **No snapshots are recorded** during those 3 weeks.
2. When calculating risk metrics (`calculateRiskMetrics`), the code blindly iterates over the `snapshots` array: `returns.push((currEquity - prevEquity) / prevEquity);`. It treats each snapshot as 1 hour of time, completely ignoring the timestamps.
3. A 3-week gap between two snapshots is incorrectly processed as just a "single hour" return.

## How it Inflated Scores Unfairly
Because inactive users skipped the hourly snapshots, they inadvertently bypassed the market's day-to-day chop:

1. **Immunity to Intra-Period Drawdowns:** The script calculates `Max Drawdown` by looking at peak-to-trough in the *snapshots*. If a user's stock crashed 40% mid-month but recovered by the time they logged in again, their recorded `Max Drawdown` is 0%.
2. **Artificially Low Volatility:** Because they skipped hundreds of volatile hours, their `stdDev` is incredibly small. 
3. **Exploited Sharpe Ratio:** The Sharpe score calculation (`(meanReturn - hourlyRiskFreeRate) / stdDev`) uses the depressed volatility. With lower volatility and no recorded drawdowns, their Risk Score is drastically inflated.

## Evidence from the CSV Data
When looking at the exact database states:
* Active teams (e.g., *Irish Student Managed Fund*, *Marshall Finance Group*) have **130-180+ snapshots**. Their portfolios correctly faced the "volatility penalties".
* Inactive teams (e.g., *Birmingham Investment & Finance Society*) have huge gaps—some as few as **12 snapshots total** across months! 
* Because Birmingham only had 12 snapshots, their portfolio appeared almost entirely flat/stable to the algorithm, rewarding them a much higher `risk_score` than realistic.

## How to Fix It
To run a fair competition, the portfolio snapshot process cannot rely on users opening their dashboard:
1. **Server-Side Cron Job:** You must move the `portfolio_snapshots` insertion to a scheduled backend task (e.g., using GitHub Actions, Vercel Cron, or a Supabase pg_cron rule) that pulls live prices for all users' portfolios every hour.
2. **Rescore Algorithm:** For the current competition, the only way to get a "Fair" score is to reconstruct their hour-by-hour equity curve using `yfinance` historical hourly data and their `trades_rows.csv` log, manually calculating the Sharpe/Volatility based on the reconstructed true curve rather than the faulty snapshots.
