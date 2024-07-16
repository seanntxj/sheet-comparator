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
from enum import Enum

class NATURE_OF_ISSUES(Enum): 
    OK = "No issues found."
    DISCREPENCY = "Discrepencies found, please check the issue log."
    FIELDS_MISMATCH = "Columns fields don't match, please check the issue log."
    FIELDS_LENGTH_MISMATCH = "The number of columns in each csv file don't match. Please check for any trailing commas with notepad."
    
class ISSUE_ITEM:
    def __init__(self, original_row: list, uploaded_row: list, mismatched_columns_indexes: list) -> None:
        self.original_row = original_row
        self.uploaded_row = uploaded_row
        self.mismatched_columns_indexes = mismatched_columns_indexes
    
class ISSUES_MAIN:
    def __init__(self, status: NATURE_OF_ISSUES = NATURE_OF_ISSUES.OK, issue_list: list[ISSUE_ITEM] = []) -> None:
        self.status = status
        self.issue_list = issue_list
        
    def insert_issue_missing_uploaded_row(self, original_row: list, value_of_identifier: str, column_of_identifier: int = 0):
        row_to_indicate_missing_row = []
        for i in range(len(original_row)):
            if i != column_of_identifier:
                row_to_indicate_missing_row.append('MISSING')
            else: 
                row_to_indicate_missing_row.append(value_of_identifier)
        issue_item = ISSUE_ITEM(original_row, row_to_indicate_missing_row, [column_of_identifier])
        self.issue_list.append(issue_item)
        return issue_item

    def insert_issue(self, original_row: list, uploaded_row: list, columns_where_discrepency_is_found: list):
        issue_item = ISSUE_ITEM(original_row, uploaded_row, columns_where_discrepency_is_found)
        self.issue_list.append(issue_item)
        return issue_item

    
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

def find_discrepencies(uploaded_file_path: str, original_file_path: str, progress_to_show_in_gui = None, identifiying_field_index: int = 0) -> ISSUES_MAIN:
    """
    Finds the difference between two CSV files. 

    Args: 
        uploaded_file_path: The path that points to the CSV file which should match the original. 
        original_file_path: The path that points to the CSV file which is meant to be compared against (or in other words, this CSV file is the source of truth).
        progress_to_show_in_gui: A function from the GUI Python file which accepts the current percentage progress of the script as an integer.

    Returns: 
        A list containing strings of the discrepencies found.
    """

    # Read uploaded csv file
    f_uploaded = open(uploaded_file_path, 'r')
    uploaded_csv_reader = csv.reader(f_uploaded)

    # Field names 
    fields_uploaded_csv = next(uploaded_csv_reader)

    # Read original csv file
    f_ori = open(original_file_path, 'r')
    ori_csv_reader = csv.reader(f_ori)
    
    # Field names 
    fields_ori_csv = next(ori_csv_reader)

    # Initialise issues custom class to hold all the found issues (if any)
    issues = ISSUES_MAIN()

    # Checking if every field in the original csv exists in the uploaded csv - If failed will not proceed with rest of check, return issue log immediately
    mismatched_fields = []
    for i in range(len(fields_ori_csv)):
        if fields_ori_csv[i] not in fields_uploaded_csv:
            issues.status = NATURE_OF_ISSUES.FIELDS_MISMATCH
            mismatched_fields.append(i)
    if issues.status == NATURE_OF_ISSUES.FIELDS_MISMATCH: 
        issues.insert_issue(fields_ori_csv, fields_uploaded_csv, mismatched_fields)
        return issues
    if len(fields_ori_csv) != len(fields_uploaded_csv): 
        issues.status = NATURE_OF_ISSUES.FIELDS_LENGTH_MISMATCH
        return issues

    # Hash the uploaded csv file based on its key value
    uploaded_hashed_csv = {}
    for row in uploaded_csv_reader:
        uploaded_hashed_csv[row[identifiying_field_index]] = row

    # Close the uploaded csv file, it's no longer needed as its now been hashed into memory
    f_uploaded.close()

    # For each row in the original csv file
    # Check if it exists in the uploaded csv file
    # If it exists, compare that row of values to the original 
    previous_update = 0 # For GUI 
    with tqdm(total=len(uploaded_hashed_csv), desc="Comparing rows") as pbar:
        for row_num, row_from_ori_csv in enumerate( ori_csv_reader ):
            if row_from_ori_csv[identifiying_field_index] not in uploaded_hashed_csv:
                issues.insert_issue_missing_uploaded_row(row_from_ori_csv, row_from_ori_csv[identifiying_field_index], identifiying_field_index)
                continue

            row_from_uploaded_csv = uploaded_hashed_csv[row_from_ori_csv[identifiying_field_index]]

            mismatched_fields = []
            for col_num in range(len(row_from_ori_csv)):
                if row_from_uploaded_csv[col_num] != row_from_ori_csv[col_num]:
                    mismatched_fields.append(col_num)
            if len(mismatched_fields) > 0: 
                issues.insert_issue(row_from_ori_csv,row_from_uploaded_csv,mismatched_fields)
            
            # GUI and TQDM progress bars
            pbar.update(1)
            progress_in_percentage = min( int(row_num / len(uploaded_hashed_csv)*100) + 1, 100)
            if progress_to_show_in_gui != None and previous_update != progress_in_percentage:
                progress_to_show_in_gui(progress_in_percentage)
                previous_update = progress_in_percentage

    # Close the original csv file, we've read through everything 
    f_ori.close()

    # Write the issues into an excel file and return the issue log
    if len(issues.issue_list) == 0: 
        issues.status = NATURE_OF_ISSUES.OK
    else: 
        issues.status = NATURE_OF_ISSUES.DISCREPENCY
    return issues

def write_issues(issue_list: list):
    f = open('issues.txt', 'w')
    f.write('\n'.join(issue_list) + '\n')
    f.close()

def load_mapping_uploaded_to_original():
    f = open('mapping.csv', 'r')
    mapping_csv_reader = csv.reader(f)
    fields = next(mapping_csv_reader)
    mapping = {}
    for _, row in enumerate(mapping_csv_reader):
        original, uploaded = row[0], row[1]
        mapping[original] = uploaded
        mapping[uploaded] = original
    return mapping

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

    issues = find_discrepencies(uploaded_file_name, ori_file_name)
    print(issues.status.value)

    f = open(f'issues_{time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())}.txt', 'a+')
    for item in issues.issue_list:
        f.write(f'ORI | {item.original_row}\n')
        f.write(f'UPL | {item.uploaded_row}\n')
        f.write(f'{item.mismatched_columns_indexes}\n')
        f.write(f'\n')
    f.close()