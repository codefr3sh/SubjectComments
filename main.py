"""
Created by:    Philip van Schalkwyk
Contact:       philiplvans@gmail.com
Last updated:  2021-11-25

This script is used to automatically generate subject comments for English
first additional language students, based on:
    - Task Scores
    - Final quarter mark
    - Misc. comments such as additional reading required, or being a pleasure in class
In this branch, we will attempt to use Pandas to read the CSV file
"""

# TODO: Query user for subject, if english, is it home or additional language? Use relevant Function

import csv
import pandas as pd
import random
from pathlib import Path
import os
import xlsxwriter

# Variables for all the different files and folders that will be used to read and write data
# Set the current working directory to the folder in which the file is contained
CWD = os.getcwd()
CSV_DIR = CWD + r"\csv"
TXT_DIR = CWD + r"\comment_output"
COMMENT_DIR = CWD + r"\comment_input"

# File Variables
FAIL_F = COMMENT_DIR + r"\1_fail.txt"
CARE_F = COMMENT_DIR + r"\2_careful.txt"
SATIS_F = COMMENT_DIR + r"\3_satisfactory.txt"
GOOD_F = COMMENT_DIR + r"\4_good.txt"
EXCEL_F = COMMENT_DIR + r"\5_excellent.txt"
ASS_F = COMMENT_DIR + r"\6_assessmentfail.txt"
PLEASURE_F = COMMENT_DIR + r"\7_pleasure.txt"
ATT_F = COMMENT_DIR + r"\8_attention.txt"
DISRUPT_F = COMMENT_DIR + r"\9_disrupt.txt"
READ_F = COMMENT_DIR + r"\10_read.txt"

# Main function
# TODO: add main function code
# TODO: P1 - Cleanup functions - Random function to take more parameters
# TODO: Add check gender function
# TODO: Add functions to return the correct pronouns depending on gender
# TODO: Parse filename to determine subject and level


def main():
    # Iterate through CSV files in input directory
    for file in Path(CSV_DIR).glob("*.csv"):
        class_path = file.name[:-4]
        df = csv_to_dataframe(file)

        # Create variables to point to the locations of the first assignment and the final mark
        first_assignment = int(df.columns.get_loc("Number"))+1
        final_index = int(df.columns.get_loc("FINAL"))

        # Check whether output directory exists, create it if it does not exist
        validate_output_directory(TXT_DIR, class_path)

        # Iterate through the data in the Pandas dataframe and create subject comments based on specified criteria
        for row in df.itertuples(index=False):
            with open(f"{TXT_DIR}\\{class_path}\\{row.Surname}_{row.Nickname}_{row.Number}.txt", "w") as text_file:
                sname = row.Nickname
                # Check gender of student and assign correct pronouns
                boy_girl = pn_boy_girl(str(row.Sex).upper())
                he_she = pn_he_she(str(row.Sex).upper())
                He_She = pn_He_She(str(row.Sex).upper())
                him_her = pn_him_her(str(row.Sex).upper())
                his_her = pn_his_her(str(row.Sex).upper())
                His_Her = pn_His_Her(str(row.Sex).upper())

                gen_eng_fal(row.FINAL, text_file, sname, he_she, He_She, him_her, his_her, His_Her, boy_girl)


# Helper Functions
# TODO: Break script into manageable helper functions
# TODO:  Create function to parse Excel filename to determine subject

# Several functions to output pronouns based on gender marked in spreadsheet
def pn_boy_girl(gender_p):
    return "boy" if gender_p == 'M' else "girl"


def pn_he_she(gender_p):
    return "he" if gender_p == 'M' else "she"


def pn_He_She(gender_p):
    return "He" if gender_p == 'M' else "She"


def pn_him_her(gender_p):
    return "him" if gender_p == 'M' else "her"


def pn_his_her(gender_p):
    return "his" if gender_p == 'M' else "her"


def pn_His_Her(gender_p):
    return "His" if gender_p == 'M' else "Her"


# Read CSV file into a dataframe, top row is the header, encoding is used because of symbols
# such as ô, é, and ê.
def csv_to_dataframe(csv_file_p):
    df = pd.read_csv(csv_file_p, header=0, encoding="ISO-8859-1")
    return df


# Validate the existence of the output folders, if non-existent, create them
def validate_output_directory(txt_dir_p, class_path_p):
    if not os.path.exists(f"{txt_dir_p}\\{class_path_p}"):
        os.mkdir(f"{txt_dir_p}\\{class_path_p}")
        print(f"Created directory: {txt_dir_p}\\{class_path_p}")


