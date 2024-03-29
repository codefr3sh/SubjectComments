"""
Created by:    Philip van Schalkwyk
Contact:       philiplvans@gmail.com
Last updated:  2022-03-10

This script is used to automatically generate subject comments for English, based on:
    - Task Scores
    - Final quarter mark
    - Misc. comments such as additional reading required, or being a pleasure in class

A Pandas dataframe is created from a CSV file to generate the comments.
Output is written to an XLS file.
Templates will be created to display how the CSV file used as input is supposed to look.

Further enhancements can make provision for other subjects, this can just be added to the check_sub function and
a {subject} keyword can be added to the comment field.

Additional enhancements include:    - GUI

"""
import pandas as pd
import random
from pathlib import Path
import os
import xlsxwriter
import yagmail
import shutil
from creds import *  # Used for mail address and password


# Variables for all the different files and folders that will be used to read and write data
# Set the current working directory to the folder in which the file is contained
CWD = os.path.join(os.getcwd(), "DATA")
CSV_DIR = os.path.join(CWD, "CSV_FILES")
OUT_DIR = os.path.join(CWD, "OUTPUT")
COMMENT_DIR = os.path.join(CWD, "COMMENT_SOURCE")
ARCHIVE_DIR = os.path.join(CWD, "ARCHIVE")
CSV_ARCHIVE_DIR = os.path.join(CSV_DIR, "ARCHIVE")

# File Variables
FAIL_F = os.path.join(COMMENT_DIR, "1_fail.txt")
CARE_F = os.path.join(COMMENT_DIR, "2_careful.txt")
SATIS_F = os.path.join(COMMENT_DIR, "3_satisfactory.txt")
GOOD_F = os.path.join(COMMENT_DIR, "4_good.txt")
EXCEL_F = os.path.join(COMMENT_DIR, "5_excellent.txt")
ASS_F = os.path.join(COMMENT_DIR, "6_assessmentfail.txt")
PLEASURE_F = os.path.join(COMMENT_DIR, "7_pleasure.txt")
ATT_F = os.path.join(COMMENT_DIR, "8_attention.txt")
DISRUPT_F = os.path.join(COMMENT_DIR, "9_disrupt.txt")
READ_F = os.path.join(COMMENT_DIR, "10_read.txt")

# Mail Attachment List
ATTACH_LIST = []


# Main function
# TODO: Investigate proper variable name best practices and refactor code

def main():
    # Iterate through CSV files in input directory
    for file in Path(CSV_DIR).glob("*.csv"):
        class_path = file.name[:-4]
        df = csv_to_dataframe(file)

        # Create variables to point to the locations of the first assignment and the final mark
        f_task = int(df.columns.get_loc("Number")) + 1
        f_index = int(df.columns.get_loc("FINAL"))

        # Check whether output directory exists, create it if it does not exist
        validate_output_directory(OUT_DIR, class_path)

        # Iterate through the data in the Pandas dataframe and create subject comments based on specified criteria
        for row in df.itertuples(index=False):
            txt_file_s = txt_file_string(OUT_DIR, class_path, row.Surname, row.Nickname, row.Number)
            with open(txt_file_s, 'a+') as txt_f:
                sname = row.Nickname
                # Check gender of student and assign correct pronouns
                boy_girl = pn_boy_girl(str(row.Sex).upper())
                he_she = pn_he_she(str(row.Sex).upper())
                He_She = pn_He_She(str(row.Sex).upper())
                him_her = pn_him_her(str(row.Sex).upper())
                his_her = pn_his_her(str(row.Sex).upper())
                His_Her = pn_His_Her(str(row.Sex).upper())

                # Check if ENG is in the filename, if it is, continue to check for FAL and HL
                # This leaves room to check for other subjects as well in the future
                check_sub(class_path, row, txt_f, sname, he_she, He_She, him_her, his_her, His_Her, boy_girl)

                # Create comments for failed assignments
                fail_task(f_task, f_index, df, row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl)

                # Functions for other general comments, e.g.
                # Pleasure in class, read more, disruptive, need to pay more attention
                pleas_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl)
                atten_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl)
                disrupt_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl)
                read_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl)

    # Write outputs to an excel file and delete the intermediate TXT data
    subfolder_name = [f.name for f in os.scandir(OUT_DIR) if f.is_dir()]
    subfolder_path = [f.path for f in os.scandir(OUT_DIR) if f.is_dir()]
    txt_to_xls(subfolder_name, subfolder_path)

    # Create list of attachments to send and send the mail
    attachment_list()
    send_mail()

    # Move contents of Comment Output and CSV to an Archive Folder
    move_to_archive()
    csv_to_archive()


