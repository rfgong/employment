import pandas as pd

# Convert compustat
header = "gvkey,datadate,fyearq,fqtr,indfmt,consol,popsrc,datafmt,tic,cusip,curcdq,datacqtr,datafqtr,rdq,ceqq,cshoq,epsf12,epsfxq,xrdq,costat,prccq,naics".split(",")
compustat = pd.read_csv("./paper_dataset/Compustat_2000_2016.txt", sep='\t', names=header)
compustat = compustat[['gvkey', 'datadate', 'fyearq', 'fqtr', 'tic', 'rdq', 'ceqq', 'naics']]
compustat.to_csv("compustat_original.csv", index=False)

# Convert crsp
header = "PERMNO,date,SHRCD,TICKER,COMNAM,NAICS,CUSIP,DLSTCD,ACPERM,DLPRC,PRC,VOL,RET,SHROUT,sprtrn".split(",")
crsp = pd.read_csv("./paper_dataset/CRSP_2000_2016.txt", sep='\t', names=header)
# Does not contain RETX or vwretx
crsp = crsp[['PERMNO', 'date', 'TICKER', 'PRC', 'VOL', 'SHROUT', 'RET']]
crsp.to_csv("crsp_original.csv", index=False)


