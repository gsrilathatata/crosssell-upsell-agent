from google.cloud import bigquery

def fetch_chat_history(customer_id: str) -> str:
    client = bigquery.Client()
    query = """
        SELECT chat_message 
        FROM `hacker2025-team-46-dev.Chathistory.chathistory-cleaned`
        WHERE customer_id = @customer_id
        ORDER BY timestamp DESC
        LIMIT 15
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)
        ]
    )
    result = client.query(query, job_config=job_config).result()
    return " ".join([row.chat_message for row in result])

