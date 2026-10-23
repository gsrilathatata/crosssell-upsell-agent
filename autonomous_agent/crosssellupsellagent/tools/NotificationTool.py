import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crosssellupsellagent.config import CONFIG


def send_email(email_content: str) -> str:
    from_email = CONFIG["from_email"]
    password = CONFIG["password"]  # Use an app-specific password if using Gmail
    print(email_content)
    email_data = json.loads(email_content)
    print(email_data)
    content = email_data.get("email", {})
    subject = content.get("subject", "No Subject")
    body = content.get("body", "No Body")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = CONFIG["tomail"]
    msg['Subject'] =subject

    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
