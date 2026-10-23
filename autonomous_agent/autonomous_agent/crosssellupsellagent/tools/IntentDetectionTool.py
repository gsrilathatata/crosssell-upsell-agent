from vertexai.preview.generative_models import GenerativeModel
from crosssellupsellagent.tools.FetchChatHistoryTool import fetch_chat_history
from crosssellupsellagent.tools.UsageRecommendationTool import get_usage_plan
from crosssellupsellagent.tools.upsell import get_upsell_offer
from crosssellupsellagent.tools.crosssell import get_crosssell_offer
from crosssellupsellagent.tools.MessageComposerTool import compose_message
from crosssellupsellagent.tools.NotificationTool import send_email
from crosssellupsellagent.config import CONFIG

customer_id = CONFIG["customer_id"]

def detect_intent(chat_text: str) -> str:
    model = GenerativeModel("gemini-2.5-flash")
    prompt = f"What is the user's intent based on this conversation:\n{chat_text}. provide the either crossell or upsell based on chat conversation intent. do not change naming convetion on intent "
    response = model.generate_content(prompt)
    return response.text.strip().lower()

#@tool(name="detect_user_intent", description="Fetches chat history and detects intent.")
def detect_user_intent() -> str:
    chat_text = fetch_chat_history(customer_id)
    return detect_intent(chat_text)

# ✅ Make sure this call is after the function is defined
intent = detect_user_intent()


if "upsell" in intent:
   result = get_upsell_offer( customer_id)
elif "crosssell" in intent:
   result = get_crosssell_offer( customer_id)
else:
   result = "Intent not recognized."

email_content = compose_message(result)
send_email(email_content)
