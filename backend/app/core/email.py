import logging
from typing import Protocol

import brevo_python
from brevo_python.api import transactional_emails_api
from brevo_python.model.send_smtp_email import SendSmtpEmail
from brevo_python.model.send_smtp_email_sender import SendSmtpEmailSender
from brevo_python.model.send_smtp_email_to_inner import SendSmtpEmailToInner

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService(Protocol):
    async def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> None: ...


class MockEmailService:
    async def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> None:
        logger.info(
            "[mock email] To: %s <%s> | Subject: %s",
            to_name,
            to_email,
            subject,
        )


class BrevoEmailService:
    def __init__(self) -> None:
        configuration = brevo_python.Configuration()
        configuration.api_key["api-key"] = settings.brevo_api_key
        client = brevo_python.ApiClient(configuration)
        self._api = transactional_emails_api.TransactionalEmailsApi(client)

    async def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> None:
        email = SendSmtpEmail(
            sender=SendSmtpEmailSender(
                email=settings.email_from,
                name=settings.email_from_name,
            ),
            to=[SendSmtpEmailToInner(email=to_email, name=to_name)],
            subject=subject,
            html_content=html_content,
        )
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self._api.send_transac_email, email
        )


def get_email_service() -> EmailService:
    if settings.use_mock_email:
        return MockEmailService()
    return BrevoEmailService()


# ── Reusable email templates ──────────────────────────────────────────────────

def render_verification_email(verification_url: str) -> str:
    return f"""
    <h2>Verify your email</h2>
    <p>Click the link below to verify your email address:</p>
    <a href="{verification_url}">Verify Email</a>
    <p>This link expires in 24 hours.</p>
    """


def render_password_reset_email(reset_url: str) -> str:
    return f"""
    <h2>Reset your password</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>This link expires in 1 hour. If you did not request this, ignore this email.</p>
    """
