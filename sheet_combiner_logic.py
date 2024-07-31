import pandas as pd
import Levenshtein
import os
from enum import Enum

class DataframePlus:
    def __init__(self, df: pd.DataFrame, file_path: str):
        self.df = df
        self.filename = os.path.basename(file_path)

def merge_dfs(df1: pd.DataFrame, df2: pd.DataFrame, df1_identifier_column: str, df2_identifier_column: str) -> pd.DataFrame:
    '''
    Merge two Pandas Dataframes
    Keep all rows from the first dataframe, only keep the first dataframe's copy of a column which appears in both dataframes.
    If the identifier column of both dataframes are different, only the first dataframe's copy is kept.
    '''
    # Rename the identifier column of the second dataframe to be the same of the first. Avoids having both columns kept in the merged dataframe.
    df2 = df2.rename(columns={df2_identifier_column: df1_identifier_column}) 
    # Left merge the two dataframes. Suffix the second dataframe's identifier column in case.
    resulting_df = pd.merge(df1, df2, how='left', left_on=df1_identifier_column, right_on=df1_identifier_column, suffixes=('', '_removeMe')) 
    return resulting_df

def find_nearest_string(target: str, list_of_strings: list[str]) -> str:
    """
    Finds the closest string in a list of strings with a combination of the Levenshtein distance and string size consistency.
    Closest string to the target is the least number of substitutions in a potential string INCLUDING removal of characters.
    """

    # Check for exact match first
    list_of_strings = [item.lower() for item in list_of_strings]
    target = target.lower()
    if target in list_of_strings:
        return target

    max_len_of_str = max(len(item) for item in list_of_strings)

    score = []
    for potential_target in list_of_strings:
        size_matched_potential_target = f"{potential_target}{(max_len_of_str - len(potential_target)) * '~'}"  # Append string to be the same size as the max sized potential match
        similarity = Levenshtein.distance(size_matched_potential_target, target)
        score.append((similarity, potential_target))

    # Find the index of the minimum score
    min_index = min(range(len(score)), key=lambda i: score[i][0])

    # If there are multiple strings with the same minimum score, choose the one closer in length to the target
    min_score = score[min_index][0]
    candidates = [string for similarity, string in score if similarity == min_score]
    closest_length = min(abs(len(target) - len(string)) for string in candidates)
    best_match = next(string for string in candidates if abs(len(target) - len(string)) == closest_length)

    return best_match

def get_folder_contents(folder_path: str, types: list[str]) -> list[str]:
    types = [type.lower() for type in types]
    return [os.path.join(folder_path, item) for item in os.listdir(folder_path) if item.split('.')[-1].lower() in types]

def get_dataframes(file_paths: list[str], infer_types: bool = False) -> list[DataframePlus]:
    def get_reader(file_path):
        _, ext = os.path.splitext(file_path)
        return pd.read_csv if ext == '.csv' else pd.read_excel
    dtype = None if infer_types else object
    return [DataframePlus(get_reader(file_path)(file_path, dtype=dtype), file_path) for file_path in file_paths]

def pop_primary_dataframe(name: str, dataframes: list[DataframePlus]) -> DataframePlus:
    for i, dataframe in enumerate(dataframes):
        if name.lower() == dataframe.filename.lower(): 
            return dataframes.pop(i)
         
if __name__ == "__main__": 
    # Load all dataframes into memory 
    dataframes = get_dataframes(get_folder_contents('test_data/unmerged', ['csv', 'xlsx']))
    # Establish which dataframe is the primary
    primary_dataframe = pop_primary_dataframe('spte-kna1.xlsx', dataframes=dataframes)
    # Establish which dataframes have what columns
    # for dataframe in dataframes:
    #     print(dataframe.filename)

    # Using the primary dataframe, start to merge with the others 
    # Return the merged dataframe
    master_df = merge_dfs(df1=primary_dataframe.df, df2=dataframes[4].df, df1_identifier_column='Customer', df2_identifier_column='Customer')
    master_df = merge_dfs(df1=master_df, df2=dataframes[2].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[0].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[1].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[3].df, df1_identifier_column='Customer', df2_identifier_column='Customer')
    
    # Rename the columns
    final_columns = ["Customer","Company Code","Buyer’s Name 1","Buyer's Name 2","Buyer's Name 3","Buyer's Name 4","Buyer’s TIN","Tax Number 1","Tax Number 2","Buyer’s SST Registration Number ( Sales Tax)","Buyer’s SST Registration Number (Service Tax)","Buyer's ID Number- Registration / Identification Number / Passport Number2","Search Term 2","Buyer's E-mail","Buyer’s Address - Address Line 1","Buyer’s Address - Address Line 2","Buyer’s Address - Address Line 3","Buyer’s Address - Address Line 4","Buyer’s Address - Address Line 5","Buyer’s Address - Postal Zone","Buyer’s Address - City Name","Buyer’s Address - State","Buyer’s Address - Country","Buyer’s Contact Number"]
    column_mapping = {
        "Customer": "Customer",
        "Company Code": "Company Code",
        "Buyer’s Name 1": "Name",
        "Buyer's Name 2": "Name 2",
        "Buyer's Name 3": "Name 3",
        "Buyer's Name 4": "Name 4",
        "Buyer’s TIN": "Tax Identification Number",  
        "Tax Number 1": "Tax Number 1",
        "Tax Number 2": "Tax Number 2",
        "Buyer’s SST Registration Number ( Sales Tax)": "Tax Number 3",  
        "Buyer’s SST Registration Number (Service Tax)": "Tax Number 4",  
        "Buyer's ID Number- Registration / Identification Number / Passport Number2": "Tax Number 5",  
        "Search Term 2": "Search Term 2",
        "Buyer’s Address - Address Line 1": "Street",
        "Buyer’s Address - Address Line 2": "Street 2",
        "Buyer’s Address - Address Line 3": "Street 3",
        "Buyer’s Address - Address Line 4": "Street 4",
        "Buyer’s Address - Address Line 5": "Street 5",
        "Buyer’s Address - Postal Zone": "Postal Code",
        "Buyer’s Address - City Name": "City",
        "Buyer’s Address - State": "Region",  
        "Buyer’s Address - Country": "Country",
        "Buyer’s Contact Number": "Telephone number"
    }

    # Rename
    for column in column_mapping:
        master_df = master_df.rename(columns={column_mapping[column]: column})
    # Remove any not used columns 
    for column in list(master_df.columns):
        if column not in final_columns: 
            master_df = master_df.drop(column, axis=1)
    # Order columns correctly 
    master_df = master_df.reindex(columns=final_columns)
    # Output
    master_df.to_excel('result.xlsx', index=False)