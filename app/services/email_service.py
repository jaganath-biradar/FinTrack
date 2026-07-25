import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def _smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from": os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "noreply@fintrack.app")),
    }


def _send(to: str, subject: str, html: str) -> bool:
    cfg = _smtp_config()
    if not cfg["user"] or not cfg["password"]:
        logger.warning("SMTP not configured — email not sent")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg["from"]
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from"], to, msg.as_string())
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to}: {e}")
        return False


def send_verification_email(to: str, full_name: str, token: str) -> bool:
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    link = f"{base_url}/auth/verify-email?token={token}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:480px;margin:auto;padding:32px;background:#0F1E2D;color:#E2E8F0;border-radius:12px">
      <h2 style="color:#10B981">Verify your FinTrack account</h2>
      <p>Hi {full_name},</p>
      <p>Click the button below to verify your email address. This link expires in 24 hours.</p>
      <a href="{link}" style="display:inline-block;margin:16px 0;padding:12px 24px;background:#10B981;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">Verify Email</a>
      <p style="color:#64748B;font-size:0.85rem">If you didn't create an account, ignore this email.</p>
    </div>"""
    return _send(to, "Verify your FinTrack email", html)


def send_password_reset_email(to: str, full_name: str, token: str) -> bool:
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    link = f"{base_url}/auth/reset-password?token={token}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:480px;margin:auto;padding:32px;background:#0F1E2D;color:#E2E8F0;border-radius:12px">
      <h2 style="color:#10B981">Reset your FinTrack password</h2>
      <p>Hi {full_name},</p>
      <p>Click the button below to reset your password. This link expires in 1 hour.</p>
      <a href="{link}" style="display:inline-block;margin:16px 0;padding:12px 24px;background:#10B981;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">Reset Password</a>
      <p style="color:#64748B;font-size:0.85rem">If you didn't request this, ignore this email.</p>
    </div>"""
    return _send(to, "Reset your FinTrack password", html)
