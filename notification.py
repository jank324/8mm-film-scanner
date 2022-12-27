import smtplib
from email.message import EmailMessage

import yaml

from utils import BaseCallback


class EmailNotifier:
    """
    Convenience class to send e-mail notifications in a preconfigured e-mail template.
    """

    def __init__(self) -> None:
        with open("notification_config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)

        self.to = config["to"]
        self.user = config["user"]
        self.password = config["password"]

        self.sender = f"Jan's Film Scanner <{self.user}>"

    def send(self, text: str) -> None:
        """
        Send an e-mail notification to the configured address with `text` as the
        message.
        """
        message = EmailMessage()
        message.set_content("")
        message["to"] = self.to
        message["from"] = self.sender
        message["subject"] = text

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.user, self.password)
        server.send_message(message)
        server.quit()


class MailCallback(BaseCallback):
    """Callback for sending an e-mail notification when a scan finished."""

    def __init__(self) -> None:
        self.notifier = EmailNotifier()

    def on_scan_end(self) -> None:
        self.notifier.send(f"Finished scanning {self.scanner.n_frames} frames!")
