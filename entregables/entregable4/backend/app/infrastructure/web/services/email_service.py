"""Servicio de email (SMTP)."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.infrastructure.config.settings import Settings

log = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def enviar(self, destinatario: str, asunto: str, cuerpo_html: str) -> None:
        if not self.settings.smtp_user:
            log.warning("SMTP no configurado, no se envía email a %s", destinatario)
            return

        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = self.settings.smtp_from
        msg["To"] = destinatario
        msg.set_content("Activar HTML en su cliente.")
        msg.add_alternative(cuerpo_html, subtype="html")

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as s:
                s.starttls()
                s.login(self.settings.smtp_user, self.settings.smtp_password)
                s.send_message(msg)
        except Exception as e:
            log.exception("Error enviando email: %s", e)
            raise
