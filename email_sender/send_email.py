import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, to_emails, from_email=None, smtp_server=None, smtp_port=None, smtp_user=None, smtp_password=None):
    from_email = from_email or os.getenv('EMAIL_SENDER')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
    smtp_user = smtp_user or os.getenv('SMTP_USER', from_email)
    smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_emails, msg.as_string())
    print(f"Mail envoyé à {to_emails}")

if __name__ == "__main__":
    # Exemple d'utilisation
    with open('../veille_ai_summaries.html', encoding='utf-8') as f:
        summary = f.read()
    # Récupère les destinataires depuis la variable d'environnement EMAIL_RECIPIENTS
    recipients = os.getenv('EMAIL_RECIPIENTS', 'destinataire@example.com').split(',')
    recipients = [email.strip() for email in recipients if email.strip()]
    send_email(
        subject="Veille technologique IA/Data - Hebdo",
        body=summary.replace('\n', '<br>'),
        to_emails=recipients
    )