# Helper Functions
# Function to create text file string
def txt_file_string(txt_dir_p, class_path_p, surname_p, nickname_p, number_p):
    return str(f"{txt_dir_p}/{class_path_p}/{surname_p}_{nickname_p}_{number_p}.txt")


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
    if not os.path.exists(f"{txt_dir_p}/{class_path_p}"):
        os.mkdir(f"{txt_dir_p}/{class_path_p}")


# Reads the final mark of the student and writes general subject comments
# to a text file depending on the mark achieved.
# Two separate functions, one for home language, one for additional language with different criteria
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


def gen_eng_hl(f_mark_p, txt_f_p, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p):
    if str(f_mark_p) == "A":
        txt_f_p.write("!!!NO FINAL MARK!!! - ")
    elif float(f_mark_p) < .5:
        txt_f_p.write(rand_line(FAIL_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .55:
        txt_f_p.write(rand_line(CARE_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .6:
        txt_f_p.write(rand_line(SATIS_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    elif float(f_mark_p) < .8:
        txt_f_p.write(rand_line(GOOD_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))
    else:
        txt_f_p.write(rand_line(EXCEL_F, sname_p, he_she_p, He_She_p, him_her_p, his_her_p, His_Her_p, boy_girl_p))


# Function to determine the subject, and if it is a language subject, whether it is Home Language or Additional Language
def check_sub(class_path, row, txt_f, sname, he_she, He_She, him_her, his_her, His_Her, boy_girl):
    if "ENG" in class_path.upper():
        if "FAL" in class_path.upper():
            gen_eng_fal(row.FINAL, txt_f, sname, he_she, He_She, him_her, his_her, His_Her, boy_girl)
        elif "HL" in class_path.upper():
            gen_eng_hl(row.FINAL, txt_f, sname, he_she, He_She, him_her, his_her, His_Her, boy_girl)


# Function to determine whether student failed a task, writes output to file
def fail_task(f_task, f_index, df, row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl):
    assignment_count = f_task
    while assignment_count < f_index:
        ass_name = str(df.columns[assignment_count])
        if str(row[assignment_count]) == "A":
            pass
        elif float(row[assignment_count]) < .4:
            txt_f.write(rand_line(ASS_F, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl, ass_name))
        assignment_count += 1


# Functions for other general comments.
# More functions can be added later if it is required
def pleas_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl):
    if str(row.Pleasure).upper() == "X":
        txt_f.write(rand_line(PLEASURE_F, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl))


def atten_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl):
    if str(row.Attention).upper() == "X":
        txt_f.write(rand_line(ATT_F, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl))


def disrupt_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl):
    if str(row.Disruption).upper() == "X":
        txt_f.write(rand_line(DISRUPT_F, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl))


def read_com(row, txt_f, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl):
    if str(row.Read).upper() == "X":
        txt_f.write(rand_line(READ_F, sname, he_she, He_She, his_her, His_Her, him_her, boy_girl))


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


# Function to write output to XLSX file and remove TXT files
def txt_to_xls(subname, subpath):
    sub_index = 0
    while sub_index < len(subname):
        row = 0
        col = 0
        workbook = xlsxwriter.Workbook(f"{subpath[sub_index]}/{subname[sub_index]}.xlsx")
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:A", 40)
        worksheet.set_column("B:B", 200)
        for file in Path(subpath[sub_index]).glob("*.txt"):
            with open(file, encoding="ISO-8859-1", mode="r") as txt_file:
                worksheet.write(row, col, file.name[:-4])
                worksheet.write(row, col + 1, file.read_text())
                row += 1
            os.remove(file)
        workbook.close()
        sub_index += 1


# Function to create list of attachments to mail
def attachment_list():
    for root, dirs, files in os.walk(OUT_DIR):
        for file in files:
            if file.endswith(".xlsx"):
                ATTACH_LIST.append(os.path.join(root, file))


# Function to send the email to the end-user
def send_mail():
    try:
        # initializing the server connection
        yag = yagmail.SMTP(user=s_mail, password=password)
        # sending the email
        yag.send(to=r_mail,
                 subject=subject,
                 contents=mail_body,
                 attachments=ATTACH_LIST)
        print("Email sent successfully")
    except:
        print("Error, email was not sent")


# Function to return a list of all subfolders in comment_output folder
def fast_scandir(dirname):
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


# Function to move Comment XLS files to an archive folder after the mail was sent
def move_to_archive():
    dir_list = fast_scandir(OUT_DIR)
    for d in dir_list:
        shutil.move(d, ARCHIVE_DIR)


# Move input CSV files to an Archive folder
def csv_to_archive():
    for file in Path(CSV_DIR).glob("*.csv"):
        shutil.move(file, CSV_ARCHIVE_DIR)


# Run main program
if __name__ == "__main__":
    main()
