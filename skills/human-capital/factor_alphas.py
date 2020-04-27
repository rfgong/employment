# factor_alphas.py
# -------
# Writes a new CSV with Fama-French factor alphas
# 5 Factor: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html
# 3 Factor: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html
# Momentum Factor: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html
# SMB is defined differently for 5 Factor and 3 Factor data
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm

crsp = pd.read_csv("crsp_full_month.csv", dtype={'date': np.object})
crsp.dropna(inplace=True)
crsp = crsp.drop_duplicates(subset=['date', 'TICKER'], keep=False)
crsp = crsp[['date', 'TICKER', 'RET']]
crsp = crsp[(crsp['RET'] != 'R') & (crsp['RET'] != 'C')]
crsp["RET"] = crsp["RET"].apply(pd.to_numeric)
crsp['date'] = crsp['date'].str.slice(0, 6)

# Generate (CAPM) 1 factor alphas, 3 factor alphas, 4 factor alphas
factors = pd.read_csv("factors3.csv", dtype={'DATE': np.object})
mom = pd.read_csv("factors_mom.csv", dtype={'DATE': np.object})
factors = factors.merge(mom, on='DATE')
factors.rename(columns={'DATE': 'date'}, inplace=True)
factors["Mkt"] = factors["Mkt-RF"] + factors["RF"]
factors = factors[["date", "SMB", "HML", "Mkt", "Mom"]]

crsp3 = crsp.merge(factors, on='date')
tickers = crsp3['TICKER'].unique().tolist()
out_f3 = pd.DataFrame({"date": [], "TICKER": [], "ffalpha": []})
out_f1 = pd.DataFrame({"date": [], "TICKER": [], "ffalpha": []})
out_f4 = pd.DataFrame({"date": [], "TICKER": [], "ffalpha": []})

for tic in tickers:
    tic_df = crsp3[crsp3["TICKER"] == tic]
    # Skip under-defined regressions where there are fewer observations than variables used
    if len(tic_df.index) < 2:
        continue
    reg = sm.ols(formula="RET ~ Mkt", data=tic_df).fit()
    tic_df["ffalpha"] = tic_df["RET"] - reg.params.Mkt * tic_df["Mkt"]
    tic_df_f1 = tic_df[["date", "TICKER", "ffalpha"]]
    out_f1 = out_f1.append(tic_df_f1, ignore_index=True)
    if len(tic_df.index) < 4:
        continue
    reg = sm.ols(formula="RET ~ SMB + HML + Mkt", data=tic_df).fit()
    tic_df["ffalpha"] = tic_df["RET"] - reg.params.SMB * tic_df["SMB"] - reg.params.HML * tic_df[
        "HML"] - reg.params.Mkt * tic_df["Mkt"]
    tic_df_f3 = tic_df[["date", "TICKER", "ffalpha"]]
    out_f3 = out_f3.append(tic_df_f3, ignore_index=True)
    if len(tic_df.index) < 5:
        continue
    reg = sm.ols(formula="RET ~ SMB + HML + Mkt + Mom", data=tic_df).fit()
    tic_df["ffalpha"] = tic_df["RET"] - reg.params.SMB * tic_df["SMB"] - reg.params.HML * tic_df[
        "HML"] - reg.params.Mkt * tic_df["Mkt"] - reg.params.Mom * tic_df["Mom"]
    tic_df_f4 = tic_df[["date", "TICKER", "ffalpha"]]
    out_f4 = out_f4.append(tic_df_f4, ignore_index=True)

out_f3.rename(columns={'date': 'DATE'}, inplace=True)
out_f3.to_csv("ff3alphas.csv", index=False)
out_f1.rename(columns={'date': 'DATE'}, inplace=True)
out_f1.to_csv("ff1alphas.csv", index=False)
out_f4.rename(columns={'date': 'DATE'}, inplace=True)
out_f4.to_csv("ff4alphas.csv", index=False)

# Generate 5 factor alphas
factors = pd.read_csv("factors5.csv", dtype={'DATE': np.object})
factors.rename(columns={'DATE': 'date'}, inplace=True)
factors["Mkt"] = factors["Mkt-RF"] + factors["RF"]
factors = factors[["date", "SMB", "HML", "Mkt", "RMW", "CMA"]]

crsp5 = crsp.merge(factors, on='date')
tickers = crsp5['TICKER'].unique().tolist()
out_f5 = pd.DataFrame({"date": [], "TICKER": [], "ffalpha": []})

# SMB_T = []
# HML_T = []
# Mkt_T = []
# RMW_T = []
# CMA_T = []
# valid_tickers = []
for tic in tickers:
    tic_df = crsp5[crsp5["TICKER"] == tic]
    # Skip under-defined regressions where there are fewer observations than variables used
    if len(tic_df.index) < 6:
        continue
    reg = sm.ols(formula="RET ~ SMB + HML + Mkt + RMW + CMA", data=tic_df).fit()
    # valid_tickers.append(tic)
    # SMB_T.append(reg.tvalues.SMB)
    # HML_T.append(reg.tvalues.HML)
    # Mkt_T.append(reg.tvalues.Mkt)
    # RMW_T.append(reg.tvalues.RMW)
    # CMA_T.append(reg.tvalues.CMA)
    tic_df["ffalpha"] = tic_df["RET"] - reg.params.SMB * tic_df["SMB"] - reg.params.HML * tic_df[
        "HML"] - reg.params.Mkt * tic_df["Mkt"] - reg.params.RMW * tic_df["RMW"] - reg.params.CMA * tic_df["CMA"]
    tic_df_f5 = tic_df[["date", "TICKER", "ffalpha"]]
    out_f5 = out_f5.append(tic_df_f5, ignore_index=True)

out_f5.rename(columns={'date': 'DATE'}, inplace=True)
out_f5.to_csv("ff5alphas.csv", index=False)
# out = pd.DataFrame({'TICKERS': valid_tickers, 'SMB_T': SMB_T, 'HML_T': HML_T, 'Mkt_T': Mkt_T, 'RMW_T': RMW_T, 'CMA_T': CMA_T})
# out.to_csv('factors_fit.csv', index=False)
# print(np.mean(map(abs, SMB_T)))
# print(np.mean(map(abs, HML_T)))
# print(np.mean(map(abs, Mkt_T)))
# print(np.mean(map(abs, RMW_T)))
# print(np.mean(map(abs, CMA_T)))
# print(np.std(map(abs, SMB_T)))
# print(np.std(map(abs, HML_T)))
# print(np.std(map(abs, Mkt_T)))
# print(np.std(map(abs, RMW_T)))
# print(np.std(map(abs, CMA_T)))
