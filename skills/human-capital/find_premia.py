# find_premia.py
# -------
# Does core data path
import pandas as pd
import statsmodels.formula.api as sm

# Setup databases to read in from
market = pd.read_csv("market_measures.csv")
cog = pd.read_csv("skills_current.csv")
ff3 = pd.read_csv("ff3alphas.csv")
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
cov_list = list(cog.columns[53:])
print(cov_list)

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
# Convert date to months
abn["DATE"] = (abn["DATE"] // 100) * 12 + (abn["DATE"] % 100)
ff3["DATE"] = (ff3["DATE"] // 100) * 12 + (ff3["DATE"] % 100)
# Regression with Lags
lags_list = [1, 2, 3, 6]
offsets = [lags_list[0]] + [lags_list[i] - lags_list[i-1] for i in range(1, len(lags_list))]
skill_col = ["[0] Personal Coaching", "[1] Business Development", "[2] Logistics", "[3] Business Development", "[4] Digital Marketing", "[5] Administration", "[6] Hospitality", "[7] Business Development", "[8] Musical Production", "[9] Industrial Management", "[10] Human Resources (Junior)", "[11] Human Resources (Senior)", "[12] Visual Design", "[13] Data Analysis", "[14] Business Development", "[15] Recruiting", "[16] Education", "[17] Business Development", "[18] Operations Management", "[19] Middle Management", "[20] Pharmaceutical", "[21] Product Management", "[22] Healthcare", "[23] Sales", "[24] Insurance", "[25] Social Media and Communications", "[26] Web Development", "[27] Manufacturing and Process Management", "[28] Electrical Engineering", "[29] Legal", "[30] Graphic Design", "[31] Non-Profit and Community", "[32] Retail and Fashion", "[33] Real Estate", "[34] Military", "[35] Accounting and Auditing", "[36] Administration", "[37] IT Management and Support", "[38] Construction Management", "[39] Video and Film Production", "[40] CRM and Sales Management", "[41] Energy, Oil, and Gas", "[42] Mobile Telecommunications", "[43] Software Engineering", "[44] Banking and Finance", "[45] Web Design", "[46] Public Policy", "[47] Business Development", "[48] Technical Product Management", "[49] Sales Management"]
out_cols = {"SKILLS": skill_col}
for l in lags_list:
    out_cols["LAG" + str(l) + "_COEFFICIENT"] = []
    out_cols["LAG" + str(l) + "_SE"] = []
    out_cols["LAG" + str(l) + "_TSTAT"] = []
for i in range(len(lags_list)):
    abn["DATE"] += offsets[i]
    m_c = abn.merge(ff3, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="ff3alpha ~ "+"AS"+str(j), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_COEFFICIENT"].append(reg.params["AS"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SE"].append(reg.bse["AS"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_TSTAT"].append(reg.tvalues["AS"+str(j)])
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("premia.csv", index=False)

# Extension Single Equation Regression + Fama-MacBeth CSVs
out_cols = {"SKILLS": skill_col}
for l in lags_list:
    out_cols["LAG" + str(l) + "_COEFFICIENT"] = []
    out_cols["LAG" + str(l) + "_SE"] = []
    out_cols["LAG" + str(l) + "_TSTAT"] = []
# Convert date to months
cog["DATE"] = (cog["DATE"] // 100) * 12 + (cog["DATE"] % 100)
for i in range(len(lags_list)):
    cog["DATE"] += offsets[i]
    m_c = cog.merge(ff3, on=["DATE", "TICKER"])
    for j in range(50):
        reg = sm.ols(formula="ff3alpha ~ "+"S"+str(j)+"+"+' + '.join(cov_list), data=m_c).fit()
        out_cols["LAG" + str(lags_list[i]) + "_COEFFICIENT"].append(reg.params["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_SE"].append(reg.bse["S"+str(j)])
        out_cols["LAG" + str(lags_list[i]) + "_TSTAT"].append(reg.tvalues["S"+str(j)])
        """
        fm_out = m_c[['DATE', 'ff3alpha', "S"+str(j)] + cov_list]
        fm_out.to_csv("./fama_macbeth_csv/reg_" + "s"+str(j) + "_lag" + str(lags_list[i]) + ".csv", index=False)
        """
# Write output
out = pd.DataFrame(out_cols)
out.to_csv("premia_single_eq.csv", index=False)

# Extension Tobit

