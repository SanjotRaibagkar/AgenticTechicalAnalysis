import logging
from kiteconnect import KiteConnect
import pandas as pd


apiKey = ""
apiSecret =""
requestToken =""
accessToken = ""
kiteBaseUrl = "https://api.kite.trade"  
logging.basicConfig(level=logging.DEBUG)
userid = ""
kite = KiteConnect(api_key=apiKey)
#print(kite.login_url())

#data = kite.generate_session(requestToken, api_secret=apiSecret)

#accessToken = data["access_token"]
print("Access Token:", accessToken)
kite.set_access_token(accessToken)
#print("Test")


def print_holdings():
    """
    Fetch and return holdings from the Kite Connect API.
    """
    return kite.holdings()

def main():
    holdings = print_holdings()
    print("Holdings:", type(holdings))
    # Convert holdings to DataFrame and save to CSV
    if holdings:
        df = pd.DataFrame(holdings)
        #df.to_csv("holdings.csv", index=False)
        #print("Holdings saved to holdings.csv")
    else:
        print("No holdings data to save.")

if __name__ == "__main__":
    main()