"""
tools/slack_tool.py
--------------------
Slack Tool — Callable interface for sending Slack messages.
Uses Slack Incoming Webhooks (no bot token needed).

TaskAgent uses this tool to:
- Notify team about new tasks
- Send workflow completion alerts
- Post summaries to Slack channels
"""

import os
import json
import logging
import requests
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------
# SlackTool Class
# ---------------------------
class SlackTool:
    """
    Callable interface for Slack messaging.

    Setup Required (.env):
        SLACK_WEBHOOK_URL = https://hooks.slack.com/services/xxx/yyy/zzz

    How to get Slack Webhook URL:
        1. Go to https://api.slack.com/apps
        2. Create New App → From Scratch
        3. Features → Incoming Webhooks → Activate
        4. Add New Webhook to Workspace
        5. Choose channel → Copy Webhook URL
        6. Add URL to .env

    Usage:
        tool = SlackTool()
        result = tool.send_message(
            text="New tasks assigned from today's meeting!",
            channel="#project-updates"
        )
    """

    # Slack API endpoint for webhook posts
    SLACK_API_URL = "https://slack.com/api/chat.postMessage"

    def __init__(self):
        self.webhook_url  = os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token    = os.getenv("SLACK_BOT_TOKEN")    # Optional
        self.tool_name    = "SlackTool"
        self.default_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "#general")

        if not self.webhook_url and not self.bot_token:
            logger.warning(
                "[SlackTool] No Slack credentials found in .env. "
                "Running in DRY RUN mode."
            )

        logger.info("[SlackTool] Initialized.")

    # ---------------------------
    # Check if Live Mode
    # ---------------------------
    def _is_live(self) -> bool:
        """Returns True if Slack credentials exist."""
        return bool(self.webhook_url or self.bot_token)

    # ---------------------------
    # Build Simple Message Payload
    # ---------------------------
    def _build_payload(self, text: str, channel: Optional[str] = None) -> dict:
        """
        Builds a simple Slack message payload.

        Args:
            text    : Message text content
            channel : Target Slack channel

        Returns:
            dict : Slack API payload
        """
        payload = {"text": text}
        if channel:
            payload["channel"] = channel
        return payload

    # ---------------------------
    # Build Rich Block Message
    # ---------------------------
    def _build_block_payload(
        self,
        title: str,
        body: str,
        color: str = "#36a64f",
        channel: Optional[str] = None
    ) -> dict:
        """
        Builds a rich Slack block message with formatting.

        Args:
            title   : Bold header text
            body    : Main message content
            color   : Sidebar color hex
                      #36a64f = green (success)
                      #e01e5a = red (error)
                      #ecb22e = yellow (warning)
                      #0078d4 = blue (info)
            channel : Target Slack channel

        Returns:
            dict : Rich Slack block payload
        """
        payload = {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": title,
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": body
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "🤖 Sent by *Agentic AI Workflow System*"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        if channel:
            payload["channel"] = channel

        return payload

    # ---------------------------
    # SEND SIMPLE MESSAGE
    # ---------------------------
    def send_message(
        self,
        text: str,
        channel: Optional[str] = None
    ) -> dict:
        """
        Sends a simple text message to Slack.

        Args:
            text    : Message content
            channel : Channel name (e.g. "#general")
                      Uses default channel if not provided

        Returns:
            dict : {
                "status"  : "sent" | "dry_run" | "failed",
                "channel" : target channel,
                "message" : status description
            }

        Usage:
            result = tool.send_message(
                text="✅ Task list created for Q2 Planning!",
                channel="#project-updates"
            )
        """
        target_channel = channel or self.default_channel

        # Dry run mode
        if not self._is_live():
            logger.info(
                f"[SlackTool] DRY RUN — Would send to {target_channel}: "
                f"{text[:80]}..."
            )
            return {
                "status": "dry_run",
                "channel": target_channel,
                "message": "Message not sent (no credentials). Dry run mode."
            }

        payload = self._build_payload(text, target_channel)

        return self._post_to_slack(payload, target_channel)

    # ---------------------------
    # SEND RICH NOTIFICATION
    # ---------------------------
    def send_notification(
        self,
        title: str,
        body: str,
        notification_type: str = "success",
        channel: Optional[str] = None
    ) -> dict:
        """
        Sends a rich formatted Slack notification.
        Used for task assignments and workflow completions.

        Args:
            title             : Notification header
            body              : Notification body (supports Slack markdown)
            notification_type : "success" | "error" | "warning" | "info"
            channel           : Target Slack channel

        Returns:
            dict : Status result dict

        Usage:
            result = tool.send_notification(
                title="🎯 New Tasks Assigned",
                body="*High Priority:*\n• Fix login bug — @dev-team\n• Review PR — @lead",
                notification_type="success",
                channel="#dev-team"
            )
        """
        target_channel = channel or self.default_channel

        # Map notification type to color
        color_map = {
            "success": "#36a64f",   # Green
            "error":   "#e01e5a",   # Red
            "warning": "#ecb22e",   # Yellow
            "info":    "#0078d4"    # Blue
        }
        color = color_map.get(notification_type, "#36a64f")

        # Dry run mode
        if not self._is_live():
            logger.info(
                f"[SlackTool] DRY RUN — Would send notification "
                f"'{title}' to {target_channel}"
            )
            return {
                "status": "dry_run",
                "channel": target_channel,
                "message": f"Notification '{title}' not sent (dry run mode)."
            }

        payload = self._build_block_payload(title, body, color, target_channel)

        return self._post_to_slack(payload, target_channel)

    # ---------------------------
    # SEND TASK SUMMARY
    # ---------------------------
    def send_task_summary(
        self,
        tasks: list,
        project_name: str = "Project",
        channel: Optional[str] = None
    ) -> dict:
        """
        Sends a formatted task summary to Slack.
        Specifically designed for TaskAgent output.

        Args:
            tasks        : List of task dicts with keys:
                           name, priority, owner, deadline
            project_name : Name of the project
            channel      : Target Slack channel

        Returns:
            dict : Status result dict

        Usage:
            result = tool.send_task_summary(
                tasks=[
                    {"name": "Fix bug", "priority": "High",
                     "owner": "@dev", "deadline": "Tomorrow"},
                    {"name": "Write docs", "priority": "Low",
                     "owner": "@writer", "deadline": "Next week"}
                ],
                project_name="Q2 Launch",
                channel="#project-updates"
            )
        """
        # Build formatted task list
        task_lines = []
        for i, task in enumerate(tasks, 1):
            priority_emoji = {
                "High": "🔴", "Medium": "🟡", "Low": "🟢"
            }.get(task.get("priority", "Medium"), "🟡")

            line = (
                f"{priority_emoji} *{i}. {task.get('name', 'Task')}*\n"
                f"   Owner: {task.get('owner', 'TBD')} | "
                f"Deadline: {task.get('deadline', 'TBD')}"
            )
            task_lines.append(line)

        body = "\n\n".join(task_lines)

        return self.send_notification(
            title=f"📋 Task Summary — {project_name}",
            body=body,
            notification_type="info",
            channel=channel
        )

    # ---------------------------
    # POST TO SLACK (Internal)
    # ---------------------------
    def _post_to_slack(self, payload: dict, channel: str) -> dict:
        """
        Internal method that actually sends the HTTP request to Slack.

        Args:
            payload : Slack API payload dict
            channel : Target channel (for logging)

        Returns:
            dict : Status result
        """
        try:
            # Use webhook if available
            if self.webhook_url:
                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                response.raise_for_status()

            # Use bot token as fallback
            elif self.bot_token:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.bot_token}"
                }
                response = requests.post(
                    self.SLACK_API_URL,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()

            logger.info(f"[SlackTool] Message sent to: {channel}")
            return {
                "status": "sent",
                "channel": channel,
                "message": f"Message sent to {channel} successfully."
            }

        except requests.exceptions.Timeout:
            error = "Slack request timed out after 10 seconds."
            logger.error(f"[SlackTool] {error}")
            return {"status": "failed", "channel": channel, "message": error}

        except requests.exceptions.RequestException as e:
            error = f"Slack request failed: {str(e)}"
            logger.error(f"[SlackTool] {error}")
            return {"status": "failed", "channel": channel, "message": error}

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self) -> str:
        mode = "live" if self._is_live() else "dry_run"
        return f"SlackTool(channel={self.default_channel}, mode={mode})"