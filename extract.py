#!/usr/bin/env python3
'''
Description: Calculates daily vol over different fixes and plots them
Author: Eric Archerman
Date: 17 July 2024
'''
import pandas as pd

LOC = 'data/running-2-years.csv'

def format(loc):
    hf_data = pd.read_csv(loc)
    hf_data['timestamp'] = hf_data['timestamp'] + 28800000
    hf_data['timestamp'] = pd.to_datetime(hf_data['timestamp'], unit='ms')
    
    return hf_data

def extract_hourly_prices(hf_data):
    print(hf_data.iloc[-1])
    hf_data.set_index('timestamp', inplace=True)
    
    print('Resampling every hour')
    resampled_data = hf_data.resample('h').first()
    
    print('Pivoting data')
    pivot_data = resampled_data.pivot_table(index=resampled_data.index.date, 
                                            columns=resampled_data.index.time, 
                                            values='indexPrice')
    
    pivot_data.columns = [time.strftime('%I%p').lower() for time in pivot_data.columns]
    
    return pivot_data

def main():
    print("************************************************************ Extracting and formatting data ************************************************************")
    hf_data = format(LOC)
    pivot_data = extract_hourly_prices(hf_data)
    pivot_data = pivot_data.iloc[-2:] # to make compatible with Tim's excel

    print(f"************************************************************ Writing to {LOC} ************************************************************")
    pivot_data.to_csv('extracted_prices.csv')
    print("Extracted data write successful.")

if __name__ == '__main__':
    main()
    print("************************************************************ program done! ************************************************************")