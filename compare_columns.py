import csv 
import sys

def find_missing_columns( first_csv, second_csv ):
    first_csv = csv.reader(open(first_csv, 'r'))
    second_csv = csv.reader(open(second_csv, 'r'))

    first_csv_columns = next(first_csv)
    second_csv_columns = next(second_csv)

    for index, item in enumerate(first_csv_columns): 

        column_excel = ""
        additional_letter = 0
        while index > 26:
            additional_letter += 1
            column_excel = f'{column_excel}'
            index -= 26
        if additional_letter != 0:
            additional_letter = chr(additional_letter+64)
        else: 
            additional_letter = ''
        column_excel = f'{additional_letter}{chr(index+65)}'

        if item not in second_csv_columns: 
            print(f'{item}, position {column_excel} not found in second csv.\n')

if __name__ == "__main__":
    name_of_script = sys.argv[0]
    try:
        first_csv = sys.argv[1]
        second_csv = sys.argv[2]

        print(f'Please note first one may be a false positive.---------\n\n')        
        find_missing_columns(first_csv, second_csv) 
    except: 
        print('Run like so: python compare_columns.py csvFile_1.csv csvFile_2.csv')
