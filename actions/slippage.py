import re
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class DynamicSlippageAction(Action):
    def name(self) -> Text:
        return "action_calculate_slippage"

    def extract_crypto_details(self, text: str) -> Dict[str, Any]:
        """
        Extract cryptocurrency and price from input text
        Supports various input formats
        """
        # Mapping of common crypto names to their CoinGecko IDs
        crypto_mapping = {
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'dogecoin': 'dogecoin',
            'doge': 'dogecoin',
            'litecoin': 'litecoin',
            'ltc': 'litecoin',
            'cardano': 'cardano',
            'ada': 'cardano',
            'ripple': 'ripple',
            'xrp': 'ripple'
        }

        # Try to find cryptocurrency
        crypto_match = None
        for word in text.lower().split():
            if word in crypto_mapping:
                crypto_match = crypto_mapping[word]
                break

        # Try to find price (look for numbers with optional $ sign)
        price_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)', text)
        price = float(price_match.group(1).replace(',', '')) if price_match else None

        return {
            'cryptocurrency': crypto_match,
            'expected_price': price
        }

    def fetch_crypto_price(self, crypto_id: str) -> float:
        """
        Fetch current price for a given cryptocurrency
        Uses CoinGecko API for real-time pricing
        """
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
            response = requests.get(url, params={
                "localization": False,
                "tickers": False,
                "market_data": True,
                "community_data": False,
                "developer_data": False,
                "sparkline": False
            })
            data = response.json()
            return data['market_data']['current_price']['usd']
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None

    def calculate_slippage(self, expected_price: float, execution_price: float) -> float:
        """
        Calculate slippage percentage
        """
        try:
            slippage = ((execution_price - expected_price) / expected_price) * 100
            return round(slippage, 2)
        except Exception as e:
            print(f"Slippage calculation error: {e}")
            return None

    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        
        # Get the latest user message
        latest_message = tracker.latest_message.get('text', '')
        
        # Extract cryptocurrency and expected price
        crypto_details = self.extract_crypto_details(latest_message)
        
        # Validate inputs
        if not crypto_details['cryptocurrency']:
            dispatcher.utter_message(text="Could not identify cryptocurrency. Please specify a supported crypto.")
            return []
        
        if not crypto_details['expected_price']:
            dispatcher.utter_message(text="Could not extract expected price. Please specify a price.")
            return []

        try:
            # Fetch current market price
            current_price = self.fetch_crypto_price(crypto_details['cryptocurrency'])
            
            if current_price is None:
                dispatcher.utter_message(text=f"Unable to fetch current price for {crypto_details['cryptocurrency']}.")
                return []

            # Calculate slippage
            slippage = self.calculate_slippage(
                crypto_details['expected_price'], 
                current_price
            )
            
            if slippage is None:
                dispatcher.utter_message(text="Error calculating slippage.")
                return []

            # Prepare response
            crypto_name = crypto_details['cryptocurrency'].capitalize()
            if slippage > 0:
                message = f"{crypto_name} - Positive Slippage: {slippage}%\n"
                message += f"Expected Price: ${crypto_details['expected_price']:.2f}\n"
                message += f"Current Market Price: ${current_price:.2f}\n"
                message += "Trade execution would be more favorable."
            elif slippage < 0:
                message = f"{crypto_name} - Negative Slippage: {abs(slippage)}%\n"
                message += f"Expected Price: ${crypto_details['expected_price']:.2f}\n"
                message += f"Current Market Price: ${current_price:.2f}\n"
                message += "Trade execution would be less favorable."
            else:
                message = f"{crypto_name} - No Slippage: Current price matches expected price."

            dispatcher.utter_message(text=message)
        
        except ValueError:
            dispatcher.utter_message(text="Invalid input. Please provide cryptocurrency and price.")
        
        return []