#!/usr/bin/env python3
"""
Google Calendar Integration for OpenClaw
List events, create events, check schedule.
Uses OAuth2 refresh token from google-calendar-token.json
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta


def run_security_gate():
    if os.environ.get("OPENCLAW_SKIP_SECURITY_CHECK") == "1":
        return
    cmd = ["bash", "/home/piet/.openclaw/scripts/security-check.sh", "--scope", "workspace"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("❌ Security gate failed. Aborting sensitive script execution.")
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())
        sys.exit(proc.returncode)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = os.path.expanduser("~/.openclaw/secrets/google-calendar-token.json")

def get_calendar_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=None,
        refresh_token=token_data["refresh_token"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    
    return build("calendar", "v3", credentials=creds)

def list_today_events():
    """List today's calendar events."""
    service = get_calendar_service()
    now = datetime.utcnow()
    start = now.isoformat() + "Z"
    end = (now + timedelta(days=1)).isoformat() + "Z"
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    
    events = events_result.get("items", [])
    if not events:
        print("📅 Heute keine Termine.")
        return
    
    print(f"📅 Heute ({datetime.now().strftime('%d.%m.%Y')}):")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "Kein Titel")
        location = event.get("location", "")
        print(f"  • {start[11:16]} — {summary}")
        if location:
            print(f"    📍 {location}")

def list_upcoming(days=7):
    """List upcoming events for the next N days."""
    service = get_calendar_service()
    now = datetime.utcnow()
    start = now.isoformat() + "Z"
    end = (now + timedelta(days=days)).isoformat() + "Z"
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    
    events = events_result.get("items", [])
    if not events:
        print(f"📅 Keine Termine in den nächsten {days} Tagen.")
        return
    
    print(f"📅 Termine (nächste {days} Tage):")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "Kein Titel")
        date_str = start[:10]
        time_str = start[11:16] if "T" in start else ""
        if time_str:
            print(f"  • {date_str} {time_str} — {summary}")
        else:
            print(f"  • {date_str} ganztägig — {summary}")

def create_event(title, start_time, duration_minutes=60, description="", location=""):
    """Create a new calendar event."""
    from dateutil import parser
    
    service = get_calendar_service()
    start_dt = parser.parse(start_time)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    event = {
        "summary": title,
        "description": description,
        "location": location,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Berlin"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Berlin"},
    }
    
    created = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ Event erstellt: {title}")
    print(f"   ID: {created['id']}")
    return created

if __name__ == "__main__":
    run_security_gate()
    if len(sys.argv) < 2:
        print("Google Calendar CLI")
        print("Usage:")
        print("  python3 google-calendar.py today          — Today's events")
        print("  python3 google-calendar.py upcoming [days] — Upcoming events (default 7)")
        print("  python3 google-calendar.py create <title> <ISO-time> [duration-min] [description] [location]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "today":
        list_today_events()
    elif cmd == "upcoming":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        list_upcoming(days)
    elif cmd == "create":
        if len(sys.argv) < 3:
            print("Usage: create <title> <ISO-time> [duration-min] [description] [location]")
            sys.exit(1)
        title = sys.argv[2]
        start_time = sys.argv[3]
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        description = sys.argv[5] if len(sys.argv) > 5 else ""
        location = sys.argv[6] if len(sys.argv) > 6 else ""
        create_event(title, start_time, duration, description, location)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
