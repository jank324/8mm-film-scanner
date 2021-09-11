import smtplib
from email.message import EmailMessage
import yaml


class EmailNotifier:

    def __init__(self):
        with open("notification_config.yml", "r") as config_file:
            config = yaml.safe_load(config_file)
        
        self._to = config["to"]
        self._user = config["user"]
        self._password = config["password"]

        self._from = f"Jan's Film Scanner <{self._user}>"
    
    def send(self, text):
        """Send an e-mail notification to the configured address with `text` as the message."""
        message = EmailMessage()
        message.set_content("")
        message["to"] = self._to
        message["from"] = self._from
        message["subject"] = text

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self._user, self._password)
        server.send_message(message)
        server.quit()


if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send("This is a test!")
