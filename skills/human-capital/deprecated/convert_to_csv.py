# convert_to_csv.py
# -------
# Converts tab delimited file to comma delimited file
import csv


def convert(text_file, csv_file):
    in_txt = csv.reader(open(text_file, "r"), delimiter='\t')
    out_csv = csv.writer(open(csv_file, 'w'))
    header = ["Symbol","YearMonth","Employees","AverageAge","KnownAge","Female","Male","NoSkills","AverageTenure","SkillsFrequencies"]
    out_csv.writerow(header)
    out_csv.writerows(in_txt)


convert("cognism_current.txt", "cognism_current.csv")
convert("cognism_join.txt", "cognism_join.csv")
convert("cognism_leave.txt", "cognism_leave.csv")
