"""Google Calendar integration via OAuth2."""

from datetime import datetime, timezone
from typing import Any

from config import GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_SCOPES


def _get_service() -> Any:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import os, json

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

    return build("calendar", "v3", credentials=creds)


def list_events(days_ahead: int = 7, max_results: int = 15) -> list[dict]:
    """List upcoming calendar events."""
    service = _get_service()
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    end = now + timedelta(days=days_ahead)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    out = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        out.append({
            "id": e["id"],
            "title": e.get("summary", "(no title)"),
            "start": start,
            "end": e["end"].get("dateTime", e["end"].get("date", "")),
            "location": e.get("location", ""),
            "description": e.get("description", "")[:200],
        })
    return out


def create_event(
    title: str,
    start: str,
    end: str,
    description: str = "",
    location: str = "",
    attendees: list[str] | None = None,
) -> dict:
    """
    Create a calendar event.
    start/end: ISO 8601 strings, e.g. '2026-07-01T10:00:00-05:00'
    """
    service = _get_service()
    body: dict = {
        "summary": title,
        "description": description,
        "location": location,
        "start": {"dateTime": start, "timeZone": "America/New_York"},
        "end": {"dateTime": end, "timeZone": "America/New_York"},
    }
    if attendees:
        body["attendees"] = [{"email": a} for a in attendees]

    event = service.events().insert(calendarId="primary", body=body).execute()
    return {"id": event["id"], "link": event.get("htmlLink", ""), "title": title}


def delete_event(event_id: str) -> str:
    """Delete a calendar event by its ID."""
    service = _get_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return f"Event {event_id} deleted."
