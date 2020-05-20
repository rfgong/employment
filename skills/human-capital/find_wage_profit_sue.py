# find_premia.py
# -------
# Runs regression and generates output CSVs
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
import os
from collections import OrderedDict

# Toggle code functionality
lags_list = [1, 2, 3, 6]
offsets = [lags_list[0]] + [lags_list[i] - lags_list[i-1] for i in range(1, len(lags_list))]

convert_skill_zscore = False
output_fm_wage = False  # Need folder named "fama_macbeth_wage_csv" for output, then run output in MATLAB
output_fm_prof = False  # Need folder named "fama_macbeth_prof_csv" for output, then run output in MATLAB
output_fm_sue = False  # Need folder named "fama_macbeth_sue_csv" for output, then run output in MATLAB
use_YYYYMM_range = False  # False to use full date range
range_start = 200001
range_end = 200512

# Setup databases to read in from
market = pd.read_csv("market_measures.csv")
cog = pd.read_csv("skills_change_current.csv")
if use_YYYYMM_range:
    cog = cog[(cog['DATE'] >= range_start) & (cog['DATE'] <= range_end)]
# Merge cognism with market
cog = cog.merge(market, on=["DATE", "TICKER"])
# Add industry and monthly controls
dummy_ind = pd.get_dummies(cog['INDUSTRY'], prefix='ind')
ind_col = list(dummy_ind.columns.values)
cog = cog.join(dummy_ind.loc[:, ind_col[1]:])
dummy_month = pd.get_dummies(cog['DATE'], prefix='month')
month_col = list(dummy_month.columns.values)
cog = cog.join(dummy_month.loc[:, month_col[1]:])
# Covariates list
cov_list = list(cog.columns[54:])
skill_col = ["[0] Personal Coaching", "[1] Business Development", "[2] Logistics", "[3] Business Development", "[4] Digital Marketing", "[5] Administration", "[6] Hospitality", "[7] Business Development", "[8] Musical Production", "[9] Industrial Management", "[10] Human Resources (Junior)", "[11] Human Resources (Senior)", "[12] Visual Design", "[13] Data Analysis", "[14] Business Development", "[15] Recruiting", "[16] Education", "[17] Business Development", "[18] Operations Management", "[19] Middle Management", "[20] Pharmaceutical", "[21] Product Management", "[22] Healthcare", "[23] Sales", "[24] Insurance", "[25] Social Media and Communications", "[26] Web Development", "[27] Manufacturing and Process Management", "[28] Electrical Engineering", "[29] Legal", "[30] Graphic Design", "[31] Non-Profit and Community", "[32] Retail and Fashion", "[33] Real Estate", "[34] Military", "[35] Accounting and Auditing", "[36] Administration", "[37] IT Management and Support", "[38] Construction Management", "[39] Video and Film Production", "[40] CRM and Sales Management", "[41] Energy, Oil, and Gas", "[42] Mobile Telecommunications", "[43] Software Engineering", "[44] Banking and Finance", "[45] Web Design", "[46] Public Policy", "[47] Business Development", "[48] Technical Product Management", "[49] Sales Management"]
# Convert date to months
cog["DATE"] = (cog["DATE"] // 100) * 12 + (cog["DATE"] % 100)

if convert_skill_zscore:
    for i in range(50):
        mean = np.mean(cog["S"+str(i)])
        std = np.std(cog["S"+str(i)])
        if std == 0:  # These skills result are not interpretable (Coefficients are always 0 anyways)
            continue
        cog["S"+str(i)] = (cog["S"+str(i)] - mean) / std

# Extension simultaneous WageBill
wb = pd.read_csv("compustat_year.csv")
wb.dropna(inplace=True)
pre_len = len(wb['xlr'])
wb = wb.drop_duplicates(subset=['tic', 'datadate'], keep=False)
print("Duplicate Data Removed: " + str(100 * (1 - len(wb['xlr'])/pre_len)) + "%")
wb.rename(columns={'datadate': 'DATE', 'tic': 'TICKER'}, inplace=True)
# Convert date to months
wb["DATE"] = (wb["DATE"] // 100)
wb["DATE"] = (wb["DATE"] // 100) * 12 + (wb["DATE"] % 100)
out_cols = OrderedDict({"SKILLS": skill_col, "COEFFICIENT": [], "SE": [], "TSTAT": []})
wb = cog.merge(wb, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="xlr ~ "+"S"+str(i)+"+"+' + '.join(cov_list), data=wb).fit()
    out_cols["COEFFICIENT"].append(reg.params["S"+str(i)])
    out_cols["SE"].append(reg.bse["S"+str(i)])
    out_cols["TSTAT"].append(reg.tvalues["S"+str(i)])
    if output_fm_wage:
        # Write data out for Fama-Macbeth in MATLAB
        fm_out = wb[['DATE', 'xlr', "S"+str(i)] + cov_list]
        fm_out.to_csv("./fama_macbeth_wage_csv/reg_" + "s"+str(i) + ".csv", index=False)
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("wage_ols.csv", index=False)

# Extension Profitability (Be sure to load in cog as "skills_change_current.csv")
p = pd.read_csv("compustat_month_extensions.csv")
pre_len = len(p['datadate'])
p = p.drop_duplicates(subset=['tic', 'datadate'], keep=False)
print("Duplicate Data Removed: " + str(100 * (1 - len(p['datadate'])/pre_len)) + "%")
p.rename(columns={'datadate': 'DATE', 'tic': 'TICKER'}, inplace=True)
# Profitability
p["PROFIT"] = (p["revtq"] - p["cogsq"]) / p["atq"]
p = p[p['PROFIT'].notna()]
# Convert date to months
p["DATE"] = (p["DATE"] // 100)
p["DATE"] = (p["DATE"] // 100) * 12 + (p["DATE"] % 100)
out_cols = OrderedDict({"SKILLS": skill_col})
reported = ['SKILL', 'LN_MCAP', 'BM', 'MOM']
for r in reported:
    for l in lags_list:
        out_cols["LAG" + str(l) + "_" + r + "_COEFFICIENT"] = []
        out_cols["LAG" + str(l) + "_" + r + "_SE"] = []
        out_cols["LAG" + str(l) + "_" + r + "_TSTAT"] = []
for i in range(len(lags_list)):
    # cog["DATE"] += offsets[i]  # "pushed ahead" lag
    p["DATE"] -= offsets[i]  # "pulled behind" lag
    m_c = cog.merge(p, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="PROFIT ~ "+"S"+str(j)+"+"+' + '.join(cov_list), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_COEFFICIENT"].append(reg.params["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_SE"].append(reg.bse["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_TSTAT"].append(reg.tvalues["S"+str(j)])
        for r in reported[1:]:
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_COEFFICIENT"].append(reg.params[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_SE"].append(reg.bse[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_TSTAT"].append(reg.tvalues[r])
        if output_fm_prof:
            # Write data out for Fama-Macbeth in MATLAB
            fm_out = m_c[['DATE', 'PROFIT', "S"+str(j)] + cov_list]
            fm_out.to_csv("./fama_macbeth_prof_csv/reg_" + "s"+str(j) + "_lag" + str(lags_list[i]) + ".csv", index=False)
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("profit_ols.csv", index=False)

# Extension SUE (Be sure to load in cog as "skills_change_current.csv")
p = pd.read_csv("compustat_month_extensions.csv")
pre_len = len(p['datadate'])
p = p.drop_duplicates(subset=['tic', 'datadate'], keep=False)
print("Duplicate Data Removed: " + str(100 * (1 - len(p['datadate'])/pre_len)) + "%")
p.rename(columns={'datadate': 'DATE', 'tic': 'TICKER'}, inplace=True)
# Convert date to months
p["DATE"] = (p["DATE"] // 100)
p["DATE"] = (p["DATE"] // 100) * 12 + (p["DATE"] % 100)
p.to_csv("intermed.csv", index=False)
# SUE
g = open("intermed2.csv", "w+")
g.write("DATE,TICKER,SUE\n")
lagged_eps = {}
lagged_difference = {}
with open("intermed.csv") as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # split line: 0:gvkey,1:DATE,2:fyearq,3:fqtr,4:TICKER,5:atq,6:cogsq,7:epspxq,8:revtq
        current = line.rstrip('\n').split(',')
        if not current[7]:
            continue
        # insert DATE, TICKER
        new_line = current[1] + "," + current[4]
        # cache EPS
        date = int(current[1])
        lagged_eps[(current[4], date)] = float(current[7])
        # cache EPS difference
        if (current[4], date - 3 * 4) in lagged_eps:
            lagged_difference[(current[4], date)] = float(current[7]) - lagged_eps[(current[4], date - 3 * 4)]
        else:
            continue
        # insert SUE if found
        eight_to_one = []
        missing = False
        for i in range(8):
            if (current[4], date - 3 * (8 - i)) in lagged_difference:
                eight_to_one.append(lagged_difference[(current[4], date - 3 * (8 - i))])
            else:
                missing = True
                break
        if missing or np.std(eight_to_one) == 0:
            continue
        new_line += "," + str((float(current[7]) - lagged_eps[(current[4], date - 3 * 4)]) / np.std(eight_to_one))
        g.write(new_line + "\n")
g.close()
s = pd.read_csv("intermed2.csv")
out_cols = OrderedDict({"SKILLS": skill_col})
reported = ['SKILL', 'LN_MCAP', 'BM', 'MOM']
for r in reported:
    for l in lags_list:
        out_cols["LAG" + str(l) + "_" + r + "_COEFFICIENT"] = []
        out_cols["LAG" + str(l) + "_" + r + "_SE"] = []
        out_cols["LAG" + str(l) + "_" + r + "_TSTAT"] = []
for i in range(len(lags_list)):
    # cog["DATE"] += offsets[i]  # "pushed ahead" lag
    s["DATE"] -= offsets[i]  # "pulled behind" lag
    m_c = cog.merge(s, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="SUE ~ "+"S"+str(j)+"+"+' + '.join(cov_list), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_COEFFICIENT"].append(reg.params["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_SE"].append(reg.bse["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_TSTAT"].append(reg.tvalues["S"+str(j)])
        for r in reported[1:]:
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_COEFFICIENT"].append(reg.params[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_SE"].append(reg.bse[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_TSTAT"].append(reg.tvalues[r])
        if output_fm_sue:
            # Write data out for Fama-Macbeth in MATLAB
            fm_out = m_c[['DATE', 'SUE', "S"+str(j)] + cov_list]
            fm_out.to_csv("./fama_macbeth_sue_csv/reg_" + "s"+str(j) + "_lag" + str(lags_list[i]) + ".csv", index=False)
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("sue_ols.csv", index=False)
# Delete intermediate files
# os.remove("intermed.csv")
# os.remove("intermed2.csv")