# Reads the final mark of the student and writes general subject comments
# to a text file depending on the mark achieved.
def gen_eng_fal(f_mark_p, txt_f_p, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p):
    if str(f_mark_p) == "A":
        txt_f_p.write("!!!NO FINAL MARK!!! - ")
    elif float(f_mark_p) < .4:
        txt_f_p.write(rand_line(FAIL_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .5:
        txt_f_p.write(rand_line(CARE_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .6:
        txt_f_p.write(rand_line(SATIS_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .8:
        txt_f_p.write(rand_line(GOOD_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    else:
        txt_f_p.write(rand_line(EXCEL_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))


# Calls a random line from the chosen comment file.
# Formatted variables are defined for interaction within text file
def rand_line(f_name, s_name_p, he_she_p, He_She_p, his_her_p, His_Her_p, him_her_p, boy_girl_p, ass_name_p=""):
    with open(f_name) as in_file:
        lines = in_file.read().splitlines()
        return random.choice(lines).format(sname=s_name_p,
                                           he_she=he_she_p,
                                           He_She=He_She_p,
                                           his_her=his_her_p,
                                           His_Her=His_Her_p,
                                           him_her=him_her_p,
                                           boy_girl=boy_girl_p,
                                           ass_name=ass_name_p)


#         # Create two lists from the CSV files
#         csv_reader = csv.reader(csv_file)
#         fields = csv_reader.__next__()  # isolates fields from the rest of the data
#         data_list = list(csv_reader)  # Create list of CSV file
#         # The number index is important - it is the last field before assignments are listed
#         # Use this index to determine the indexes of all other assignments
#         number_index = fields.index("Number")
#         first_assessment = fields.index("Number") + 1
#         final_index = fields.index("FINAL")
#
#         # General performance comments
#         for row in data_list:
#             with open(txt_dir + f"\\{class_path}" + f"\\{row[1]}_{row[2]}_{row[number_index]}.txt", "w") as text_file:
#                 student_name = row[2]
#                 if str(row[-1]) == "A":
#                     text_file.write("!!!NO FINAL MARK!!! - ")
#                 elif float(row[-1]) < .4:
#                     text_file.write(random_line(fail_file))
#                 elif float(row[-1]) < .5:
#                     text_file.write(random_line(careful_file))
#                 elif float(row[-1]) < .6:
#                     text_file.write(random_line(satisfactory_file))
#                 elif float(row[-1]) < .8:
#                     text_file.write(random_line(good_file))
#                 else:
#                     text_file.write(random_line(excellent_file))
#
#         # Failed assignment comments
#         student_count = 0
#         while student_count < len(data_list):
#             single_student = (data_list[student_count])
#             assignment_count = first_assessment
#             while assignment_count < final_index:
#                 assignment_name = fields[assignment_count]
#                 student_name = single_student[2]
#                 He_She = "He" if str(single_student[3]).upper() == "M" else "She"
#                 he_she = "he" if str(single_student[3]).upper() == "M" else "she"
#                 him_her = "him" if str(single_student[3]).upper() == "M" else "her"
#                 his_her = "his" if str(single_student[3]).upper() == "M" else "her"
#                 His_Her = "His" if str(single_student[3]).upper() == "M" else "Her"
#                 if str(single_student[assignment_count]) == "A":
#                     pass
#                 elif float(single_student[assignment_count]) < .4:
#                     with open(txt_dir + f"\\{class_path}" + f"\\{single_student[1]}_{single_student[2]}_"
#                                                             f"{single_student[number_index]}.txt", 'a+') as text_file:
#                         text_file.write(random_line(assessment_file))
#                 assignment_count += 1
#             student_count += 1
#
#         # Figure out how to let the functions work - later
#         # category_comment(4, pleasure_file)
#         # category_comment(5, attention_file)
#         # category_comment(6, disrupt_file)
#         # category_comment(7, reading_file)
#
#         # Other observation comments
#         student_count = 0
#         while student_count < len(data_list):
#             single_student = (data_list[student_count])
#             student_name = single_student[2]
#             He_She = "He" if str(single_student[3]).upper() == "M" else "She"
#             he_she = "he" if str(single_student[3]).upper() == "M" else "she"
#             him_her = "him" if str(single_student[3]).upper() == "M" else "her"
#             his_her = "his" if str(single_student[3]).upper() == "M" else "her"
#             His_Her = "His" if str(single_student[3]).upper() == "M" else "Her"
#             boy_girl = "boy" if str(single_student[3]).upper() == "M" else "girl"
#             if str(single_student[4]).upper() == "X":
#                 with open(txt_dir + f"\\{class_path}" + f"\\{single_student[1]}_{single_student[2]}_"
#                                                         f"{single_student[number_index]}.txt", 'a+') as text_file:
#                     text_file.write(random_line(pleasure_file))
#             student_count += 1
#
#             student_count = 0
#             while student_count < len(data_list):
#                 single_student = (data_list[student_count])
#                 student_name = single_student[2]
#                 He_She = "He" if str(single_student[3]).upper() == "M" else "She"
#                 he_she = "he" if str(single_student[3]).upper() == "M" else "she"
#                 him_her = "him" if str(single_student[3]).upper() == "M" else "her"
#                 his_her = "his" if str(single_student[3]).upper() == "M" else "her"
#                 His_Her = "His" if str(single_student[3]).upper() == "M" else "Her"
#                 boy_girl = "boy" if str(single_student[3]).upper() == "M" else "girl"
#                 if str(single_student[5]).upper() == "X":
#                     with open(txt_dir + f"\\{class_path}" + f"\\{single_student[1]}_{single_student[2]}_"
#                                                             f"{single_student[number_index]}.txt", 'a+') as text_file:
#                         text_file.write(random_line(attention_file))
#                 student_count += 1
#
#             student_count = 0
#             while student_count < len(data_list):
#                 single_student = (data_list[student_count])
#                 student_name = single_student[2]
#                 He_She = "He" if str(single_student[3]).upper() == "M" else "She"
#                 he_she = "he" if str(single_student[3]).upper() == "M" else "she"
#                 him_her = "him" if str(single_student[3]).upper() == "M" else "her"
#                 his_her = "his" if str(single_student[3]).upper() == "M" else "her"
#                 His_Her = "His" if str(single_student[3]).upper() == "M" else "Her"
#                 boy_girl = "boy" if str(single_student[3]).upper() == "M" else "girl"
#                 if str(single_student[6]).upper() == "X":
#                     with open(txt_dir + f"\\{class_path}" + f"\\{single_student[1]}_{single_student[2]}_"
#                                                             f"{single_student[number_index]}.txt", 'a+') as text_file:
#                         text_file.write(random_line(disrupt_file))
#                 student_count += 1
#
#             student_count = 0
#             while student_count < len(data_list):
#                 single_student = (data_list[student_count])
#                 student_name = single_student[2]
#                 He_She = "He" if str(single_student[3]).upper() == "M" else "She"
#                 he_she = "he" if str(single_student[3]).upper() == "M" else "she"
#                 him_her = "him" if str(single_student[3]).upper() == "M" else "her"
#                 his_her = "his" if str(single_student[3]).upper() == "M" else "her"
#                 His_Her = "His" if str(single_student[3]).upper() == "M" else "Her"
#                 boy_girl = "boy" if str(single_student[3]).upper() == "M" else "girl"
#                 if str(single_student[7]).upper() == "X":
#                     with open(txt_dir + f"\\{class_path}" + f"\\{single_student[1]}_{single_student[2]}_"
#                                                             f"{single_student[number_index]}.txt", 'a+') as text_file:
#                         text_file.write(random_line(reading_file))
#                 student_count += 1
#
# # Write outputs to an excel file and delete the intermediate TXT data
# subfolder_name = [f.name for f in os.scandir(txt_dir) if f.is_dir()]
# subfolder_path = [f.path for f in os.scandir(txt_dir) if f.is_dir()]
#
# sub_index = 0
# while sub_index < len(subfolder_name):
#     row = 0
#     col = 0
#     workbook = xlsxwriter.Workbook(subfolder_path[sub_index] + f"\\{subfolder_name[sub_index]}.xlsx")
#     worksheet = workbook.add_worksheet()
#     worksheet.set_column("A:A", 40)
#     worksheet.set_column("B:B", 200)
#     for file in Path(subfolder_path[sub_index]).glob("*.txt"):
#         with open(file, encoding="ISO-8859-1", mode="r") as txt_file:
#             worksheet.write(row, col, file.name[:-4])
#             worksheet.write(row, col + 1, file.read_text())
#             row += 1
#         os.remove(file)
#     workbook.close()
#     sub_index += 1

# Run main program
if __name__ == "__main__":
    main()
