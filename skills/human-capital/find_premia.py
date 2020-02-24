# run.py
# -------
# Does core data path
import pandas as pd
import statsmodels.formula.api as sm

# Setup databases to read in from
market = pd.read_csv("market_measures.csv")
cog_c = pd.read_csv("skills_current.csv")
cog_j = pd.read_csv("skills_join.csv")
cog_l = pd.read_csv("skills_leave.csv")
ff3 = pd.read_csv("ff3alphas.csv")
# Add monthly controls to market data
dummy_month = pd.get_dummies(market['DATE'], prefix='month')
month_col = list(dummy_month.columns.values)
market = market.join(dummy_month.loc[:, month_col[1]:])
# Merge cognism with market
cog_c = cog_c.merge(market, on=["DATE", "TICKER"])
cog_j = cog_j.merge(market, on=["DATE", "TICKER"])
cog_l = cog_l.merge(market, on=["DATE", "TICKER"])

cols = {"DATE": [], "TICKER": []}
for i in range(50):
    cols["AS" + str(i)] = []
abn_c = pd.DataFrame(cols)
abn_c["DATE"] = cog_c["DATE"]
abn_c["TICKER"] = cog_c["TICKER"]
abn_j = pd.DataFrame(cols)
abn_j["DATE"] = cog_j["DATE"]
abn_j["TICKER"] = cog_j["TICKER"]
abn_l = pd.DataFrame(cols)
abn_l["DATE"] = cog_l["DATE"]
abn_l["TICKER"] = cog_l["TICKER"]
# Find AbnSkills
dependent_vars = ' + '.join(market.columns[2:])
for i in range(50):
    reg = sm.ols(formula="S"+str(i)+" ~ "+dependent_vars, data=cog_c).fit()
    abn_c["AS" + str(i)] = reg.resid
for i in range(50):
    reg = sm.ols(formula="S"+str(i)+" ~ "+dependent_vars, data=cog_j).fit()
    abn_j["AS" + str(i)] = reg.resid
for i in range(50):
    reg = sm.ols(formula="S"+str(i)+" ~ "+dependent_vars, data=cog_l).fit()
    abn_l["AS" + str(i)] = reg.resid

