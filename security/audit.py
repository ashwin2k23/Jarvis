import os
import datetime
from pathlib import Path

class SecurityAuditLogger:
    """Logs system actions, automation events, and command execution for security & audit trails."""
    
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = Path(os.path.expanduser("~")) / ".jarvis_ai" / "logs"
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "security_audit.log"

    def log_event(self, category: str, action: str, details: str = "", status: str = "SUCCESS"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{category.upper()}] [{status.upper()}] {action} - {details}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"[SecurityAudit] Failed to write log: {e}")

    def verify_action_permission(self, category: str, action: str, safe_mode: bool = True) -> tuple[bool, str]:
        """Validates whether an action requires explicit user confirmation."""
        HIGH_RISK_KEYWORDS = ["delete", "remove", "format", "shutdown", "restart", "kill", "rmdir"]
        
        action_lower = action.lower()
        if safe_mode and any(kw in action_lower for kw in HIGH_RISK_KEYWORDS):
            self.log_event(category, action, "Blocked pending confirmation", status="REQUIRES_APPROVAL")
            return False, f"Action '{action}' involves a high-risk operation and requires confirmation."
        
        self.log_event(category, action, "Permission granted", status="ALLOWED")
        return True, "Allowed"
