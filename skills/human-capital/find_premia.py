# find_premia.py
# -------
# Runs regression and generates output CSVs
import pandas as pd
import statsmodels.formula.api as sm
from collections import OrderedDict

# Toggle code path
use_abn_skills = True
output_fm_tobit = False  # User should create folder named "fama_macbeth_tob_csv" for output
output_fm_skill = False  # User should create folder named "fama_macbeth_skill_csv" for output

# Setup databases to read in from
market = pd.read_csv("market_measures.csv")
cog = pd.read_csv("skills_current.csv")
ff = pd.read_csv("ff5alphas.csv")
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

if use_abn_skills:
    # Find AbnSkills
    cols = {"DATE": [], "TICKER": []}
    for i in range(50):
        cols["AS" + str(i)] = []
    abn = pd.DataFrame(cols)
    abn["DATE"] = cog["DATE"]
    abn["TICKER"] = cog["TICKER"]
    dependent_vars = ' + '.join(cov_list)
    for i in range(50):
        reg = sm.ols(formula="S"+str(i)+" ~ "+dependent_vars, data=cog).fit()
        abn["AS" + str(i)] = reg.resid
else:
    # Use Skills instead of AbnSkills
    cols = {"DATE": [], "TICKER": []}
    for i in range(50):
        cols["AS" + str(i)] = []
    abn = pd.DataFrame(cols)
    abn["DATE"] = cog["DATE"]
    abn["TICKER"] = cog["TICKER"]
    for i in range(50):
        abn["AS" + str(i)] = cog["S"+str(i)]

# Extension Tobit for equal market and book liabilities
q_db = cog[['DATE', 'TICKER', 'TOB']]
out_cols = OrderedDict({"SKILLS": skill_col, "COEFFICIENT": [], "SE": [], "TSTAT": []})
m_q = abn.merge(q_db, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="TOB ~ "+"AS"+str(i), data=m_q).fit()
    out_cols["COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols["SE"].append(reg.bse["AS"+str(i)])
    out_cols["TSTAT"].append(reg.tvalues["AS"+str(i)])
    if output_fm_tobit:
        # Write data out for Fama-Macbeth in MATLAB
        fm_out = m_q[['DATE', 'TOB', "AS"+str(i)]]
        fm_out.to_csv("./fama_macbeth_tob_csv/reg_" + "s"+str(i) + ".csv", index=False)
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("tobit_ols.csv", index=False)

# Convert date to months
abn["DATE"] = (abn["DATE"] // 100) * 12 + (abn["DATE"] % 100)
ff["DATE"] = (ff["DATE"] // 100) * 12 + (ff["DATE"] % 100)
# Regression with Lags
lags_list = [1, 2, 3, 6]
offsets = [lags_list[0]] + [lags_list[i] - lags_list[i-1] for i in range(1, len(lags_list))]
out_cols = OrderedDict({"SKILLS": skill_col})
for l in lags_list:
    out_cols["LAG" + str(l) + "_COEFFICIENT"] = []
    out_cols["LAG" + str(l) + "_SE"] = []
    out_cols["LAG" + str(l) + "_TSTAT"] = []
for i in range(len(lags_list)):
    abn["DATE"] += offsets[i]
    m_c = abn.merge(ff, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="ffalpha ~ "+"AS"+str(j), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_COEFFICIENT"].append(reg.params["AS"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SE"].append(reg.bse["AS"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_TSTAT"].append(reg.tvalues["AS"+str(j)])
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("premia.csv", index=False)

# Extension Single Equation Regression + Fama-MacBeth CSVs
out_cols = OrderedDict({"SKILLS": skill_col})
reported = ['SKILL', 'LN_MCAP', 'BM', 'MOM']
for r in reported:
    for l in lags_list:
        out_cols["LAG" + str(l) + "_" + r + "_COEFFICIENT"] = []
        out_cols["LAG" + str(l) + "_" + r + "_SE"] = []
        out_cols["LAG" + str(l) + "_" + r + "_TSTAT"] = []
# Convert date to months
cog["DATE"] = (cog["DATE"] // 100) * 12 + (cog["DATE"] % 100)
for i in range(len(lags_list)):
    cog["DATE"] += offsets[i]
    m_c = cog.merge(ff, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="ffalpha ~ "+"S"+str(j)+"+"+' + '.join(cov_list), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_COEFFICIENT"].append(reg.params["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_SE"].append(reg.bse["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SKILL_TSTAT"].append(reg.tvalues["S"+str(j)])
        for r in reported[1:]:
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_COEFFICIENT"].append(reg.params[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_SE"].append(reg.bse[r])
            out_cols["LAG" + str(lags_list[i]) + "_" + r + "_TSTAT"].append(reg.tvalues[r])
        if output_fm_skill:
            # Write data out for Fama-Macbeth in MATLAB
            fm_out = m_c[['DATE', 'ffalpha', "S"+str(j)] + cov_list]
            fm_out.to_csv("./fama_macbeth_skill_csv/reg_" + "s"+str(j) + "_lag" + str(lags_list[i]) + ".csv", index=False)
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("premia_single_eq.csv", index=False)

