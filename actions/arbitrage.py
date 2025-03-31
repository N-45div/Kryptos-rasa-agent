from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionArbitrageData(Action):
    def name(self) -> Text:
        return "action_crypto_arbitrage"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        url = "https://crypto-arbitrage3.p.rapidapi.com/arbitrage"
        querystring = {"keyword":"binance"}
        
        headers = {
            "X-RapidAPI-Key": "API-KEY",
            "X-RapidAPI-Host": "crypto-arbitrage3.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            crypto_data = response.json()
            
            # Limit to top 10 opportunities
            top_data = crypto_data[:10]
            
            if top_data:
                dispatcher.utter_message(text="Here are profitable arbitrage opportunities between cryptocurrency exchanges:")
                
                # Process each arbitrage opportunity
                for i, data in enumerate(top_data, 1):
                    dispatcher.utter_message(text=f"Opportunity #{i}:")
                    dispatcher.utter_message(text=f"Buy on Exchange: {data['buy_exchange']}")
                    dispatcher.utter_message(text=f"Buy price: {data['buy_price']}")
                    dispatcher.utter_message(text=f"Coin: {data['coin']}")
                    dispatcher.utter_message(text=f"Profit: {data['profit']}%")
                    dispatcher.utter_message(text=f"Sell on Exchange: {data['sell_exchange']}")
                    dispatcher.utter_message(text=f"Selling price: {data['sell_price']}")
                    dispatcher.utter_message(text="---")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't find any profitable trades")
                
        except Exception as e:
            dispatcher.utter_message(text=f"Encountered an error: {str(e)}")
        
        return []
