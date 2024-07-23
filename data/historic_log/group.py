import os
import pandas as pd

LOC = 'data/historic_log/'

HF_FILES = [
    '22-7-12.csv',
    '23-1-7.csv',
    '23-7-12.csv',
    '24-1-7.csv',
]

DESTINATION ='data/running-2-years.csv'

def format(loc, hf_files):
    try:
        hf_data_sep = []
        for file in hf_files:
            file_path = os.path.join(loc, file)
            print(f"Reading file: {file_path}")
            df = pd.read_csv(file_path)
            hf_data_sep.append(df)
    except Exception as e:
        print(f"An error occured: {e}")
        exit()
    
    hf_data = pd.concat(hf_data_sep, ignore_index=True)
    return hf_data

def main():
    hf_data = format(LOC, HF_FILES)

    print(f'writing to ... *-*-*-*-> {DESTINATION} <-*-*-*-* ...')
    hf_data.to_csv(DESTINATION, index=False)

if __name__ == '__main__':
    main()
    print('program done!')