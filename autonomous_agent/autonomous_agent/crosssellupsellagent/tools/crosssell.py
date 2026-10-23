import requests
import json
from vertexai.preview.generative_models import GenerativeModel
from crosssellupsellagent.tools.UsageRecommendationTool import get_usage_plan
from crosssellupsellagent.config import CONFIG

def get_crosssell_offer(customer_id: str) -> str:
    raw_text = get_usage_plan(customer_id)
    plan_name = raw_text["name"]
    payload = {
        "plan_name": plan_name
    }

    response_addon = requests.post(
        CONFIG["addonurl"],
        json=payload,  # Use `json=` instead of `data=` to send JSON
        headers={"Content-Type": "application/json"}
    )

    response_summary = requests.post(
        CONFIG["summaryurl"],
        json=payload,  # Use `json=` instead of `data=` to send JSON
        headers={"Content-Type": "application/json"}
    )
    
    combined_response = {
      "addon": response_addon.json(),
      "summary": response_summary.json()
    }
    return combined_response