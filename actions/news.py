from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionCryptoNews(Action):
    def name(self) -> Text:
        return "action_crypto_news"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        url = "https://cryptocurrency-news2.p.rapidapi.com/v1/cointelegraph"
        headers = {
            "X-RapidAPI-Key": "ab8f7b4349msh50141c095d909bfp1704d5jsn0d63b8bfe685",
            "X-RapidAPI-Host": "cryptocurrency-news2.p.rapidapi.com"
        } 
        try:
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
            # Navigate through the nested structure
            if 'data' in response_data and isinstance(response_data['data'], list):
                news_items = response_data['data']
                top_news = news_items[:5]
                
                if top_news:
                    dispatcher.utter_message(text="Here is the latest crypto related news from CoinTelegraph:")
                    
                    for i, news in enumerate(top_news, 1):
                        # Extract data from the nested structure
                        title = news.get('title', 'No title available')
                        url = news.get('url', '')
                        
                        # Get description if available
                        description = ''
                        if 'description' in news and isinstance(news['description'], dict):
                            description_dict = news['description']
                            if 'p' in description_dict and isinstance(description_dict['p'], list):
                                for p_item in description_dict['p']:
                                    if '#text' in p_item:
                                        description += p_item['#text'] + " "
                        
                        # Send formatted messages
                        dispatcher.utter_message(text=f"{i}. {title}")
                        if description:
                            dispatcher.utter_message(text=f"Summary: {description.strip()}")
                        dispatcher.utter_message(text=f"Link: {url}")
                        dispatcher.utter_message(text="---")
                else:
                    dispatcher.utter_message(text="Sorry, I couldn't find any crypto related news")
            else:
                dispatcher.utter_message(text="Received unexpected data format from the API")
        
        except Exception as e:
            dispatcher.utter_message(text=f"Encountered an error: {str(e)}")
    
        return []