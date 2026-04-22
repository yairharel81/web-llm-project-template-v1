import asyncio
import logging
from typing import Protocol

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
    """Brevo transactional email (brevo-python v4+).

    The package was renamed from `brevo_python` to `brevo` in v4.
    Import is deferred so the mock path never touches the SDK.
    """

    def __init__(self) -> None:
        import brevo  # noqa: PLC0415

        self._brevo = brevo
        self._api_key = settings.brevo_api_key

    async def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> None:
        brevo = self._brevo

        def _send() -> None:
            client = brevo.Brevo(api_key=self._api_key)
            client.transactional_emails.send_transac_email(
                brevo.SendTransacEmailRequestSender(
                    email=settings.email_from,
                    name=settings.email_from_name,
                ),
                to=[brevo.SendTransacEmailRequestToItem(email=to_email, name=to_name)],
                subject=subject,
                html_content=html_content,
            )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)


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
