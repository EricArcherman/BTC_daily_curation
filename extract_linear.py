import pandas as pd

LOC = 'data/running-2-years.csv'

def format(loc):
    hf_data = pd.read_csv(loc)
    hf_data['timestamp'] = hf_data['timestamp'] + 28800000
    hf_data['timestamp'] = pd.to_datetime(hf_data['timestamp'], unit='ms')
    
    return hf_data

def extract_hourly_prices(hf_data):
    hf_data.set_index('timestamp', inplace=True)
    
    print('Resampling every hour')
    resampled_data = hf_data.resample('h').first()
    
    print(resampled_data)

    return resampled_data

def main():
    print("************************************************************ Extracting and formatting data ************************************************************")
    hf_data = format(LOC)
    pivot_data = extract_hourly_prices(hf_data)
    rows = 643 * 24
    pivot_data = pivot_data.iloc[-rows:] # get last 3 rows bc that's what Tim wants

    print(f"************************************************************ Writing to {LOC} ************************************************************")
    pivot_data.to_csv('extracted_linear.csv')
    print("Extracted data write successful.")

if __name__ == '__main__':
    main()
    print("************************************************************ program done! ************************************************************")