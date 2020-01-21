# collect_skills.py
# -------
# Writes a new CSV with percentage skills, sorted first by date and then by ticker
import pandas as pd
import ast
import os


def write_skills(input_name, output_name):
    # Create file and write header
    g = open(output_name, "w+")
    header = "DATE,TICKER"
    for i in range(50):
        header += ",S" + str(i)
    g.write(header + "\n")

    with open(input_name) as f:
        for line in f:
            # split line of cognism: 0:Symbol,1:YearMonth,2:Employees,3:AverageAge,4:KnownAge,5:Female,6:Male,7:NoSkills,8:AverageTenure,9:SkillsFrequencies
            current = line.rstrip('\n').split('\t')
            # skip malformed symbols and companies with 0 employees
            if "," in current[0] or int(current[2]) == 0:
                continue
            skills_arr = ast.literal_eval(current[9])
            # insert DATE, TICKER
            new_line = current[1] + "," + current[0]
            # insert lines for skill percents
            for i in range(50):
                new_line += "," + str(skills_arr[i] / int(current[2]))
            g.write(new_line + "\n")
    g.close()


def winsorize(input_name, output_name, cutoff):
    """
    Winsorize top and bottom of distributions of PERCENT, independently for each SKILL_CODE
    cutoff: integer percentage removed from top and bottom
    """
    code_to_lower_cut_val = {}  # maps every SKILL_CODE to the determined lower PERCENT value cutoff
    code_to_upper_cut_val = {}  # maps every SKILL_CODE to the determined upper PERCENT value cutoff

    # determine cut values
    in_df = pd.read_csv(input_name)
    for i in range(50):
        percents = list(in_df["S"+str(i)])
        percents.sort()
        low_ind = int(len(percents) * cutoff / 100)
        high_ind = len(percents) - low_ind
        code_to_lower_cut_val[i] = percents[low_ind]
        code_to_upper_cut_val[i] = percents[high_ind]

    # Create file
    g = open(output_name, "w+")

    # exclude values based on cutoffs
    with open(input_name) as f:
        skip = True
        for line in f:
            if skip:
                g.write(line)
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:S0, ... ,51:S49
            current = line.rstrip('\n').split(',')
            for i in range(50):
                if float(current[i+2]) < code_to_lower_cut_val[i]:
                    current[i+2] = str(code_to_lower_cut_val[i])
                elif float(current[i+2]) > code_to_upper_cut_val[i]:
                    current[i+2] = str(code_to_upper_cut_val[i])
            g.write(','.join(current) + "\n")
    g.close()


write_skills("cognism_current.txt", "intermed_current.csv")
write_skills("cognism_join.txt", "intermed_join.csv")
write_skills("cognism_leave.txt", "intermed_leave.csv")
winsorize("intermed_current.csv", "skills_current.csv", 1)
winsorize("intermed_join.csv", "skills_join.csv", 1)
winsorize("intermed_leave.csv", "skills_leave.csv", 1)
# Delete intermediate files
os.remove("intermed_current.csv")
os.remove("intermed_join.csv")
os.remove("intermed_leave.csv")