# Convert date to months
abn_c["DATE"] = (abn_c["DATE"] // 100) * 12 + (abn_c["DATE"] % 100)
abn_j["DATE"] = (abn_j["DATE"] // 100) * 12 + (abn_j["DATE"] % 100)
abn_l["DATE"] = (abn_l["DATE"] // 100) * 12 + (abn_l["DATE"] % 100)
ff3["DATE"] = (ff3["DATE"] // 100) * 12 + (ff3["DATE"] % 100)

skill_col = ["[0] Personal Coaching", "[1] Business Development", "[2] Logistics", "[3] Business Development", "[4] Digital Marketing", "[5] Administration", "[6] Hospitality", "[7] Business Development", "[8] Musical Production", "[9] Industrial Management", "[10] Human Resources (Junior)", "[11] Human Resources (Senior)", "[12] Visual Design", "[13] Data Analysis", "[14] Business Development", "[15] Recruiting", "[16] Education", "[17] Business Development", "[18] Operations Management", "[19] Middle Management", "[20] Pharmaceutical", "[21] Product Management", "[22] Healthcare", "[23] Sales", "[24] Insurance", "[25] Social Media and Communications", "[26] Web Development", "[27] Manufacturing and Process Management", "[28] Electrical Engineering", "[29] Legal", "[30] Graphic Design", "[31] Non-Profit and Community", "[32] Retail and Fashion", "[33] Real Estate", "[34] Military", "[35] Accounting and Auditing", "[36] Administration", "[37] IT Management and Support", "[38] Construction Management", "[39] Video and Film Production", "[40] CRM and Sales Management", "[41] Energy, Oil, and Gas", "[42] Mobile Telecommunications", "[43] Software Engineering", "[44] Banking and Finance", "[45] Web Design", "[46] Public Policy", "[47] Business Development", "[48] Technical Product Management", "[49] Sales Management"]
out_cols_c = {"SKILLS": skill_col, "LAG1_COEFFICIENT": [], "LAG1_SE": [], "LAG1_TSTAT": [],
              "LAG2_COEFFICIENT": [], "LAG2_SE": [], "LAG2_TSTAT": [],
              "LAG3_COEFFICIENT": [], "LAG3_SE": [], "LAG3_TSTAT": [],
              "LAG6_COEFFICIENT": [], "LAG6_SE": [], "LAG6_TSTAT": []}
out_cols_j = {"SKILLS": skill_col, "LAG1_COEFFICIENT": [], "LAG1_SE": [], "LAG1_TSTAT": [],
              "LAG2_COEFFICIENT": [], "LAG2_SE": [], "LAG2_TSTAT": [],
              "LAG3_COEFFICIENT": [], "LAG3_SE": [], "LAG3_TSTAT": [],
              "LAG6_COEFFICIENT": [], "LAG6_SE": [], "LAG6_TSTAT": []}
out_cols_l = {"SKILLS": skill_col, "LAG1_COEFFICIENT": [], "LAG1_SE": [], "LAG1_TSTAT": [],
              "LAG2_COEFFICIENT": [], "LAG2_SE": [], "LAG2_TSTAT": [],
              "LAG3_COEFFICIENT": [], "LAG3_SE": [], "LAG3_TSTAT": [],
              "LAG6_COEFFICIENT": [], "LAG6_SE": [], "LAG6_TSTAT": []}

# Regression 1 Month Lag
abn_c["DATE"] += 1
abn_j["DATE"] += 1
abn_l["DATE"] += 1
m_c = abn_c.merge(ff3, on=["DATE", "TICKER"])
m_j = abn_j.merge(ff3, on=["DATE", "TICKER"])
m_l = abn_l.merge(ff3, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_c).fit()
    out_cols_c["LAG1_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_c["LAG1_SE"].append(reg.bse["AS"+str(i)])
    out_cols_c["LAG1_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_j).fit()
    out_cols_j["LAG1_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_j["LAG1_SE"].append(reg.bse["AS"+str(i)])
    out_cols_j["LAG1_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_l).fit()
    out_cols_l["LAG1_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_l["LAG1_SE"].append(reg.bse["AS"+str(i)])
    out_cols_l["LAG1_TSTAT"].append(reg.tvalues["AS"+str(i)])

# Regression 2 Month Lag
abn_c["DATE"] += 1
abn_j["DATE"] += 1
abn_l["DATE"] += 1
m_c = abn_c.merge(ff3, on=["DATE", "TICKER"])
m_j = abn_j.merge(ff3, on=["DATE", "TICKER"])
m_l = abn_l.merge(ff3, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_c).fit()
    out_cols_c["LAG2_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_c["LAG2_SE"].append(reg.bse["AS"+str(i)])
    out_cols_c["LAG2_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_j).fit()
    out_cols_j["LAG2_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_j["LAG2_SE"].append(reg.bse["AS"+str(i)])
    out_cols_j["LAG2_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_l).fit()
    out_cols_l["LAG2_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_l["LAG2_SE"].append(reg.bse["AS"+str(i)])
    out_cols_l["LAG2_TSTAT"].append(reg.tvalues["AS"+str(i)])

# Regression 3 Month Lag
abn_c["DATE"] += 1
abn_j["DATE"] += 1
abn_l["DATE"] += 1
m_c = abn_c.merge(ff3, on=["DATE", "TICKER"])
m_j = abn_j.merge(ff3, on=["DATE", "TICKER"])
m_l = abn_l.merge(ff3, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_c).fit()
    out_cols_c["LAG3_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_c["LAG3_SE"].append(reg.bse["AS"+str(i)])
    out_cols_c["LAG3_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_j).fit()
    out_cols_j["LAG3_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_j["LAG3_SE"].append(reg.bse["AS"+str(i)])
    out_cols_j["LAG3_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_l).fit()
    out_cols_l["LAG3_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_l["LAG3_SE"].append(reg.bse["AS"+str(i)])
    out_cols_l["LAG3_TSTAT"].append(reg.tvalues["AS"+str(i)])

# Regression 6 Month Lag
abn_c["DATE"] += 3
abn_j["DATE"] += 3
abn_l["DATE"] += 3
m_c = abn_c.merge(ff3, on=["DATE", "TICKER"])
m_j = abn_j.merge(ff3, on=["DATE", "TICKER"])
m_l = abn_l.merge(ff3, on=["DATE", "TICKER"])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_c).fit()
    out_cols_c["LAG6_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_c["LAG6_SE"].append(reg.bse["AS"+str(i)])
    out_cols_c["LAG6_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_j).fit()
    out_cols_j["LAG6_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_j["LAG6_SE"].append(reg.bse["AS"+str(i)])
    out_cols_j["LAG6_TSTAT"].append(reg.tvalues["AS"+str(i)])
for i in range(50):
    reg = sm.ols(formula="ff3alpha ~ " + "AS"+str(i), data=m_l).fit()
    out_cols_l["LAG6_COEFFICIENT"].append(reg.params["AS"+str(i)])
    out_cols_l["LAG6_SE"].append(reg.bse["AS"+str(i)])
    out_cols_l["LAG6_TSTAT"].append(reg.tvalues["AS"+str(i)])

# Write output
out_c = pd.DataFrame(out_cols_c)
out_j = pd.DataFrame(out_cols_j)
out_l = pd.DataFrame(out_cols_l)

out_c.to_csv("premia_current.csv", index=False)
out_j.to_csv("premia_join.csv", index=False)
out_l.to_csv("premia_leave.csv", index=False)


