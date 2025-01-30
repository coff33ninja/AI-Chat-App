import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging
import shutil

logger = logging.getLogger("main.history")


class ChatHistory:
    def __init__(self, storage_dir: str = "chat_history/chat_history"):
        self.storage_dir = storage_dir
        self.current_session = []
        self.session_name = None
        self.ensure_storage_exists()
        logger.info(f"Chat history initialized with storage at {storage_dir}")

    def ensure_storage_exists(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created chat history directory at {self.storage_dir}")

    def add_message(self, role: str, content: str):
        """Add a message to the current session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.current_session.append(message)
        logger.debug(f"Added message from {role}")

    def save_session(self, session_name: Optional[str] = None):
        """Save current session to file"""
        if not self.current_session or (len(self.current_session) == 1 and self.current_session[0]['content'].startswith("Welcome to")):
            logger.debug("No meaningful messages to save")
            return

        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            filename = os.path.join(self.storage_dir, f"chat_{session_name}.json")

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "session_name": session_name,
                        "messages": self.current_session,
                        "metadata": {
                            "created_at": datetime.now().isoformat(),
                            "message_count": len(self.current_session),
                            "last_modified": datetime.now().isoformat(),
                        },
                    },
                    f,
                    indent=2,
                )

            self.session_name = session_name
            logger.info(f"Saved session to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def load_session(self, session_name: str) -> bool:
        """Load a specific session"""
        filename = os.path.join(self.storage_dir, f"chat_{session_name}.json")

        if not os.path.exists(filename):
            logger.warning(f"Session file not found: {filename}")
            return False

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.current_session = data.get("messages", [])
                self.session_name = session_name
                logger.info(f"Loaded session from {filename}")
                return True
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False

    def list_sessions(self) -> List[Dict[str, str]]:
        """List all available chat sessions with metadata"""
        sessions = []
        for filename in os.listdir(self.storage_dir):
            if filename.startswith("chat_") and filename.endswith(".json"):
                try:
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append(
                            {
                                "name": data.get("session_name"),
                                "created_at": data.get("metadata", {}).get(
                                    "created_at"
                                ),
                                "message_count": data.get("metadata", {}).get(
                                    "message_count", 0
                                ),
                                "last_modified": data.get("metadata", {}).get(
                                    "last_modified"
                                ),
                            }
                        )
                except Exception as e:
                    logger.error(f"Error reading session file {filename}: {e}")

        return sorted(sessions, key=lambda x: x.get("last_modified", ""), reverse=True)

    def export_session(self, format: str = "txt") -> Optional[str]:
        """Export current session in various formats"""
        if not self.current_session:
            logger.warning("No messages to export")
            return None

        try:
            session_name = self.session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(self.storage_dir, "exports")
            os.makedirs(export_dir, exist_ok=True)

            if format == "txt":
                filename = os.path.join(export_dir, f"chat_{session_name}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    for msg in self.current_session:
                        f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")

            elif format == "markdown":
                filename = os.path.join(export_dir, f"chat_{session_name}.md")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# Chat Session: {session_name}\n\n")
                    for msg in self.current_session:
                        f.write(f"### {msg['role'].title()}\n")
                        f.write(f"{msg['content']}\n\n")

            elif format == "json":
                filename = os.path.join(export_dir, f"chat_{session_name}_export.json")
                shutil.copy2(
                    os.path.join(self.storage_dir, f"chat_{session_name}.json"),
                    filename,
                )

            else:
                logger.error(f"Unsupported export format: {format}")
                return None

            logger.info(f"Exported session to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return None

    def clear_session(self):
        """Clear the current session"""
        self.current_session = []
        self.session_name = None
        logger.info("Cleared current session")

    def delete_session(self, session_name: str) -> bool:
        """Delete a saved session"""
        try:
            filename = os.path.join(self.storage_dir, f"chat_{session_name}.json")
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"Deleted session {session_name}")
                return True
            else:
                logger.warning(f"Session {session_name} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def get_session_stats(self) -> Dict:
        """Get statistics about the current session"""
        if not self.current_session:
            return {
                "message_count": 0,
                "user_messages": 0,
                "ai_messages": 0,
                "average_message_length": 0,
            }

        user_messages = sum(1 for msg in self.current_session if msg["role"] == "user")
        ai_messages = sum(
            1 for msg in self.current_session if msg["role"] == "assistant"
        )
        total_length = sum(len(msg["content"]) for msg in self.current_session)

        return {
            "message_count": len(self.current_session),
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "average_message_length": total_length / len(self.current_session),
        }
