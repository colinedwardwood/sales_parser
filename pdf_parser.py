import pdfplumber
import csv
import re
from os import path
from glob import glob  

def find_ext(dr, ext):
    return glob(path.join(dr,"*.{}".format(ext)))

def parse_name(line):
    pos_firstslash = line.find("/")  # first find the position of the first slash in the line, it is the only consistent character
    pos_spacebefore_firstslash = line[:pos_firstslash].rfind(" ")  # first the last space before the first slash, this is the end of the policy number
    name_and_policy = line[:pos_spacebefore_firstslash]  # slice the line at this position

    pos_name_policy_divider = name_and_policy.rfind(" ")
    name = name_and_policy[:pos_name_policy_divider].strip()
    policy = name_and_policy[pos_name_policy_divider:].strip()
    rest = line[pos_spacebefore_firstslash:].strip()

    line_list = []
    line_list = rest.split()
    line_list.insert(0,policy)
    line_list.insert(0, name)
    return line_list

def parse_dates(line):
    result = re.search('\d{2}.\d{2}.\d{4}', line)
    start_date = result.group()
    end_date = re.search('\d{2}.\d{2}.\d{4}',line[result.end():]).group()
    tmp = start_date+"_"+end_date+".csv"
    result = tmp.replace("/","-")
    return result

def parse_file(file):
    with pdfplumber.open(file) as pdf:
        lines = []  # empty list to store processed lines
        filename = ""
        for page in range(0, len(pdf.pages)-1):
            start = False  # keep track of whether or not the start of the table has been reached
            first_page = pdf.pages[page]  # get the first page
            txt = first_page.extract_text().splitlines()  # extract the text from the first page and split into list of lines
            for i in range(0, len(txt)-1):
                if start == True:
                    lines.append(parse_name(txt[i]))
                if "PolicyHolder" in txt[i]:
                    start = True
                if "TRANSACTION DATES" in txt[i] and len(filename) == 0:
                    filename = parse_dates(txt[i])
        
        
        with open("/Users/colin/Code/sales_parser/csvs/"+filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(lines)
            print(filename, "written.")
    return None
            
files = find_ext("/Users/colin/Code/sales_parser/pdfs/","PDF")

for file in files:
    parse_file(file)
