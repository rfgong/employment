# compare_factor_functions.py
# -------
# Checks that factors.csv and FF3factor_returns.py yields the same output after they are run
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np

FF3 = pickle.load(open('FF3_Generated.csv', 'rb'), encoding='latin1')
tics = []
dates = []
vals = []
for tup in FF3:
    tics.append(tup[0])
    dat = str(tup[1]).split(".")
    if len(dat[1]) < 2:
        dat[1] += "0"
    dates.append(dat[0] + dat[1])
    vals.append(float(FF3[tup]))
cff3 = pd.DataFrame({"DATE": dates, "TICKER": tics, "cff3alpha": vals})
cff3.sort_values(by=["TICKER", "DATE"], inplace=True)
ff3 = pd.read_csv("ff3alphas.csv", dtype={'DATE': np.object})
ff3 = ff3.merge(cff3, on=["DATE", "TICKER"])
fig, ax = plt.subplots()
scatter = ax.scatter(
    ff3["cff3alpha"],
    ff3["ff3alpha"]
)
ax.set_xlabel("cff3alpha")
ax.set_ylabel("ff3alpha")
plt.show()

# record misalignment
ff3 = ff3[abs(ff3["cff3alpha"] - ff3["ff3alpha"]) > 0.0000000000001]
ff3.sort_values(by=["TICKER", "DATE"], inplace=True)
ff3.to_csv('mismatch.csv', index=False)

# fetch mismatched crsp rows
m = pd.read_csv("mismatch.csv")
crsp = pd.read_csv("crsp_full_month.csv")
crsp.dropna(inplace=True)
crsp = crsp.loc[crsp["TICKER"].isin(m["TICKER"].unique().tolist())]
crsp.sort_values(by=["TICKER"], inplace=True)
crsp.to_csv("mismatch_crsp.csv", index=False)
print(len(crsp["TICKER"].unique().tolist()))


