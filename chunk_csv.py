import pandas as pd
import sys
import os

def split_csv_chunks(df, chunk_size, filename_prefix="chunk"):
  num_chunks = len(df) // chunk_size + 1  # Integer division with ceiling
  for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, len(df))
    chunk_df = df.iloc[start_idx:end_idx]
    filename = f"{filename_prefix}_{i + 1}.csv"
    try:
      os.mkdir(f'{filename_prefix}_chunks')
    except:
       pass
    chunk_df.to_csv(f'{filename_prefix}_chunks/{filename}', index=False)  # Save chunk to separate CSV

if __name__ == "__main__":
  try:
    name_of_script = sys.argv[0]
    csv_file_path = sys.argv[1]
    chunk_size = int(sys.argv[2])
    name = csv_file_path.split('.')[0]

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path, dtype=object)
    split_csv_chunks(df, chunk_size, name)  
  except FileNotFoundError:
    print('Cannot find the file, make sure it is spelled correctly.')
  except IndexError:
    print('Run like so: python chunk_csv.py csvFile_1.csv chunkSizeInNumbers')
  except UnicodeDecodeError: 
    print('Please open the file with Notepad and save it again to another name')
