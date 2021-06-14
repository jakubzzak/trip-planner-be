from server import Config, mail
from flask_mail import Message


def send_mail(subject: str, recipient_email: str, html) -> bool:
    try:
        msg = Message(subject=subject, sender=(Config.MAIL_SENDER_NAME, Config.MAIL_USERNAME))
        if Config.MAIL_OVERRIDE:
            msg.add_recipient(Config.MAIL_OVERRIDE)
        else:
            msg.add_recipient(recipient_email)
        msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        print(str(e))
        return False
