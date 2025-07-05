import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import INFO
from pathlib import Path

from jinja2 import FileSystemLoader, Environment

from app.LoggingLogic import create_logger
from app.celery_app import celery

send_email_logger = create_logger(name="Email_Task", get_logger="app.SendEmailLogic", level=INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

@celery.task(bind=True, max_retries=3)
def send_verification_email(self, email_data_json: str):
    try:
        email_data = json.loads(email_data_json)

        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL = "dimon.2007.17@gmail.com"
        PASSWORD = "hlcp iesn abmu owrv"

        template = env.get_template("mail_response.html")
        html_content = template.render(code=email_data["code"], session_id=email_data["session_id"], username=email_data["username"])

        msg = MIMEMultipart()
        msg["From"] = "dimon.2007.17@gmail.com"
        msg["To"] = email_data["email"]
        msg["Subject"] = "Подтвердите ваш email"

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
                send_email_logger.info("Письмо отправлено!")
        except smtplib.SMTPAuthenticationError:
            send_email_logger.error("Ошибка Авторизации")
        except smtplib.SMTPException as e:
            send_email_logger.error(f"Ошибка отправки письма: {str(e)}")
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")
            send_email_logger.error(f"Неожиданная ошибка: {str(e)}")
    except Exception as e:
        send_email_logger.error(f"Неожиданная ошибка: {str(e)}")
        raise self.retry(exc=e, countdown=60)