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
    for dataframe in dataframes:
        print(dataframe.filename)

    # Using the primary dataframe, start to merge with the others 
    # Return the merged dataframe
    master_df = merge_dfs(df1=primary_dataframe.df, df2=dataframes[2].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[0].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[1].df, df1_identifier_column='Address', df2_identifier_column='Address number')
    master_df = merge_dfs(df1=master_df, df2=dataframes[3].df, df1_identifier_column='Customer', df2_identifier_column='Customer')
    
    master_df.to_excel('result.xlsx', index=False)
    pass