"""
Takes in two line arguments:
1 - original csv file to be compared against
2 - seconday csv file which should match the first ASIDE from order
Compares both for discrepencies. If any are found they are noted into a file 'issues.txt' with their location in Excel format. 

Assumptions:
- All fields should be the same
- The unique identifier of each row is the first column 
"""
import csv 
import sys
import os.path
from tqdm import tqdm
import time

def number_to_excel_column(n):
  """Converts a number to its corresponding Excel column format.

  Args:
    n: The number to convert.

  Returns:
    The Excel column format as a string.
  """

  column_name = ""
  while n > 0:
    n, remainder = divmod(n - 1, 26)
    column_name = chr(65 + remainder) + column_name
  return column_name

issues = []
def write_issues(issue_list: list):
    f = open('issues.txt', 'w')
    f.write('\n'.join(issue_list) + '\n')
    f.close()

if __name__ == "__main__": 
    # Get input parameters, if not use default name
    try:
        name_of_script = sys.argv[0]
        ori_file_name = sys.argv[1]
        uploaded_file_name = sys.argv[2]
    except: 
        print(f'Using default filenames ori.csv and uploaded.csv\n\n')
        ori_file_name = 'ori.csv'
        uploaded_file_name = 'uploaded.csv'

    # Give error and quit script if files cannot be found
    if not (os.path.isfile(ori_file_name) and os.path.isfile(uploaded_file_name)):
        raise Exception(f'Files {ori_file_name} or {uploaded_file_name} cannot be found. Terminating script.')

    # Read uploaded csv file
    f_uploaded = open(uploaded_file_name, 'r')
    uploaded_csv_reader = csv.reader(f_uploaded)

    # Field names 
    fields_uploaded_csv = next(uploaded_csv_reader)

    # Read original csv file
    f_ori = open(ori_file_name, 'r')
    ori_csv_reader = csv.reader(f_ori)
    
    # Field names 
    fields_ori_csv = next(ori_csv_reader)

    # Checking if every field in the original csv exists in the uploaded csv - If failed will not proceed with rest of check
    for i in range(len(fields_ori_csv)):
        if fields_ori_csv[i] not in fields_uploaded_csv:
            print(f'FIELD {fields_ori_csv[i]} NOT EXIST. TERMINATING SCRIPT.')
            quit()

    # Hash the uploaded csv file based on its key value
    uploaded_hashed_csv = {}
    for row in uploaded_csv_reader:
        uploaded_hashed_csv[row[0]] = row[1:]

    # Close the uploaded csv file, it's no longer needed as its now been hashed into memory
    f_uploaded.close()

    # For each row in the original csv file
    # Check if it exists in the uploaded csv file
    # If it exists, compare that row of values to the original 
    with tqdm(total=len(uploaded_hashed_csv), desc="Comparing rows") as pbar:
        for row_num, row_from_ori_csv in enumerate( ori_csv_reader ):
            if row_from_ori_csv[0] not in uploaded_hashed_csv:
                issues.append(f'{row_from_ori_csv[0]} | NOT EXIST')
                continue

            row_from_uploaded_csv = uploaded_hashed_csv[row_from_ori_csv[0]]
            row_from_ori_csv = row_from_ori_csv[1:]

            for col_num in range(len(row_from_ori_csv)):
                if row_from_uploaded_csv[col_num] != row_from_ori_csv[col_num]:
                    issues.append(f'{number_to_excel_column(col_num)}{row_num} | ORI: {row_from_ori_csv[col_num]} | UPLOADED: {row_from_uploaded_csv[col_num]} ')
            time.sleep(0.005)
            pbar.update(1)

    # Close the original csv file, we've read through everything 
    f_ori.close()

    # Write any issues down into the issues list text file
    if len(issues) > 0:
        write_issues(issues)
        print(f'Discrepencies found, please refer to issues.txt')
    else: 
        print(f'No discrepencies found!')