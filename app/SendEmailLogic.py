from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import INFO
from pathlib import Path
from tempfile import template

from app.LoggingLogic import create_logger

from jinja2 import Environment, FileSystemLoader
import smtplib

send_email_logger = create_logger(name="Email", get_logger="app.SendEmailLogic", level=INFO)

BASE_DIR = Path(__file__).resolve().parent.parent  # Поднимаемся на уровень выше
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def send_email(email: str, code: str, session_id: str, username: str):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL = "dimon.2007.17@gmail.com"
    PASSWORD = "hlcp iesn abmu owrv"


    template = env.get_template("mail_response.html")
    html_content = template.render(code=code, session_id=session_id, username=username)

    msg = MIMEMultipart()
    msg["From"] = "dimon.2007.17@gmail.com"
    msg["To"] = email
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


