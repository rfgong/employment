"""
FILE HAS BEEN MODIFIED TO BE COMPATIBLE WITH REPLICATION CODE
"""
import datetime

import pandas as pd
import statsmodels.regression.linear_model as sm


## Script for computing FF3 alphas

# Load FF3 factors
FF3 = {}
FF3_file = open('F-F_Benchmark_Factors_Monthly_Generated.txt')
for line in FF3_file:
    columns = line.strip().split('\t')
    FF3[float(columns[0])/100] = [float(columns[1])/100,float(columns[2])/100,float(columns[3])/100]

# Security return from CRSP
crsp = open('crsp_full_month.csv')
ret = {}
# 0:PERMNO,1:date,2:TICKER,3:PRC,4:VOL,5:SHROUT,6:RETX,7:vwretx
skip = True
for line in crsp:
    if skip:
        skip = False
        continue
    columns = line.split(',')
    if len(columns[6])>0 and len(columns[2])>0 and columns[6] != 'C' and columns[6] != 'B':
        dt =  float(columns[1][0:4])+float(columns[1][4:6])/100
        if dt in FF3:
            if columns[2] not in ret:
                ret[columns[2]] = {}
            ret[columns[2]][dt] = [float(columns[6]),FF3[dt][0],FF3[dt][1],FF3[dt][2]]

# Run the time series regression for each firm, estimate monthly alphas
alphas = {}
print(len(ret))
count = 0
# g = open("m2_co.csv", "w+")
for item in ret:
    df = pd.DataFrame.from_dict(ret[item], orient='index',dtype=None)
    df.columns = ['ret','market','size','bm']
    df['intercept'] = 1.0
    train_cols = df.columns[1:]
    predict = sm.OLS(df['ret'].astype(float), df[train_cols].astype(float))
    result = predict.fit()
    # g.write(item + ": SMB " + str(result.params[1]) + " HML " + str(result.params[2]) + " Mkt " + str(result.params[0]) + "\n")
    # g.write(str(df) + "\n")
    for dt in ret[item]:
        alphas[(item,dt)] = ret[item][dt][0] - result.params[0]*ret[item][dt][1] - result.params[1]*ret[item][dt][2] - result.params[2]*ret[item][dt][3]
    count = count + 1
    if count%1000==0:
        print(count)
        print(datetime.datetime.now())

# Save output
import pickle
output = open('FF3_Generated.csv',"wb")
pickle.dump(alphas,output)
output.close()
