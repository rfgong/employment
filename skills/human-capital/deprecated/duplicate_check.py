# duplicate_check.py
# -------
# Checks for duplicates
import pandas as pd
import numpy as np

"""
compustat = pd.read_csv("compustat_full_copy.csv")
compustat.dropna(inplace=True)
nf = len(compustat)
duplicate2 = compustat[compustat.duplicated(subset=['tic', 'datadate'], keep=False)]
redundancy2 = len(duplicate2)
# print("NUM ROWS WITH DUPLICATED tic + datadate: " + str(redundancy2))
duplicate3 = duplicate2[duplicate2.duplicated(subset=['tic', 'datadate', 'ceqq'], keep=False)]
redundancy3 = len(duplicate3)
# print("NUM ROWS WITH DUPLICATED tic + datadate + ceqq: " + str(redundancy3))
print("NUM ROWS WITH DATA DISCREPANCIES: " + str(redundancy2 - redundancy3))
print((redundancy2 - redundancy3) / nf * 100)
problematic = duplicate2.drop_duplicates(subset=['tic', 'datadate', 'ceqq'], keep=False)
problematic.sort_values(by=['tic', "datadate"], inplace=True)
problematic.to_csv("problematic_compustat.csv", index=False)
"""

crsp = pd.read_csv("crsp_code.csv")
crsp.dropna(inplace=True)
gn = len(crsp)
# crsp = crsp[crsp['SHRCD'] == 11 or crsp['SHRCD'] == 10]
nf = len(crsp)
print("TOT: " + str(gn))
print(nf / gn * 100)
duplicate3 = crsp[crsp.duplicated(subset=['date', 'TICKER', 'SHRCD'], keep=False)]
redundancy3 = len(duplicate3)
duplicate6 = crsp[crsp.duplicated(subset=['date', 'TICKER', 'SHRCD', 'RETX', 'PRC', 'SHROUT'], keep=False)]
redundancy6 = len(duplicate6)
print("NUM ROWS WITH DATA DISCREPANCIES: " + str(redundancy3 - redundancy6))
print((redundancy3 - redundancy6) / nf * 100)
problematic = duplicate3.drop_duplicates(subset=['date', 'TICKER', 'SHRCD', 'RETX', 'PRC', 'SHROUT'], keep=False)
problematic.sort_values(by=['date', 'TICKER'], inplace=True)
problematic.to_csv("problematic_crsp.csv", index=False)


cog_c = pd.read_csv("skills_current.csv")
cog_j = pd.read_csv("skills_join.csv")
cog_l = pd.read_csv("skills_leave.csv")
union = set(cog_c["TICKER"].unique().tolist()) | set(cog_j["TICKER"].unique().tolist()) | set(cog_l["TICKER"].unique().tolist()) | set(problematic["TICKER"].unique().tolist())
intersect = set(cog_c["TICKER"].unique().tolist()) & set(cog_j["TICKER"].unique().tolist()) & set(cog_l["TICKER"].unique().tolist()) & set(problematic["TICKER"].unique().tolist())
print("UNION NO DROP: " + str(len(union)))
print("INTERSECT NO DROP: " + str(len(intersect)))
"""
crsp = crsp[crsp['SHRCLS'] == 'A']
crsp.dropna(inplace=True)
union = set(cog_c["TICKER"].unique().tolist()) | set(cog_j["TICKER"].unique().tolist()) | set(cog_l["TICKER"].unique().tolist()) | set(crsp["TICKER"].unique().tolist())
intersect = set(cog_c["TICKER"].unique().tolist()) & set(cog_j["TICKER"].unique().tolist()) & set(cog_l["TICKER"].unique().tolist()) & set(crsp["TICKER"].unique().tolist())
print("UNION A SHARES: " + str(len(union)))
print("INTERSECT A SHARES: " + str(len(intersect)))

crsp = pd.read_csv("crsp_class.csv")
crsp = crsp[crsp['SHRCLS'] != 'A']
crsp['SHRCLS'] = 'B'
crsp.dropna(inplace=True)
union = set(cog_c["TICKER"].unique().tolist()) | set(cog_j["TICKER"].unique().tolist()) | set(cog_l["TICKER"].unique().tolist()) | set(crsp["TICKER"].unique().tolist())
intersect = set(cog_c["TICKER"].unique().tolist()) & set(cog_j["TICKER"].unique().tolist()) & set(cog_l["TICKER"].unique().tolist()) & set(crsp["TICKER"].unique().tolist())
print("UNION NOT A SHARES: " + str(len(union)))
print("INTERSECT NOT A SHARES: " + str(len(intersect)))
"""



