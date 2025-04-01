from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import san
import pandas as pd
from datetime import datetime, timedelta

san.ApiConfig.api_key = "api-key"

class ActionmvrvData(Action):
    def name(self) -> Text:
        return "action_mvrv_data"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        try:
            # Set dates within the allowed range for free tier
            # Using recent past date and a date within allowed bounds
            end_date = datetime(2025, 3, 28)  # Using the max allowed date from error
            start_date = datetime(2024, 3, 31)  # Using day after min allowed date
            
            # Format dates for GraphQL
            end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            result = san.graphql.execute_gql(f"""
            {{
                allProjects(
                    selector: {{
                    baseProjects: {{
                        slugs: ["ethereum", "bitcoin", "aave"]
                    }}
                    }}) {{
                    slug
                    aggregatedTimeseriesData(
                        metric: "mvrv_usd_intraday_365d"
                        from: "{start_date_str}"
                        to: "{end_date_str}"
                        aggregation: LAST)
                }}
            }}
            """)
            
            # Extract data from the result structure
            projects_data = result['allProjects']
            
            # Format the data for display
            message = "MVRV Ratio for cryptocurrencies:\n"
            
            for project in projects_data:
                slug = project['slug']
                mvrv_value = project['aggregatedTimeseriesData']
                
                # Handle the case when the value is available
                if mvrv_value is not None:
                    message += f"- {slug.capitalize()}: {mvrv_value:.2f}\n"
                else:
                    message += f"- {slug.capitalize()}: Data not available\n"
            
            # Send the formatted message
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            # Add error handling to help debug
            print(f"Error in action_coin_data: {str(e)}")
            dispatcher.utter_message(text="I'm having trouble retrieving cryptocurrency data right now.")
            
        return []
