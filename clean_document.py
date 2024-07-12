import pandas as pd
import sys
import os
from tqdm import tqdm  # Import tqdm for progress bar

date_types = ['calendar', 'date', 'month', 'day', 'year']

def find_containing_strings(array1, array2):
  """
  This function finds strings in array2 that contain any string in array1 (case-insensitive).

  Args:
      array1: A list of strings to search for (converted to lowercase).
      array2: A list of strings to search within.

  Returns:
      A list of strings from array2 that contain any string in array1 (case-insensitive).
  """

  # Convert array1 elements to lowercase for case-insensitive search
  lowercase_array1 = [string.lower() for string in array1]

  # Use list comprehension for concise filtering
  return [string for string in array2 if any(substring.lower() in string.lower() for substring in lowercase_array1)]

def clean(df): 
    # Replace all occurrences of "#VALUE" with empty strings
    df.replace("#VALUE!", "", inplace=True)

    # Replace all occurrences of "#VALUE" with empty strings
    df.replace("0:00:00", "", inplace=True)

    for date_column in find_containing_strings(date_types, list(df.columns.values)):
        df[date_column] = df[date_column].astype(str).str.replace(r'\.0$', '', regex=True)
        df[date_column] = df[date_column].astype(str).str.replace('.', '')
        df[date_column] = df[date_column].astype(str).str.replace('nan', '')

    return df

if __name__ == "__main__":
    name_of_script = sys.argv[0]

    # Read the CSV file into a pandas DataFrame
    try:
        folder_name = sys.argv[1]
        files_to_clean = os.listdir(folder_name)

        if not os.path.exists(f'{folder_name}_cleaned'):
            os.mkdir(f'{folder_name}_cleaned')

        # Use tqdm for progress bar
        with tqdm(total=len(files_to_clean), desc="Cleaning Files") as pbar:
            for file_name in files_to_clean:
                df = pd.read_csv(f'{folder_name}/{file_name}', dtype=object)
                df = clean(df)
                df.to_csv(f'{folder_name}_cleaned/{file_name}', index=False)
                pbar.update(1)  # Update progress bar for each file

    except FileNotFoundError:
        print('Cannot find the file, make sure it is spelled correctly.')
    except IndexError:
        print('Run like so: python folder')
    except UnicodeDecodeError:
        print('Please open the file with Notepad and save it again to another name')