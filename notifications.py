OUTBOX_PATH = "outbox.txt"


class MockNotifier:
    """Mock object that simulates an email server without sending real emails."""

    def __init__(self, outbox_path=OUTBOX_PATH):
        self.outbox_path = outbox_path
        self.sent_messages = []

    def send_email(self, email, subject, body):
        record = f"TO: {email} | SUBJECT: {subject} | BODY: {body}"
        self.sent_messages.append(
            {"to": email, "subject": subject, "body": body})
        with open(self.outbox_path, "a") as f:
            f.write(record + "\n")


notifier = MockNotifier()


def send_email(email, subject, body):
    notifier.send_email(email, subject, body)
