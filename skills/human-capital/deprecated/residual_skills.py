# residual_skills.py
# -------
# Writes a new CSV with abnormal percentage skills
import pandas as pd
import statsmodels.formula.api as sm


def write_abn_skills(skills_file_name, market_file_name, output_name):
    # Create file
    g = open(output_name, "w+")
    header = "DATE,TICKER,ABN_PERCENT\n"
    g.write(header)

    # For ols regression step
    date = []  # list of DATE
    ticker = []  # list of TICKER
    skills = []  # list of PERCENT skills
    mc = []  # list of LN_MCAP
    bm = []  # list of BM
    mom = []  # list of MOM
    # prepare industry dummy lists, n-1 are permitted with NAICS "11" omitted
    industry_to_values = {}
    permitted_inds = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                      "62", "71", "72", "81", "92"]
    for ind in permitted_inds:
        industry_to_values[ind] = []

    skills_f = open(skills_file_name)
    skills_f.readline()  # skip header
    skills_lines = skills_f.readlines()
    skills_index = 0
    terminate = False
    with open(market_file_name) as market_f:
        skip = True
        for line in market_f:
            if skip:
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:BM,4:INDUSTRY,5:MOM
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:PERCENT
            current_skills = skills_lines[skills_index].rstrip('\n').split(',')
            # market date must be in YYYYMM format
            current_market[0] = current_market[0][:6]
            # check date alignment
            if current_market[0] < current_skills[0]:
                continue
            while current_skills[0] < current_market[0]:
                skills_index += 1
                if skills_index >= len(skills_lines):
                    terminate = True
                    break
                current_skills = skills_lines[skills_index].rstrip('\n').split(',')
            if terminate:
                break
            # updated skills ticker passes current market ticker or updated skills date passes current market date
            if current_market[0] < current_skills[0] or current_market[1] < current_skills[1]:
                continue
            while current_skills[1] < current_market[1]:
                skills_index += 1
                if skills_index >= len(skills_lines):
                    terminate = True
                    break
                current_skills = skills_lines[skills_index].rstrip('\n').split(',')
                # make sure date still aligned
                if current_market[0] < current_skills[0]:
                    break
            if terminate:
                break
            # updated skills ticker passes current market ticker or updated skills date passes current market date
            if current_market[0] < current_skills[0] or current_market[1] < current_skills[1]:
                continue
            date.append(current_skills[0])
            ticker.append(current_skills[1])
            # add to regression data
            skills.append(float(current_skills[2]))
            mc.append(float(current_market[2]))
            bm.append(float(current_market[3]))
            mom.append(float(current_market[5]))
            for ind in permitted_inds:
                if current_market[4] == ind:
                    industry_to_values[ind].append(1)
                else:
                    industry_to_values[ind].append(0)
    # Create pandas data frame and run regression with statsmodels
    df = pd.DataFrame({"Y": skills, "B": mc, "C": bm,
                       "D": industry_to_values["21"], "E": industry_to_values["22"], "F": industry_to_values["23"],
                       "G": industry_to_values["31"], "H": industry_to_values["42"], "I": industry_to_values["44"],
                       "J": industry_to_values["48"], "K": industry_to_values["51"], "L": industry_to_values["52"],
                       "M": industry_to_values["53"], "N": industry_to_values["54"], "O": industry_to_values["55"],
                       "P": industry_to_values["56"], "Q": industry_to_values["61"], "R": industry_to_values["62"],
                       "S": industry_to_values["71"], "T": industry_to_values["72"], "U": industry_to_values["81"],
                       "V": industry_to_values["92"], "W": mom})
    result = sm.ols(formula="Y ~ B + C + D + E + F + G + H + I + J + K + L + M + N + O + P + Q + R + S + T + U + V + W",
                    data=df).fit()
    # save ABN_PERCENT skills
    abn = list(result.resid)
    # write output
    for i in range(len(abn)):
        new_line = date[i] + "," + ticker[i] + "," + str(abn.pop(0)) + "\n"
        g.write(new_line)
    g.close()


input_prefix = "skills_current_"
output_prefix = "abn_skills_current_"
for i in range(50):
    write_abn_skills(input_prefix + str(i) + ".csv", "market_measures.csv", output_prefix + str(i) + ".csv")
input_prefix = "skills_join_"
output_prefix = "abn_skills_join_"
for i in range(50):
    write_abn_skills(input_prefix + str(i) + ".csv", "market_measures.csv", output_prefix + str(i) + ".csv")
input_prefix = "skills_leave_"
output_prefix = "abn_skills_leave_"
for i in range(50):
    write_abn_skills(input_prefix + str(i) + ".csv", "market_measures.csv", output_prefix + str(i) + ".csv")
