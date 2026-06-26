"""Gmail send/read via Google API."""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

from config import GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_SCOPES, EMAIL_FROM


def _get_service() -> Any:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import os

    creds = None
    if os.path.exists(GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """Send an email via Gmail."""
    service = _get_service()

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    part = MIMEText(body, "html" if html else "plain")
    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return {"message_id": result["id"], "status": "sent", "to": to, "subject": subject}


def list_emails(max_results: int = 10, query: str = "") -> list[dict]:
    """List recent emails (inbox)."""
    service = _get_service()
    q = query or "in:inbox"
    response = service.users().messages().list(userId="me", q=q, maxResults=max_results).execute()
    messages = response.get("messages", [])

    emails = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        emails.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": detail.get("snippet", ""),
        })
    return emails
