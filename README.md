# Cross-sell / Upsell Agent (Telecom)

A working prototype of two cooperating AI agents for a telecom provider, built on Google Cloud (Vertex AI, Dialogflow CX, BigQuery, Cloud Run):

1. **Virtual Tele Assist**: a conversational agent that talks to a customer, reviews their usage, recommends plans and add-ons, and places an order.
2. **Autonomous cross-sell / upsell agent**: a batch agent that reads a customer's recent chat history, detects whether they are a cross-sell or upsell opportunity, and sends a personalised promotional email.

> **Status: prototype built with sample data.** All customer records are synthetic. See [Limitations](#limitations-and-what-i-would-do-for-production) for what is missing before production use.

## Architecture

```
                      ┌─────────────────────────────┐
 Customer ──chat────▶ │  Web app (Dialogflow         │
                      │  Messenger widget)           │
                      └──────────────┬───────────────┘
                                     ▼
                      ┌─────────────────────────────┐        ┌──────────────────────────┐
                      │  Virtual Tele Assist         │──────▶ │ Usage / ordering APIs    │
                      │  (Dialogflow CX generative   │        │ (MuleSoft, CloudHub)     │
                      │   playbook + tools)          │        └──────────────────────────┘
                      └───┬──────────┬───────────┬───┘
                          │          │           │
                          ▼          ▼           ▼
                   Upsell model  Plan summary  Cross-sell
                   (Vertex AI    (Cloud Run +  (Cloud Run +
                    endpoint via  BigQuery)     BigQuery)
                    Cloud Run)
                          │
   Conversation history ──┴──▶ Cloud Run webhook ──▶ BigQuery (chat history)
                                                          │
                                                          ▼
                      ┌─────────────────────────────────────────────────┐
                      │ Autonomous agent (Google ADK + Gemini)           │
                      │ 1. fetch last 15 chat messages for a customer    │
                      │ 2. Gemini classifies intent: upsell | crosssell  │
                      │ 3. call the matching offer service               │
                      │ 4. Gemini drafts the email (JSON: subject, body) │
                      │ 5. send email via SMTP                           │
                      └─────────────────────────────────────────────────┘
```

## Repository layout

| Folder | What it contains |
|---|---|
| `Agent_Virtual Assist/` | Exported Dialogflow CX agent: generative playbook, tools (OpenAPI schemas), webhooks, intents |
| `autonomous_agent/` | Python agent built with Google ADK: `agent.py`, `config.py` and one file per tool under `tools/` |
| `CloudRun Funtions/` | Source of four Cloud Run services (zipped exports): `upsellrun`, `crossellrun`, `plansummary`, `conversationhistory` |
| `BigQueryTables/` | Sample CSVs to load into BigQuery: usage dataset (1,000 customers), chat history, plan details |
| `web app/` | Demo web page embedding the Dialogflow Messenger chat widget |

## How it works

### Virtual Tele Assist (conversational)
The playbook asks for the customer's mobile number, fetches usage history, and summarises it. It then asks the **upsell model** for the top two plans (excluding the current plan), explains a chosen plan using **plan summary**, offers eligible **add-ons** from the cross-sell service, and can place an order. Each conversation turn is logged to BigQuery through a webhook.

### Autonomous agent (batch)
`IntentDetectionTool` fetches the customer's recent chat messages from BigQuery, then Gemini decides **upsell** or **crosssell**.
- **Upsell:** usage data is normalised by Gemini and sent to a Vertex AI classification endpoint (via the `upsellrun` service). The top two plans are returned.
- **Cross-sell:** the customer's current plan is used to look up eligible add-ons and the plan summary.
- `MessageComposerTool` asks Gemini for a promotional email as structured JSON, and `NotificationTool` sends it.

### Cloud Run services
| Service | Purpose | Data source |
|---|---|---|
| `upsellrun` | Calls the Vertex AI endpoint that ranks plans from usage data | Vertex AI endpoint |
| `crossellrun` | Returns eligible add-ons for a plan | BigQuery `crosssellplandetails` |
| `plansummary` | Returns summary and pricing for a plan | BigQuery `plandescription` |
| `conversationhistory` | Webhook that stores each chat turn | BigQuery `conversationhistory` |

## Setup

**Prerequisites:** Python 3.12, a Google Cloud project with Vertex AI, BigQuery, Cloud Run and Dialogflow CX enabled, and `gcloud` authenticated.

1. **Load the data.** Create the datasets and tables, then load the CSVs from `BigQueryTables/`.
2. **Deploy the Cloud Run services.** Unzip each package under `CloudRun Funtions/` and deploy it. Edit the project, dataset and endpoint IDs in each `main.py` first.
3. **Restore the Dialogflow agent.** Import `Agent_Virtual Assist/` into Dialogflow CX and update each tool's URL to your deployed services.
4. **Configure the autonomous agent.**
   ```bash
   cd autonomous_agent
   pip install -r requirements.txt
   cp crosssellupsellagent/.env.example crosssellupsellagent/.env   # then fill in your values
   ```
   Fill in the Google Cloud settings in `.env` (never commit it):
   ```
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=<your-project-id>
   GOOGLE_CLOUD_LOCATION=us-central1
   MODEL=gemini-2.0-flash-001
   ```
   Then edit `config.py` with your own service URLs, customer ID and email settings. The sender address and password are placeholders in the repo and must be supplied locally (see Limitations on moving them to a secret store).
5. **Run the agent.**
   ```bash
   adk run crosssellupsellagent
   ```
6. **Try the web demo.** Set your own project and agent IDs in `web app/web app/index.html`, then open it in a browser.

## Limitations and what I would do for production

This was built to prove the flow end to end. Before real customers use it:

- **Authentication:** protect the Cloud Run services (IAM or authenticated invocation) and the customer-facing APIs. Today the services are called without credentials.
- **Secrets:** move SMTP credentials into Secret Manager, and replace hard-coded IDs and URLs in `config.py` with environment variables.
- **Customer consent and PII:** check marketing consent before sending any email, and restrict who can read chat history.
- **Customer selection:** the batch agent uses a single hard-coded customer ID. It should read a list of eligible customers from BigQuery on a schedule.
- **Evaluation and monitoring:** add an eval set for intent detection and email quality, log every model call with a correlation ID, and alert on failures.
- **Guardrails:** validate the model's JSON output against a schema, and have the email's price and plan details come from data, not from the LLM.
- **Email delivery:** use a transactional email service instead of a personal SMTP account. A human approval step for the first campaigns would also be sensible.
- **Code structure:** the pipeline currently runs when the intent tool module is imported. Move it into a function that the agent calls.

## Tech stack

Python, Google ADK, Gemini (Vertex AI), Dialogflow CX, Cloud Run, BigQuery, Flask, MuleSoft Anypoint (CloudHub) for the usage and ordering APIs, scikit-learn.
