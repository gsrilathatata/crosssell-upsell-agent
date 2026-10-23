import requests
import json
from vertexai.preview.generative_models import GenerativeModel

def get_usage_plan(customer_id: str) -> str:
    # Step 1: Fetch raw usage data
    response = requests.get(
        f"https://usagesummaries-kuock8.5sc6y6-3.usa-e2.cloudhub.io/api/usageSummary/{customer_id}"
    )
    usage_data = response.json()

    return usage_data
