import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionLiveCryptoData(Action):
    def name(self) -> Text:
        return "action_live_market_data"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        try:
            # Get live price data for top cryptocurrencies
            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 10,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h,7d,30d"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}")
                
            crypto_data = response.json()
            
            # Format message with live data
            message = "Current Cryptocurrency Market Overview:\n\n"
            
            for coin in crypto_data:
                price = coin["current_price"]
                change_24h = coin["price_change_percentage_24h_in_currency"]
                change_7d = coin["price_change_percentage_7d_in_currency"]
                market_cap = coin["market_cap"]
                
                message += f"*{coin['name']} ({coin['symbol'].upper()})*\n"
                message += f"Price: ${price:,.2f}\n"
                message += f"24h Change: {change_24h:.2f}%\n"
                message += f"7d Change: {change_7d:.2f}%\n"
                message += f"Market Cap: ${market_cap:,.0f}\n\n"
            
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            print(f"Error fetching crypto data: {str(e)}")
            dispatcher.utter_message(text="I'm having trouble retrieving live cryptocurrency data right now.")
            
        return []