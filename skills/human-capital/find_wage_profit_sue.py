# find_premia.py
# -------
# Runs regression and generates output CSVs
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
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
cog = pd.read_csv("skills_current.csv")
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
print("Duplicate Data Removed: " + str(100 * len(wb['xlr'])/pre_len) + "%")
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

