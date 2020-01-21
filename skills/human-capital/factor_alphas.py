# factor_alphas.py
# -------
# Writes a new CSV with Fama-French 3 factor alphas
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm

crsp = pd.read_csv("crsp_full_month.csv", dtype={'date': np.object})
crsp = crsp[['date', 'TICKER', 'RETX']]
crsp = crsp[(crsp['RETX'] != 'R') & (crsp['RETX'] != 'C')]
crsp["RETX"] = crsp["RETX"].apply(pd.to_numeric)
crsp['date'] = crsp['date'].str.slice(0, 6)
factors = pd.read_csv("factors.csv", dtype={'DATE': np.object})
factors.rename(columns={'DATE': 'date'}, inplace=True)
factors["Mkt"] = factors["Mkt-RF"] + factors["RF"]
factors = factors[["date", "SMB", "HML", "Mkt"]]

crsp = crsp.merge(factors, on='date')
tickers = crsp['TICKER'].unique().tolist()
out = pd.DataFrame({"date": [], "TICKER": [], "ff3alpha": []})

for tic in tickers:
    tic_df = crsp[crsp["TICKER"] == tic]
    # Skip under-defined regressions where there are fewer observations than variables used
    if len(tic_df.index) < 4:
        continue
    reg = sm.ols(formula="RETX ~ SMB + HML + Mkt", data=tic_df).fit()
    tic_df["ff3alpha"] = tic_df["RETX"] - reg.params.SMB * tic_df["SMB"] - reg.params.HML * tic_df["HML"] - reg.params.Mkt * tic_df["Mkt"]
    tic_df = tic_df[["date", "TICKER", "ff3alpha"]]
    out = out.append(tic_df, ignore_index=True)

out.rename(columns={'date': 'DATE'}, inplace=True)
out.to_csv("ff3alphas.csv", index=False)
