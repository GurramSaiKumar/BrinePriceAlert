import requests
import smtplib
from celery import shared_task
from django.core.mail import send_mail


def fetch_latest_price(cryptocurrency):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "USD",
        "ids": cryptocurrency,
        "order": "market_cap_desc",
        "per_page": 1,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get("current_price")
    return None


def send_email(recipient, subject, body):
    # SMTP server configuration
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "xxxx@gmail.com"
    smtp_password = "xxxxx"

    # Email configuration
    sender = "xxxx@gmail.com"
    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipient, message)


def print_alert_notification(alert):
    print(f"Price alert triggered for cryptocurrency {alert.cryptocurrency}. Target price: {alert.target_price}")


@shared_task
def send_email_task(recipient, subject, body):
    send_mail(subject, body, 'sender@example.com', [recipient])
