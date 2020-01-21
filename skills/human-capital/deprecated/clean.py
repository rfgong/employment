# clean.py
# -------
# Writes new CSVs that only have mutually shared tickers and are sorted by date
import pandas as pd
import databases as d

# setup databases to read in from
compustat = d.PandasDatabase("compustat_full_month.csv")
crsp = d.PandasDatabase("crsp_full_month.csv")
cog_c = d.PandasDatabase("cognism_current.csv")
cog_j = d.PandasDatabase("cognism_join.csv")
cog_l = d.PandasDatabase("cognism_leave.csv")
# Find shared firms between databases
compustat.recordTickers("tic", False)
crsp.recordTickers("TICKER", False)
cog_c.recordTickers("Symbol", False)
cog_j.recordTickers("Symbol", False)
cog_l.recordTickers("Symbol", False)
sharedTics = list(set(compustat.tics) & set(crsp.tics) & set(cog_c.tics) & set(cog_j.tics) & set(cog_l.tics))


def keep_shared(file_name, new_name, shared_tics, tic_col_num, row_size):
    g = open(new_name, "w+")
    with open(file_name) as f:
        skip = True
        for line in f:
            if skip:
                g.write(line)
                skip = False
                continue
            current = line.rstrip('\n').split(',')
            if (current[tic_col_num] in shared_tics) and len(current) == row_size:
                empty_check = False
                for v in current:
                    if not v:
                        empty_check = True
                        break
                if not empty_check:
                    g.write(line)
    g.close()


def sort_by_date(file_name, new_name, date_col_name):
    df = pd.read_csv(file_name)
    df.sort_values(by=[date_col_name], inplace=True)
    df.to_csv(new_name, index=False)


keep_shared("compustat_full_month.csv", "reduced_compustat_full_month.csv", sharedTics, 4, 8)
sort_by_date("reduced_compustat_full_month.csv", "reduced_compustat_full_month.csv", "rdq")
keep_shared("crsp_full_month.csv", "reduced_crsp_full_month.csv", sharedTics, 2, 8)
sort_by_date("reduced_crsp_full_month.csv", "reduced_crsp_full_month.csv", "date")
keep_shared("cognism_current.csv", "reduced_cognism_current.csv", sharedTics, 0, 59)
sort_by_date("reduced_cognism_current.csv", "reduced_cognism_current.csv", "YearMonth")
keep_shared("cognism_join.csv", "reduced_cognism_join.csv", sharedTics, 0, 59)
sort_by_date("reduced_cognism_join.csv", "reduced_cognism_join.csv", "YearMonth")
keep_shared("cognism_leave.csv", "reduced_cognism_leave.csv", sharedTics, 0, 59)
sort_by_date("reduced_cognism_leave.csv", "reduced_cognism_leave.csv", "YearMonth")
