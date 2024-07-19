#!/usr/bin/env python3
'''
Description: Calculates daily vol over different fixes and plots them
Author: Eric Archerman
Date: 17 July 2024
'''
import os
import pandas as pd
import matplotlib.pyplot as plt

LOC = 'BTC_vol_analytics/raw_data/'

HF_FILES = [
    '22-7-12.csv',
    '23-1-7.csv',
    '23-7-12.csv',
    '24-1-7.csv',
    '24-7.csv',
]

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
    hf_data['timestamp'] = pd.to_datetime(hf_data['timestamp'], unit='ms')
    
    return hf_data

def extract_all_hourly_prices(hf_data):
    # Set the timestamp column as the index
    hf_data.set_index('timestamp', inplace=True)
    
    # Resample the data to get the price at each full hour
    resampled_data = hf_data.resample('h').first()
    
    # Pivot the data to have dates as rows and hours as columns
    pivot_data = resampled_data.pivot_table(index=resampled_data.index.date, 
                                            columns=resampled_data.index.time, 
                                            values='indexPrice')
    
    # Rename the columns to have a more readable format
    pivot_data.columns = [time.strftime('%I%p').lower() for time in pivot_data.columns]
    
    return pivot_data

def plot_hourly_prices(pivot_data):
    plt.figure(figsize=(12, 8))

    for hour in pivot_data.columns:
        plt.plot(pivot_data.index, pivot_data[hour], label=hour)

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Hourly Prices')
    plt.legend(title='Hour')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    hf_data = format(LOC, HF_FILES)
    pivot_data = extract_all_hourly_prices(hf_data)
    pivot_data = pivot_data.iloc[-643:] # to make compatible with Tim's excel
    pivot_data.to_csv('extracted_prices.csv')
    # plot_hourly_prices(pivot_data)

if __name__ == '__main__':
    main()