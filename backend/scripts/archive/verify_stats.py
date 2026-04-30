import pandas as pd
import json

with open("data.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print("--- Descriptive Statistics ---")
print(df.describe().to_string())
print("\n--- Correlation Matrix ---")
print(df.corr(numeric_only=True).to_string())

# Specific check: Does Activity Score unfairly dominate Risk Score?
activity_risk_corr = df['activity_score'].corr(df['risk_score'])
print(f"\nCorrelation between Activity Score and Risk Score: {activity_risk_corr:.4f}")
