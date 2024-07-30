import pandas as pd
import Levenshtein

def merge_dfs(df1, df2, df1_identifier_column, df2_identifier_column):
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

def find_nearest_string(target, list_of_strings):
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

if __name__ == "__main__": 
    # Load all dataframes into memory 
    # Establish which dataframe is the primary
    # Establish which dataframes have what columns
    # Using the primary dataframe, start to merge with the others 
    # Return the merged dataframe
    pass