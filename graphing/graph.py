import matplotlib.pyplot as plt

import pandas as pd

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
    prices = pd.read_csv('extracted_prices.csv')
    plot_hourly_prices(prices.iloc[:,1:])

if __name__ == "__main__":
    main()