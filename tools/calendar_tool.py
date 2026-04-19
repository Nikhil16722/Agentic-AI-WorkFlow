"""
tools/calendar_tool.py
-----------------------
Calendar Tool — Callable interface for Google Calendar.
Uses Google Calendar API to create and fetch events.

MeetingAgent uses this tool to:
- Create calendar events from meeting summaries
- Check existing events
- List upcoming meetings
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------
# CalendarTool Class
# ---------------------------
class CalendarTool:
    """
    Callable interface for Google Calendar operations.

    Setup Required (.env):
        GOOGLE_CALENDAR_ID           = your-calendar-id@gmail.com
        GOOGLE_SERVICE_ACCOUNT_JSON  = path/to/service-account.json

    How to set up:
        1. Go to Google Cloud Console
        2. Enable Google Calendar API
        3. Create Service Account → Download JSON key
        4. Share your calendar with the service account email
        5. Add credentials path to .env

    Usage:
        tool = CalendarTool()
        result = tool.create_event(
            title="Project Kickoff",
            date="2026-04-20",
            time="10:00",
            duration_minutes=60,
            attendees=["team@company.com"]
        )
    """

    def __init__(self):
        self.calendar_id     = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.tool_name       = "CalendarTool"
        self.service         = None     # Google Calendar API service object

        # Try to initialize Google Calendar API
        self._init_service()

        logger.info("[CalendarTool] Initialized.")

    # ---------------------------
    # Initialize Google API Service
    # ---------------------------
    def _init_service(self):
        """
        Initializes Google Calendar API service.
        Falls back to dry-run mode if credentials missing.
        """
        if not self.credentials_path:
            logger.warning(
                "[CalendarTool] GOOGLE_SERVICE_ACCOUNT_JSON not found. "
                "Running in DRY RUN mode."
            )
            return

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/calendar"]

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )

            self.service = build("calendar", "v3", credentials=credentials)
            logger.info("[CalendarTool] Google Calendar API connected.")

        except Exception as e:
            logger.error(f"[CalendarTool] Failed to connect Google Calendar: {e}")
            self.service = None

    # ---------------------------
    # Format DateTime for Google API
    # ---------------------------
    def _format_datetime(self, date: str, time: str) -> str:
        """
        Converts date + time strings into ISO 8601 format
        required by Google Calendar API.

        Args:
            date : "YYYY-MM-DD"  e.g. "2026-04-20"
            time : "HH:MM"       e.g. "10:00"

        Returns:
            str : "2026-04-20T10:00:00" (ISO format)
        """
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        return dt.isoformat()

    # ---------------------------
    # CREATE EVENT
    # ---------------------------
    def create_event(
        self,
        title: str,
        date: str,
        time: str,
        duration_minutes: int = 60,
        description: str = "",
        attendees: Optional[list] = None,
        location: str = ""
    ) -> dict:
        """
        Creates a new Google Calendar event.

        Args:
            title            : Event title/name
            date             : Date in "YYYY-MM-DD" format
            time             : Start time in "HH:MM" format
            duration_minutes : Length of event in minutes (default: 60)
            description      : Optional event description/agenda
            attendees        : Optional list of attendee emails
            location         : Optional meeting location or link

        Returns:
            dict : {
                "status"   : "created" | "dry_run" | "failed",
                "event_id" : Google event ID (if created),
                "title"    : event title,
                "start"    : start datetime string,
                "end"      : end datetime string,
                "link"     : Google Calendar event link,
                "message"  : status description
            }

        Usage:
            result = tool.create_event(
                title="Q2 Planning Meeting",
                date="2026-04-25",
                time="14:00",
                duration_minutes=90,
                description="Quarterly planning session",
                attendees=["pm@company.com", "dev@company.com"],
                location="https://meet.google.com/abc-xyz"
            )
        """
        # Calculate end time
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt   = start_dt + timedelta(minutes=duration_minutes)

        start_iso = start_dt.isoformat()
        end_iso   = end_dt.isoformat()

        # Dry run mode if no service
        if not self.service:
            logger.info(
                f"[CalendarTool] DRY RUN — Would create event: "
                f"'{title}' on {date} at {time}"
            )
            return {
                "status": "dry_run",
                "event_id": "dry_run_id",
                "title": title,
                "start": start_iso,
                "end": end_iso,
                "link": "No link (dry run mode)",
                "message": f"Event '{title}' not created (no credentials). Dry run mode."
            }

        # Build event body
        event_body = {
            "summary": title,
            "description": description,
            "location": location,
            "start": {
                "dateTime": start_iso,
                "timeZone": "Asia/Kolkata"        # IST timezone (change if needed)
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": "Asia/Kolkata"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},   # 1 hour before
                    {"method": "popup", "minutes": 15}    # 15 min popup
                ]
            }
        }

        # Add attendees if provided
        if attendees:
            event_body["attendees"] = [
                {"email": email} for email in attendees
            ]

        # Call Google Calendar API
        try:
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_body,
                sendUpdates="all"           # Sends invite emails to attendees
            ).execute()

            event_link = event.get("htmlLink", "")
            event_id   = event.get("id", "")

            logger.info(
                f"[CalendarTool] Event created: '{title}' | "
                f"ID: {event_id} | Start: {start_iso}"
            )

            return {
                "status": "created",
                "event_id": event_id,
                "title": title,
                "start": start_iso,
                "end": end_iso,
                "link": event_link,
                "message": f"Event '{title}' created for {date} at {time}."
            }

        except Exception as e:
            error = f"Failed to create event: {str(e)}"
            logger.error(f"[CalendarTool] {error}")
            return {
                "status": "failed",
                "event_id": None,
                "title": title,
                "start": start_iso,
                "end": end_iso,
                "link": "",
                "message": error
            }

    # ---------------------------
    # GET UPCOMING EVENTS
    # ---------------------------
    def get_upcoming_events(self, max_results: int = 5) -> list:
        """
        Fetches upcoming calendar events.

        Args:
            max_results : Max number of events to return (default: 5)

        Returns:
            list : List of upcoming event dicts

        Usage:
            events = tool.get_upcoming_events(max_results=10)
            for event in events:
                print(event["title"], event["start"])
        """
        # Dry run mode
        if not self.service:
            logger.info("[CalendarTool] DRY RUN — get_upcoming_events called.")
            return [
                {
                    "event_id": "dry_run_1",
                    "title": "Sample Meeting (Dry Run)",
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(hours=1)).isoformat()
                }
            ]

        try:
            now = datetime.utcnow().isoformat() + "Z"   # UTC format for API

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])

            formatted = []
            for event in events:
                formatted.append({
                    "event_id": event.get("id"),
                    "title": event.get("summary", "No Title"),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "location": event.get("location", ""),
                    "link": event.get("htmlLink", "")
                })

            logger.info(f"[CalendarTool] Fetched {len(formatted)} upcoming events.")
            return formatted

        except Exception as e:
            logger.error(f"[CalendarTool] get_upcoming_events failed: {e}")
            return []

    # ---------------------------
    # DELETE EVENT
    # ---------------------------
    def delete_event(self, event_id: str) -> dict:
        """
        Deletes a calendar event by ID.

        Args:
            event_id : Google Calendar event ID

        Returns:
            dict : {"status": "deleted" | "failed", "message": ...}

        Usage:
            result = tool.delete_event("abc123eventid")
        """
        if not self.service:
            return {
                "status": "dry_run",
                "message": f"Would delete event ID: {event_id} (dry run mode)"
            }

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"[CalendarTool] Event deleted: {event_id}")
            return {
                "status": "deleted",
                "message": f"Event {event_id} deleted successfully."
            }

        except Exception as e:
            error = f"Failed to delete event: {str(e)}"
            logger.error(f"[CalendarTool] {error}")
            return {"status": "failed", "message": error}

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self) -> str:
        mode = "live" if self.service else "dry_run"
        return f"CalendarTool(calendar={self.calendar_id}, mode={mode})"