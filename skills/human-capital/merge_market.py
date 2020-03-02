# merge_market.py
# -------
# Merges COMPUSTAT and CRSP and writes a new CSV, sorted first by date and then by ticker
import databases as d
import utils_direct as ud
import pandas as pd
import os

compustat = pd.read_csv("compustat_full_month.csv")
compustat.dropna(inplace=True)
compustat = compustat.drop_duplicates(subset=['tic', 'datadate'], keep=False)
compustat.sort_values(by=['datadate'], inplace=True)

crsp = pd.read_csv("crsp_full_month.csv")
crsp = crsp[['PERMNO', 'date', 'TICKER', 'PRC', 'VOL', 'SHROUT', 'RET', 'vwretx']]  # For code compatibility
crsp.dropna(inplace=True)
crsp = crsp.drop_duplicates(subset=['date', 'TICKER'], keep=False)
crsp = crsp[(crsp['RET'] != 'R') & (crsp['RET'] != 'C')]
crsp.sort_values(by=['date'], inplace=True)

sharedTics = list(set(compustat["tic"].unique().tolist()) & set(crsp["TICKER"].unique().tolist()))
compustat = compustat.loc[compustat["tic"].isin(sharedTics)]
crsp = crsp.loc[crsp["TICKER"].isin(sharedTics)]
compustat.to_csv("reduced_compustat_full_month.csv", index=False)
crsp.to_csv("reduced_crsp_full_month.csv", index=False)

compustat = d.BookDatabase("reduced_compustat_full_month.csv")

# Create file and write header
file_name = "market_measures.csv"
g = open(file_name, "w+")
header = "DATE,TICKER,INDUSTRY,LN_MCAP,BM,MOM\n"
g.write(header)

ticker_to_YYYYMM_to_prc = {}  # Maps each ticker to a dictionary, which maps YYYYMM to prc

with open("reduced_crsp_full_month.csv") as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # split line of crsp: 0:PERMNO,1:date,2:TICKER,3:PRC,4:VOL,5:SHROUT,6:RET,7:vwretx
        current = line.rstrip('\n').split(',')
        # save the PRC for later reference
        if current[2] not in ticker_to_YYYYMM_to_prc:
            # create a dictionary for firm
            ticker_to_YYYYMM_to_prc[current[2]] = {}
        key = current[1][:6]  # creates current YYYYMM key
        ticker_to_YYYYMM_to_prc[current[2]][key] = abs(float(current[3]))  # PRC may be negative bid-ask average
        # insert DATE, TICKER
        new_line = key + "," + current[2]
        if float(current[5]) == 0:  # SHROUT may be zero if it is missing
            continue
        mcap = ud.marketCap(abs(float(current[3])), float(current[5]))
        # insert industry
        ind_code = compustat.getIndustryCode(current[2])
        new_line += "," + str(ind_code)
        # insert LN_MCAP
        new_line += "," + str(ud.marketCapLN(mcap))
        # insert BM
        book = compustat.getBookValue(current[2], current[1])
        if book == -1:
            continue
        else:
            new_line += "," + str(book / mcap)
        # insert MOM
        mom = ud.momentum(key, ticker_to_YYYYMM_to_prc[current[2]])
        if mom == "":
            continue
        else:
            new_line += "," + mom
        new_line += "\n"
        g.write(new_line)
g.close()

# Sort by date and ticker
df = pd.read_csv(file_name)
df.sort_values(by=["DATE", "TICKER"], inplace=True)
df.to_csv(file_name, index=False)

# Delete intermediate files
os.remove("reduced_compustat_full_month.csv")
os.remove("reduced_crsp_full_month.csv")

