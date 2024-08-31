import smtplib
import imaplib
import email
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email credentials
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_password"

# IMAP server credentials
IMAP_SERVER = "imap.example.com"
IMAP_PORT = 993

# SMTP server credentials
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587

# Recipient email address for reports
RECIPIENT_EMAIL = "recipient@example.com"

def fetch_emails(email_address, email_password):
    """Fetch unread emails from the inbox."""
    try:
        # Connect to the mail server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email_address, email_password)
        mail.select("inbox")

        # Search for all unread emails
        status, messages = mail.search(None, '(UNSEEN)')

        email_messages = []
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            email_messages.append(email_message)

        mail.close()
        mail.logout()

        return email_messages
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def send_email(subject, body, recipient):
    """Send an email."""
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Send the email
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())

        # Terminate the SMTP session
        server.quit()
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_report(email_messages):
    """Generate a report based on the fetched emails."""
    report = "Daily Email Report\n\n"
    for i, message in enumerate(email_messages, start=1):
        report += f"Email {i}:\n"
        report += f"From: {message['From']}\n"
        report += f"Subject: {message['Subject']}\n\n"
    return report

def daily_email_report():
    """Fetch emails and send a daily report."""
    email_messages = fetch_emails(EMAIL_ADDRESS, EMAIL_PASSWORD)
    if email_messages:
        report = generate_report(email_messages)
        send_email("Daily Email Report", report, RECIPIENT_EMAIL)
    else:
        print("No new emails to report.")

# Schedule the daily email report
schedule.every().day.at("09:00").do(daily_email_report)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
