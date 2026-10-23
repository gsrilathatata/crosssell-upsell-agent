import requests
import json
from vertexai.preview.generative_models import GenerativeModel
from crosssellupsellagent.tools.UsageRecommendationTool import get_usage_plan
from crosssellupsellagent.config import CONFIG

def get_upsell_offer(customer_id: str) -> str:
    usage_data = get_usage_plan(customer_id)
    model = GenerativeModel("gemini-2.5-flash")
    prompt = f"""
You are a data assistant. Given this usage summary JSON:

{usage_data}

Extract and return a dictionary with the following keys:
- MonthlyDataUsage (in GB) as number
- MonthlyCallUsage (in minutes) as string
- MonthlySmsUsage (in count) as string

Only return the dictionary in JSON format.
"""
    result = model.generate_content(prompt)
    raw_text = result.text.strip()
    if raw_text.startswith("```json"):
       raw_text = raw_text.replace("```json", "").replace("```", "").strip()  
    
    response = requests.post(
        CONFIG["upsellurl"],
        data=raw_text,
        headers={"Content-Type": "application/json"}
    )

    # Step 3: Parse the response JSON
    try:
        prediction = response.json()
    except json.JSONDecodeError:
        return ["Failed to parse upsell model response."]

    # Step 4: Extract top 2 plans
    try:
        classes = prediction[0]["classes"]
        scores = prediction[0]["scores"]
        sorted_plans = sorted(zip(classes, scores), key=lambda x: x[1], reverse=True)
        top_2 = [plan for plan, _ in sorted_plans[:2]]
        return top_2
    except (KeyError, IndexError, TypeError):
        return ["Invalid prediction format."]
