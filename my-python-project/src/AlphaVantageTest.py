from finanace_server import AlphaVantageAPI

def main():
    symbol = "AAPL"  # You can change this to any valid symbol
    interval = "1min"
    outputsize = "compact"

    try:
        df = AlphaVantageAPI.get_intraday_data(symbol, interval, outputsize)
        print(f"Intraday data for {symbol} ({interval}):")
        print(df.head())
    except Exception as e:
        print(f"Error fetching intraday data: {e}")

if __name__ == "__main__":
    main()