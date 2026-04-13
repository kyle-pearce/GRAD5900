"""
Google Calendar MCP Server

Exposes Google Calendar as MCP tools for listing events,
checking availability, and creating events.

Safety: create_event uses sendUpdates="none" so attendees
are never notified automatically. The user must open Google
Calendar and manually click Send to notify attendees.

Tools exposed:
- list_events: list upcoming calendar events
- check_availability: check free/busy for a date
- create_event: create an event (no auto-notification)
"""

import os
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("google-calendar")

# Timezone used for all date/time operations.
# Override via CALENDAR_TIMEZONE env var (default: America/New_York).
TIMEZONE = os.environ.get("CALENDAR_TIMEZONE", "America/New_York")


def _get_service():
    """Build an authenticated Google Calendar API client.

    Uses OAuth2 refresh token from environment variables.
    The token is refreshed automatically by the google-auth library.
    """
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_CALENDAR_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    return build("calendar", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# Tool 1: list_events
# ---------------------------------------------------------------------------
@mcp.tool()
def list_events(days_ahead: int = 7, max_results: int = 20) -> str:
    """List upcoming calendar events.

    Use this to see what meetings are coming up, prep for 1:1s,
    or understand the user's schedule.

    Args:
        days_ahead: How many days ahead to look. Default 7.
        max_results: Maximum events to return. Default 20.

    Returns:
        Formatted list of events with times and attendees.
    """
    service = _get_service()
    now = datetime.now(timezone.utc).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=end,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
        timeZone=TIMEZONE,
    ).execute()

    events = result.get("items", [])
    if not events:
        return f"No events in the next {days_ahead} days."

    lines = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "(no title)")
        attendees = [a["email"] for a in e.get("attendees", [])]
        att_str = f" \u2014 with: {', '.join(attendees)}" if attendees else ""
        lines.append(f"\u2022 {start}  {summary}{att_str}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 2: check_availability
# ---------------------------------------------------------------------------
@mcp.tool()
def check_availability(
    date: str, start_hour: int = 9, end_hour: int = 17
) -> str:
    """Check free/busy slots for a given date.

    Use this before scheduling a meeting to find open time slots.

    Args:
        date: Date to check in YYYY-MM-DD format.
        start_hour: Start of window (24h). Default 9.
        end_hour: End of window (24h). Default 17.

    Returns:
        List of busy slots, or confirmation that the day is free.
    """
    service = _get_service()
    time_min = f"{date}T{start_hour:02d}:00:00"
    time_max = f"{date}T{end_hour:02d}:00:00"

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": TIMEZONE,
        "items": [{"id": "primary"}],
    }
    result = service.freebusy().query(body=body).execute()
    busy = result["calendars"]["primary"]["busy"]

    if not busy:
        return f"Fully available on {date} from {start_hour}:00 to {end_hour}:00 ({TIMEZONE})."

    lines = [f"Busy slots on {date} ({TIMEZONE}):"]
    for slot in busy:
        lines.append(f"  \u2022 {slot['start']} \u2192 {slot['end']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3: create_event
# ---------------------------------------------------------------------------
@mcp.tool()
def create_event(
    summary: str,
    date: str,
    start_time: str,
    duration_minutes: int = 30,
    description: str = "",
    attendee_emails: list[str] | None = None,
) -> str:
    """Create a calendar event. Attendees are NOT auto-notified.

    The event is created on the user's calendar but sendUpdates
    is set to "none" \u2014 the user must open Google Calendar and
    click Send to notify attendees. This is a safety measure.

    Args:
        summary: Event title.
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM format (24h), e.g. "14:30".
        duration_minutes: Length in minutes. Default 30.
        description: Optional event description/agenda.
        attendee_emails: Optional list of attendee email addresses.

    Returns:
        Confirmation with event details and a link to the event.
    """
    service = _get_service()

    # Parse start time
    start_h, start_m = map(int, start_time.split(":"))
    start_dt = f"{date}T{start_h:02d}:{start_m:02d}:00"

    # Calculate end time
    total_minutes = start_h * 60 + start_m + duration_minutes
    end_h, end_m = divmod(total_minutes, 60)
    end_dt = f"{date}T{end_h:02d}:{end_m:02d}:00"

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt, "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt, "timeZone": TIMEZONE},
    }
    if attendee_emails:
        event["attendees"] = [{"email": e} for e in attendee_emails]

    created = service.events().insert(
        calendarId="primary", body=event, sendUpdates="none"
    ).execute()

    return (
        f"Event created: {created['summary']} on {date} "
        f"at {start_time} ({duration_minutes}min) [{TIMEZONE}]\n"
        f"Link: {created.get('htmlLink', 'n/a')}"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
