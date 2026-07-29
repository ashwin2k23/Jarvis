"""
proactive/monitor.py — Phase 10: Proactive Intelligence
Background QThread that monitors system state and fires alerts:
- Low battery warnings
- High CPU temperature/usage alerts
- Due reminder notifications
- Daily briefings at 9:00 AM
- GitHub notification pings (if skill configured)
"""
import datetime
import psutil
from PySide6.QtCore import QThread, Signal


class ProactiveMonitor(QThread):
    """
    Background monitor that periodically checks system health and user reminders,
    emitting signals for the UI to display as proactive alerts.
    """

    # Emitted with (alert_type, title, message)
    alert_fired = Signal(str, str, str)
    # Emitted with a daily briefing string
    daily_briefing = Signal(str)

    CHECK_INTERVAL_MS = 60_000  # Check every 60 seconds

    def __init__(self, core=None, parent=None):
        super().__init__(parent)
        self.core = core
        self._running = True
        self._high_cpu_count = 0
        self._briefing_sent_today = None

    def set_core(self, core):
        self.core = core

    def stop(self):
        """Signals the thread to stop cleanly."""
        self._running = False
        self.quit()

    def run(self):
        """Main monitoring loop — runs every 60 seconds."""
        while self._running:
            try:
                self._check_battery()
                self._check_cpu()
                self._check_reminders()
                self._check_daily_briefing()
            except Exception:
                pass
            # Sleep in 1-second increments to allow clean stop
            for _ in range(self.CHECK_INTERVAL_MS // 1000):
                if not self._running:
                    return
                self.msleep(1000)

    # ------------------------------------------------------------------
    # Battery Monitor
    # ------------------------------------------------------------------

    def _check_battery(self):
        """Alerts if battery drops below 20% and is discharging."""
        try:
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged:
                pct = battery.percent
                if pct <= 10:
                    self.alert_fired.emit(
                        "battery_critical",
                        "🔋 Critical Battery",
                        f"Battery is at {pct:.0f}%! Connect your charger immediately."
                    )
                elif pct <= 20:
                    self.alert_fired.emit(
                        "battery_low",
                        "🔋 Low Battery Warning",
                        f"Battery is at {pct:.0f}%. Consider plugging in soon."
                    )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # CPU Monitor
    # ------------------------------------------------------------------

    def _check_cpu(self):
        """Alerts if CPU usage stays above 90% for multiple consecutive checks."""
        try:
            cpu_pct = psutil.cpu_percent(interval=0.5)
            if cpu_pct > 90:
                self._high_cpu_count += 1
                if self._high_cpu_count >= 3:  # 3 consecutive minutes
                    self._high_cpu_count = 0
                    ram = psutil.virtual_memory()
                    self.alert_fired.emit(
                        "high_cpu",
                        "⚡ High System Load",
                        f"CPU is at {cpu_pct:.0f}% and RAM at {ram.percent:.0f}%. "
                        f"Consider closing unused applications."
                    )
            else:
                self._high_cpu_count = max(0, self._high_cpu_count - 1)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Reminder Check
    # ------------------------------------------------------------------

    def _check_reminders(self):
        """Checks for tasks/reminders due within the next hour."""
        if not self.core or not hasattr(self.core, 'db'):
            return
        try:
            now = datetime.datetime.now()
            tasks = self.core.db.get_tasks(status="pending")
            for task in tasks:
                due_str = task.get("due_date", "")
                if not due_str:
                    continue
                try:
                    # Parse common date formats
                    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y"]:
                        try:
                            due_dt = datetime.datetime.strptime(due_str, fmt)
                            break
                        except ValueError:
                            due_dt = None

                    if due_dt:
                        diff_minutes = (due_dt - now).total_seconds() / 60
                        if 0 <= diff_minutes <= 30:
                            self.alert_fired.emit(
                                "reminder",
                                "⏰ Upcoming Reminder",
                                f"Task due in {int(diff_minutes)} min: **{task['title']}**"
                            )
                except Exception:
                    continue
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Daily Briefing
    # ------------------------------------------------------------------

    def _check_daily_briefing(self):
        """Sends a morning briefing at 9:00 AM if not already sent today."""
        now = datetime.datetime.now()
        today = now.date()

        if self._briefing_sent_today == today:
            return

        if now.hour == 9 and now.minute < 2:  # Fire within first 2 min of 9 AM
            self._briefing_sent_today = today
            briefing = self._build_briefing(now)
            self.daily_briefing.emit(briefing)

    def _build_briefing(self, now: datetime.datetime) -> str:
        """Constructs the morning briefing text."""
        lines = [f"🌅 **Good morning! Here's your daily briefing for {now.strftime('%A, %B %d')}:**\n"]

        # Pending tasks
        if self.core and hasattr(self.core, 'db'):
            try:
                tasks = self.core.db.get_tasks(status="pending")
                if tasks:
                    lines.append(f"📋 **Tasks ({len(tasks)} pending):**")
                    for t in tasks[:5]:
                        due = f" — due {t['due_date']}" if t.get('due_date') else ""
                        lines.append(f"  • {t['title']}{due}")
                else:
                    lines.append("📋 No pending tasks — clean slate!")
            except Exception:
                pass

        # System health
        try:
            cpu = psutil.cpu_percent(interval=0.2)
            ram = psutil.virtual_memory()
            battery = psutil.sensors_battery()
            batt_str = f" | 🔋 Battery: {battery.percent:.0f}%" if battery else ""
            lines.append(f"\n💻 **System**: CPU {cpu:.0f}% | RAM {ram.percent:.0f}%{batt_str}")
        except Exception:
            pass

        # User name greeting
        if self.core and hasattr(self.core, 'config'):
            name = self.core.config.get("user_name", "Boss")
            lines.insert(0, f"Good morning, {name}! 👋\n")

        return "\n".join(lines)


class GhostCopilotMonitor(QThread):
    """
    Proactive Live Screen Monitor (Ghost Copilot).
    Periodically checks desktop screen for code errors, stack traces, or crash dialogs.
    """

    error_detected = Signal(str, str)  # Emits (title, suggestion)

    def __init__(self, core=None, interval_seconds: int = 30, parent=None):
        super().__init__(parent)
        self.core = core
        self.interval_seconds = interval_seconds
        self._running = True

    def stop(self):
        self._running = False
        self.quit()

    def run(self):
        while self._running:
            # Sleep step by step
            for _ in range(self.interval_seconds):
                if not self._running:
                    return
                self.msleep(1000)

            try:
                self._analyze_screen_for_errors()
            except Exception:
                pass

    def _analyze_screen_for_errors(self):
        if not self.core or not hasattr(self.core, 'screen_vision'):
            return

        # Perform screen OCR / vision analysis
        res = self.core.screen_vision.analyze_screen("Scan this screenshot specifically for software errors, exceptions, stack traces, or failure messages. If an error is found, return 'ERROR: [brief description] | FIX: [1 sentence fix]'. If no error is visible, return 'OK'.")
        
        if res and "ERROR:" in res:
            try:
                parts = res.split("ERROR:", 1)[1].split("| FIX:")
                err_desc = parts[0].strip()
                fix_desc = parts[1].strip() if len(parts) > 1 else "Check terminal output."
                self.error_detected.emit(f"⚠️ Error Detected: {err_desc[:40]}...", f"💡 **Suggested Fix**: {fix_desc}")
            except Exception:
                self.error_detected.emit("⚠️ Screen Error Detected", res[:150])

