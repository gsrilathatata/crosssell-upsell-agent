from google.adk import Agent

import sys
sys.path.append("..")
from .tools.IntentDetectionTool import detect_user_intent

root_agent = Agent(
    name="crossell_upsell_agent",
    description="As an autonomous agent connects to various systems to achieve the task of sending promotional offers",
    model="gemini-2.0-flash-001",
    instruction="You are an expert connecting to the tools provided and sending promotional offers to users based on their chat history",
    tools=[detect_user_intent]
)
