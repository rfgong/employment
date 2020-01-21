# merge_market.py
# -------
# Merges COMPUSTAT and CRSP and writes a new CSV, sorted first by date and then by ticker
import databases as d
import utils_direct as ud
import pandas as pd

compustat = pd.read_csv("compustat_full_month.csv")
compustat.dropna(inplace=True)
compustat = compustat.drop_duplicates(subset=['tic', 'rdq'], keep='first')  # compustat has redundancy

crsp = pd.read_csv("crsp_full_month.csv")
crsp.dropna(inplace=True)
crsp = crsp.drop_duplicates(subset=['date', 'TICKER'], keep='first')  # crsp has redundancy

sharedTics = list(set(compustat["tic"].unique().tolist()) & set(crsp["TICKER"].unique().tolist()))
compustat = compustat.loc[compustat["tic"].isin(sharedTics)]
compustat.to_csv("compustat_full_month.csv", index=False)
crsp = crsp.loc[crsp["TICKER"].isin(sharedTics)]
crsp.to_csv("crsp_full_month.csv", index=False)

compustat = d.BookDatabase("compustat_full_month.csv")
# Industry dummy lists, n-1 are permitted with NAICS "11" omitted
permitted_inds = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                  "62", "71", "72", "81", "92"]

# Create file and write header
file_name = "market_measures.csv"
g = open(file_name, "w+")
header = "DATE,TICKER,LN_MCAP,BM"
for ind in permitted_inds:
    header += ",I" + ind
g.write(header + ",MOM\n")

ticker_to_YYYYMM_to_ret = {}  # Maps each ticker to a dictionary, which maps YYYYMM to return

with open("crsp_full_month.csv") as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # split line of crsp: 0:PERMNO,1:date,2:TICKER,3:PRC,4:VOL,5:SHROUT,6:RETX,7:vwretx
        current = line.rstrip('\n').split(',')
        # skip if RETX is invalid
        if current[6] == 'C' or current[6] == 'R':
            continue
        # save the RETX for later reference
        if current[2] not in ticker_to_YYYYMM_to_ret:
            # create a dictionary for firm
            ticker_to_YYYYMM_to_ret[current[2]] = {}
        key = current[1][:6]  # creates current YYYYMM key
        ticker_to_YYYYMM_to_ret[current[2]][key] = float(current[6])
        # insert DATE, TICKER
        new_line = key + "," + current[2]
        if float(current[5]) == 0:  # SHROUT may be zero if it is missing
            continue
        mcap = ud.marketCap(abs(float(current[3])), float(current[5]))  # PRC may be negative bid-ask average
        # insert LN_MCAP
        new_line += "," + str(ud.marketCapLN(mcap))
        # insert BM
        book = compustat.getBookValue(current[2], current[1])
        if book == -1:
            continue
        else:
            new_line += "," + str(book / mcap)
        # insert industry codes
        ind_code = compustat.getIndustryCode(current[2])
        for ind in permitted_inds:
            if ind_code == ind:
                new_line += ",1"
            else:
                new_line += ",0"
        # insert MOM
        mom = ud.momentum(key, ticker_to_YYYYMM_to_ret[current[2]])
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
