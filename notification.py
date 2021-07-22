import smtplib
from email.message import EmailMessage
import yaml


with open("notification_config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)


def send_notification(text):
    """Send an e-mail notification to the configured address with `text` as the message."""
    message = EmailMessage()
    message.set_content("")
    message["to"] = config["to"]
    message["from"] = f"Jan's Film Scanner <{config['user']}>"
    message["subject"] = text

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(config["user"], config["password"])
    server.send_message(message)
    server.quit()


if __name__ == "__main__":
    send_notification("This is a test!")
