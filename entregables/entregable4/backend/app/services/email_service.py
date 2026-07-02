import smtplib
from email.message import EmailMessage

from app.core.config import get_settings


class EmailService:
    @staticmethod
    def enviar_codigo_recuperacion(destinatario: str, codigo: str) -> None:
        settings = get_settings()

        asunto = "Código de recuperación de contraseña - Codex Venta"
        cuerpo = f"""
Hola,

Recibimos una solicitud para recuperar tu contraseña en Codex Venta.

Tu código de verificación es: {codigo}

Este código vence en {settings.reset_code_expire_minutes} minutos.
Si no solicitaste este cambio, puedes ignorar este mensaje.

Codex Venta
""".strip()

        smtp_password = (settings.smtp_password or "").replace(" ", "").strip()

        if not settings.smtp_enabled or not smtp_password:
            print("[RECUPERACION_CONTRASENA] SMTP no configurado. Código generado para", destinatario, ":", codigo)
            return

        mensaje = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
        mensaje["To"] = destinatario
        mensaje.set_content(cuerpo)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as servidor:
            if settings.smtp_use_tls:
                servidor.starttls()
            servidor.login(settings.smtp_user, smtp_password)
            servidor.send_message(mensaje)
