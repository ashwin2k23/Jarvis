import os
import subprocess
import webbrowser
import platform
import psutil
from pathlib import Path
from PIL import ImageGrab


class ComputerAutomation:
    """PC Control and OS Automation framework for Jarvis."""

    def __init__(self, security_logger=None):
        self.security_logger = security_logger
        self.os_name = platform.system().lower()

    def _resolve_app_path(self, clean_name: str):
        """Dynamically resolves app paths, Windows protocols, or Start Menu shortcuts."""
        import os
        import glob

        # 1. Windows Protocol URI Mappings (UWP / Modern Windows Apps)
        protocols = {
            "teams": "ms-teams:",
            "microsoft teams": "ms-teams:",
            "settings": "ms-settings:",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "spotify": "spotify:",
            "store": "ms-windows-store:",
        }
        if clean_name in protocols:
            return protocols[clean_name]

        # 2. Windows Start Menu Shortcut Scan
        start_dirs = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs")
        ]
        
        shortcut_matches = []
        for d in start_dirs:
            if os.path.exists(d):
                for lnk in glob.glob(d + "/**/*.lnk", recursive=True):
                    basename = os.path.basename(lnk).lower().replace(".lnk", "")
                    if clean_name in basename or basename in clean_name:
                        shortcut_matches.append(lnk)

        if shortcut_matches:
            shortcut_matches.sort(key=lambda x: len(os.path.basename(x)))
            return shortcut_matches[0]

        # 3. Known Common Installation Directory Paths
        prog_dirs = [
            os.path.expandvars(r"%ProgramFiles%"),
            os.path.expandvars(r"%ProgramFiles(x86)%"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%APPDATA%"),
        ]
        for pd in prog_dirs:
            if os.path.exists(pd):
                for exe in glob.glob(pd + f"/**/{clean_name}.exe", recursive=True):
                    return exe

        return None

    def launch_app(self, app_name: str) -> str:
        """Launches desktop applications by name, alias, protocol, or web app URL."""
        clean_name = app_name.lower().replace("browser", "").replace("app", "").strip(" .,!?:;")
        
        # 1. Dynamic Start Menu & Protocol Resolution
        resolved = self._resolve_app_path(clean_name)
        if resolved:
            try:
                if resolved.startswith("ms-") or resolved.endswith(":"):
                    os.system(f'start {resolved}')
                elif os.path.exists(resolved):
                    os.startfile(resolved)
                else:
                    os.system(f'start "" "{resolved}"')
                
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Launch App: {clean_name}")
                return f"✅ Launched **{clean_name.title()}**."
            except Exception as e:
                print(f"[OSControl] Resolved target launch notice: {e}")

        # 2. Check Web Services / Social Media Apps (Instagram, Facebook, LinkedIn, TikTok, WhatsApp, etc.)
        web_services = {
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "linkedin": "https://www.linkedin.com",
            "tiktok": "https://www.tiktok.com",
            "whatsapp": "https://web.whatsapp.com",
            "pinterest": "https://www.pinterest.com",
            "youtube": "https://www.youtube.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "netflix": "https://www.netflix.com",
            "reddit": "https://www.reddit.com",
            "amazon": "https://www.amazon.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "notion": "https://www.notion.so",
            "figma": "https://www.figma.com",
        }
        for w_key, w_url in web_services.items():
            if w_key in clean_name or clean_name in w_key:
                return self.open_website(w_url)

        # 3. Fallback App Map
        common_apps = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "brave": "brave.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe" if self.os_name == "windows" else "bash",
            "explorer": "explorer.exe",
            "paint": "mspaint.exe",
            "vscode": "code",
            "code": "code",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "task manager": "taskmgr.exe",
            "spotify": "spotify:",
            "discord": "discord.exe",
            "steam": "steam.exe",
            "vlc": "vlc.exe",
            "slack": "slack.exe",
            "zoom": "zoom.exe",
            "teams": "ms-teams:",
            "microsoft teams": "ms-teams:",
            "settings": "ms-settings:",
        }

        target = None
        for key, exe in common_apps.items():
            if key in clean_name or clean_name in key:
                target = exe
                break

        if not target:
            from utils.fuzzy_match import find_best_fuzzy_match
            fuzzy_key = find_best_fuzzy_match(clean_name, list(common_apps.keys()), threshold=0.60)
            if fuzzy_key:
                target = common_apps[fuzzy_key]
                clean_name = fuzzy_key

        if target:
            try:
                if self.os_name == "windows":
                    if target.startswith("ms-") or target.endswith(":"):
                        os.system(f'start {target}')
                    elif os.path.exists(target):
                        os.startfile(target)
                    else:
                        ret = os.system(f'start "" "{target}"')
                        if ret == 0:
                            return f"✅ Launched **{clean_name.title()}**."
                else:
                    subprocess.Popen([target])
                    return f"✅ Launched **{clean_name.title()}**."
            except Exception:
                pass

        # 4. Graceful Fallback: Open Web App / Search for unknown target
        search_url = f"https://www.google.com/search?q={clean_name.replace(' ', '+')}"
        return self.open_website(search_url)



    def close_app(self, app_name: str) -> str:
        """Terminates processes matching the app name with typo tolerance."""
        clean_name = app_name.lower().strip(" .,!?:;")
        
        common_process_names = {
            "chrome": "chrome",
            "google chrome": "chrome",
            "google": "chrome",
            "brave": "brave",
            "brave browser": "brave",
            "firefox": "firefox",
            "opera": "opera",
            "edge": "msedge",
            "microsoft edge": "msedge",
            "notepad": "notepad",
            "calc": "calculator",
            "calculator": "calculator",
            "vscode": "code",
            "code": "code",
            "vs code": "code",
            "spotify": "spotify",
            "discord": "discord",
            "steam": "steam",
            "vlc": "vlc",
            "slack": "slack",
            "zoom": "zoom",
            "obs": "obs64",
            "teams": "teams",
            "explorer": "explorer",
            "taskbar": "explorer",
        }
        
        proc_target = common_process_names.get(clean_name)
        if not proc_target:
            from utils.fuzzy_match import find_best_fuzzy_match
            fuzzy_key = find_best_fuzzy_match(clean_name, list(common_process_names.keys()), threshold=0.60)
            if fuzzy_key:
                proc_target = common_process_names[fuzzy_key]
                clean_name = fuzzy_key
            else:
                proc_target = clean_name
        killed_count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                pname = proc.info['name']
                if pname and proc_target in pname.lower():
                    proc.kill()
                    killed_count += 1
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Close App: {clean_name}", f"Killed {killed_count} instances")
            if killed_count > 0:
                return f"✅ Closed {killed_count} instance(s) of **{clean_name.title()}**."
            return f"⚠️ No running application found matching **{clean_name.title()}**."
        except Exception as e:
            return f"Error closing '{clean_name}': {e}"

    def open_website(self, url: str, browser: str = None) -> str:
        """Opens a website URL in the default system browser or a specified browser (e.g. Brave, Chrome, Firefox)."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        if browser:
            b_clean = browser.lower().strip()
            browser_map = {
                "brave": "brave.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "opera": "opera.exe"
            }
            exe = browser_map.get(b_clean, f"{b_clean}.exe")
            try:
                subprocess.Popen([exe, url])
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Open Website in {b_clean}: {url}")
                return f"✅ Opened in {b_clean.title()}: {url}"
            except Exception:
                pass

        try:
            webbrowser.open(url)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Open Website: {url}")
            return f"✅ Opened: {url}"
        except Exception as e:
            return f"Failed to open website: {e}"

    def play_local_video(self, folder_or_query: str = "") -> str:
        """
        Scans local folders (Telegram Desktop, Videos, Downloads, Desktop, or custom folder path)
        and plays a matching or available local video file.
        """
        import os
        import glob
        from pathlib import Path

        video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".ts"}
        user_home = Path(os.path.expanduser("~"))

        known_subfolders = {
            "telegram": user_home / "Downloads" / "Telegram Desktop",
            "telegram desktop": user_home / "Downloads" / "Telegram Desktop",
            "downloads": user_home / "Downloads",
            "videos": user_home / "Videos",
            "desktop": user_home / "Desktop",
            "documents": user_home / "Documents",
            "movies": user_home / "Videos",
        }

        search_dirs = []
        q_lower = folder_or_query.lower()

        # Check explicit folder path inside query
        import re
        path_match = re.search(r'([A-Za-z]:\\[^"\'\n]+|/[^"\'\n]+)', folder_or_query)
        if path_match and os.path.exists(path_match.group(1)):
            explicit_dir = Path(path_match.group(1))
            if explicit_dir.is_dir():
                search_dirs.append(explicit_dir)
            elif explicit_dir.is_file() and explicit_dir.suffix.lower() in video_extensions:
                os.startfile(str(explicit_dir))
                return f"🎬 Playing local video: **{explicit_dir.name}**"

        # Check keyword folder matches
        for k_alias, k_path in known_subfolders.items():
            if k_alias in q_lower and k_path.exists():
                if k_path not in search_dirs:
                    search_dirs.append(k_path)

        if not search_dirs:
            tg_path = user_home / "Downloads" / "Telegram Desktop"
            if tg_path.exists():
                search_dirs.append(tg_path)
            search_dirs.extend([
                user_home / "Videos",
                user_home / "Downloads",
                user_home / "Desktop",
                user_home / "Documents"
            ])

        found_videos = []
        for d in search_dirs:
            if d.exists() and d.is_dir():
                try:
                    for root, _, files in os.walk(str(d)):
                        for f in files:
                            ext = os.path.splitext(f)[1].lower()
                            if ext in video_extensions:
                                found_videos.append(Path(root) / f)
                                if len(found_videos) >= 50:
                                    break
                        if len(found_videos) >= 50:
                            break
                except Exception as e:
                    print(f"[OSControl] Video search notice: {e}")

        if not found_videos:
            return "⚠️ No video files (.mp4, .mkv, .avi, .mov) found in Telegram Desktop, Videos, or Downloads."

        target_video = found_videos[0]
        ignore_words = ["play", "any", "video", "present", "in", "the", "telegram", "desktop", "folder", "from", "my", "lap", "laptop", "some", "a"]
        query_words = [w for w in q_lower.split() if w not in ignore_words and len(w) > 2]

        if query_words:
            for v in found_videos:
                v_name = v.name.lower()
                if any(qw in v_name for qw in query_words):
                    target_video = v
                    break

        try:
            os.startfile(str(target_video))
            return f"🎬 Playing local video: **{target_video.name}** from `{target_video.parent}`"
        except Exception as e:
            return f"Failed to play video '{target_video.name}': {e}"



    def take_screenshot(self, save_dir: str = None) -> str:
        """Captures a screenshot of the main monitor."""
        try:
            if save_dir is None:
                save_dir = Path(os.path.expanduser("~")) / "Pictures" / "Jarvis_Screenshots"
            else:
                save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"screenshot_{os.urandom(4).hex()}.png"
            filepath = save_dir / filename
            
            img = ImageGrab.grab()
            img.save(filepath)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Take Screenshot", str(filepath))
            return f"📸 Screenshot saved to: `{filepath}`"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def get_clipboard_text(self) -> str:
        """Reads plain text content from the system clipboard."""
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            return clipboard.text()
        except Exception:
            return "Unable to access clipboard."

    def control_volume(self, action: str, level: int = None) -> str:
        """Controls Windows master audio volume."""
        if self.os_name != "windows":
            return "Volume control is currently optimized for Windows OS."
            
        action = action.lower().strip()
        try:
            if action in ["mute", "unmute", "toggle_mute"]:
                subprocess.run(['powershell', '-Command', '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'], capture_output=True)
                msg = "🔇 Muted." if action == "mute" else ("🔊 Unmuted." if action == "unmute" else "🔊 Toggled mute.")
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Audio Control: {action}")
                return msg
                
            elif action in ["decrease", "down", "lower", "quieter", "turn down"]:
                steps = max(1, min(50, int((level if level is not None else 10) / 2)))
                ps_cmd = f"1..{steps} | ForEach-Object {{ (New-Object -ComObject WScript.Shell).SendKeys([char]174) }}"
                subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
                amount_str = f"by {level}%" if level is not None else ""
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Audio Control: Volume Decreased {amount_str}")
                return f"🔉 Volume decreased {amount_str}.".strip()
                
            elif action in ["increase", "up", "raise", "louder", "turn up"]:
                steps = max(1, min(50, int((level if level is not None else 10) / 2)))
                ps_cmd = f"1..{steps} | ForEach-Object {{ (New-Object -ComObject WScript.Shell).SendKeys([char]175) }}"
                subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
                amount_str = f"by {level}%" if level is not None else ""
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Audio Control: Volume Increased {amount_str}")
                return f"🔊 Volume increased {amount_str}.".strip()
                
            elif action in ["set", "level"] and level is not None:
                up_count = max(0, min(50, int(level / 2)))
                ps_cmd = f"1..50 | ForEach-Object {{ (New-Object -ComObject WScript.Shell).SendKeys([char]174) }}; 1..{up_count} | ForEach-Object {{ (New-Object -ComObject WScript.Shell).SendKeys([char]175) }}"
                subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Audio Control: Volume Set to {level}%")
                return f"🔊 Volume set to {level}%."
            else:
                subprocess.run(['powershell', '-Command', '1..5 | ForEach-Object { (New-Object -ComObject WScript.Shell).SendKeys([char]174) }'], capture_output=True)
                return "🔉 Volume decreased."
        except Exception as e:
            return f"Failed to adjust volume: {e}"

    def set_volume(self, level: int) -> str:
        """Legacy helper for setting volume."""
        return self.control_volume("set", level=level)

    def execute_terminal_command(self, command: str) -> str:
        """Safely executes a shell/cmd command with output capture."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            output = result.stdout if result.stdout else result.stderr
            if self.security_logger:
                self.security_logger.log_event("TERMINAL", f"Executed command: {command}")
            return output.strip() if output else "Command executed with no output."
        except subprocess.TimeoutExpired:
            return "Command execution timed out (15s limit)."
        except Exception as e:
            return f"Execution error: {e}"

    # ================================================================
    # Phase 2: Extended OS Automation
    # ================================================================

    def shutdown_pc(self) -> str:
        """Shuts down the PC after a 10-second delay (cancellable with 'shutdown /a')."""
        try:
            subprocess.run(['shutdown', '/s', '/t', '10'], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Shutdown PC initiated")
            return "🔴 PC will shut down in **10 seconds**. Type `shutdown /a` in CMD to cancel."
        except Exception as e:
            return f"Shutdown failed: {e}"

    def restart_pc(self) -> str:
        """Restarts the PC after a 10-second delay."""
        try:
            subprocess.run(['shutdown', '/r', '/t', '10'], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Restart PC initiated")
            return "🔄 PC will **restart** in 10 seconds. Type `shutdown /a` in CMD to cancel."
        except Exception as e:
            return f"Restart failed: {e}"

    def lock_screen(self) -> str:
        """Locks the Windows screen immediately."""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Screen Locked")
            return "🔒 Screen locked."
        except Exception as e:
            return f"Lock screen failed: {e}"

    def sleep_pc(self) -> str:
        """Puts the PC to sleep."""
        try:
            subprocess.run(['powershell', '-Command', 'Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)'], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "PC Sleep initiated")
            return "💤 Putting PC to sleep..."
        except Exception as e:
            return f"Sleep failed: {e}"

    def empty_recycle_bin(self) -> str:
        """Empties the Windows Recycle Bin."""
        try:
            subprocess.run(['powershell', '-Command', 'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Recycle Bin Emptied")
            return "🗑️ Recycle Bin emptied successfully."
        except Exception as e:
            return f"Failed to empty Recycle Bin: {e}"

    def open_downloads(self) -> str:
        """Opens the user's Downloads folder."""
        try:
            downloads = Path(os.path.expanduser("~")) / "Downloads"
            os.startfile(str(downloads))
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", "Opened Downloads folder")
            return f"📂 Opened Downloads folder: `{downloads}`"
        except Exception as e:
            return f"Failed to open Downloads: {e}"

    def open_folder(self, path: str) -> str:
        """Opens a folder in File Explorer."""
        try:
            folder = Path(os.path.expanduser(path))
            if folder.exists():
                os.startfile(str(folder))
                return f"📂 Opened folder: `{folder}`"
            else:
                return f"⚠️ Folder not found: {path}"
        except Exception as e:
            return f"Failed to open folder: {e}"

    def set_brightness(self, level: int) -> str:
        """Sets screen brightness (0–100) via PowerShell WMI."""
        level = max(0, min(100, level))
        try:
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                if self.security_logger:
                    self.security_logger.log_event("AUTOMATION", f"Brightness set to {level}%")
                return f"☀️ Brightness set to **{level}%**."
            else:
                return f"⚠️ Brightness adjustment may not be supported on desktop monitors (WMI method unavailable)."
        except Exception as e:
            return f"Brightness control failed: {e}"

    def toggle_night_light(self) -> str:
        """Toggles Windows Night Light (blue light filter) via registry."""
        try:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate\windows.data.bluelightreduction.bluelightreductionstate"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                data, _ = winreg.QueryValueEx(key, "Data")
                # Byte 18 controls night light: 0x13 = on, 0x10 = off
                data_list = list(data)
                if len(data_list) > 18:
                    is_on = data_list[18] == 0x13
                    data_list[18] = 0x10 if is_on else 0x13
                    winreg.SetValueEx(key, "Data", 0, winreg.REG_BINARY, bytes(data_list))
                    winreg.CloseKey(key)
                    state = "OFF" if is_on else "ON"
                    return f"🌙 Night Light toggled **{state}**."
            except Exception:
                winreg.CloseKey(key) if 'key' in dir() else None
        except ImportError:
            pass
        # Fallback: open Night Light settings
        try:
            subprocess.run(['powershell', '-Command', 'Start-Process ms-settings:nightlight'], capture_output=True)
            return "🌙 Opened Night Light settings (toggle it manually)."
        except Exception as e:
            return f"Night Light control failed: {e}"

    def toggle_wifi(self, enable: bool = None) -> str:
        """Enables or disables Wi-Fi via netsh. Toggle if enable=None."""
        try:
            # Get current status first
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True)
            output = result.stdout.lower()
            wifi_connected = "wi-fi" in output or "wireless" in output

            if enable is None:
                enable = not wifi_connected  # Toggle

            action = "enable" if enable else "disable"
            subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', action], capture_output=True)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Wi-Fi {action}d")
            emoji = "📶" if enable else "📵"
            return f"{emoji} Wi-Fi **{'enabled' if enable else 'disabled'}**."
        except Exception as e:
            return f"Wi-Fi control failed: {e}"

    def toggle_bluetooth(self, enable: bool = None) -> str:
        """Enables or disables Bluetooth via PowerShell DeviceManagement."""
        try:
            # Use Windows Radio Management API via PowerShell
            check_cmd = "Get-PnpDevice -Class Bluetooth -Status OK | Select-Object -First 1 Status"
            result = subprocess.run(['powershell', '-Command', check_cmd], capture_output=True, text=True)
            currently_on = "OK" in result.stdout

            if enable is None:
                enable = not currently_on  # Toggle

            if enable:
                ps_cmd = "Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false"
            else:
                ps_cmd = "Get-PnpDevice -Class Bluetooth | Disable-PnpDevice -Confirm:$false"

            subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, timeout=10)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Bluetooth {'enabled' if enable else 'disabled'}")
            emoji = "🔵" if enable else "⚫"
            return f"{emoji} Bluetooth **{'enabled' if enable else 'disabled'}**."
        except Exception as e:
            # Fallback: open Bluetooth settings
            subprocess.run(['powershell', '-Command', 'Start-Process ms-settings:bluetooth'], capture_output=True)
            return "🔵 Opened Bluetooth settings (toggle manually)."

    def switch_monitor_mode(self, mode: str = None) -> str:
        """
        Switches display mode using DisplaySwitch.exe.
        Modes: internal, external, extend, clone (duplicate)
        """
        valid_modes = {
            "internal": "/internal",
            "external": "/external",
            "extend": "/extend",
            "extended": "/extend",
            "clone": "/clone",
            "duplicate": "/clone",
            "mirror": "/clone",
            "second": "/external",
        }
        if mode:
            flag = valid_modes.get(mode.lower(), "/extend")
        else:
            flag = "/extend"  # Default to extend

        try:
            subprocess.Popen(['DisplaySwitch.exe', flag])
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Monitor mode: {flag}")
            mode_name = flag.replace("/", "").title()
            return f"🖥️ Switched display to **{mode_name}** mode."
        except Exception as e:
            return f"Monitor switch failed: {e}"

    def record_screen(self, duration_seconds: int = 30, save_dir: str = None) -> str:
        """Records the screen for a given duration using ffmpeg (if available)."""
        try:
            if save_dir is None:
                save_dir = Path(os.path.expanduser("~")) / "Videos" / "Jarvis_Recordings"
            else:
                save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)

            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = save_dir / f"recording_{timestamp}.mp4"

            duration_seconds = min(duration_seconds, 300)  # Cap at 5 minutes

            # Try ffmpeg (must be in PATH)
            cmd = [
                'ffmpeg', '-y',
                '-f', 'gdigrab',
                '-framerate', '15',
                '-i', 'desktop',
                '-t', str(duration_seconds),
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]
            subprocess.Popen(cmd)
            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Screen recording started: {output_path}")
            return (f"🎥 Screen recording started ({duration_seconds}s).\n"
                    f"Saving to: `{output_path}`\n"
                    f"Requires **ffmpeg** installed in PATH.")
        except FileNotFoundError:
            return ("⚠️ Screen recording requires **ffmpeg** installed.\n"
                    "Download from: https://ffmpeg.org/download.html")
        except Exception as e:
            return f"Screen recording failed: {e}"

    def get_system_info(self) -> str:
        """Returns comprehensive system information."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            net = psutil.net_io_counters()

            batt_str = (f"{battery.percent:.0f}% ({'⚡ Plugged in' if battery.power_plugged else '🔋 Discharging'})"
                       if battery else "N/A (Desktop)")

            sent_gb = round(net.bytes_sent / (1024**3), 2)
            recv_gb = round(net.bytes_recv / (1024**3), 2)

            return (
                "### 💻 System Status\n"
                f"• **CPU**: {cpu}% ({cpu_count} cores)\n"
                f"• **RAM**: {ram.percent}% used ({round(ram.used/(1024**3),1)} / {round(ram.total/(1024**3),1)} GB)\n"
                f"• **Disk**: {disk.percent}% used ({round(disk.free/(1024**3),1)} GB free)\n"
                f"• **Battery**: {batt_str}\n"
                f"• **Network**: ↑ {sent_gb} GB sent | ↓ {recv_gb} GB received"
            )
        except Exception as e:
            return f"System info error: {e}"

    def organize_directory(self, folder_path: str = None) -> str:
        """Organizes a folder into Images, Documents, Executables, Archives, Videos, Audio, and Code."""
        try:
            if not folder_path:
                target_dir = Path(os.path.expanduser("~")) / "Downloads"
            else:
                target_dir = Path(folder_path)

            if not target_dir.exists():
                return f"⚠️ Directory not found: `{target_dir}`"

            categories = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
                "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".epub"],
                "Executables": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
                "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                "Code": [".py", ".js", ".html", ".css", ".json", ".cpp", ".java", ".ts"]
            }

            moved_count = 0
            for item in target_dir.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    ext = item.suffix.lower()
                    for category, extensions in categories.items():
                        if ext in extensions:
                            dest_folder = target_dir / category
                            dest_folder.mkdir(exist_ok=True)
                            try:
                                item.rename(dest_folder / item.name)
                                moved_count += 1
                            except Exception:
                                pass
                            break

            if self.security_logger:
                self.security_logger.log_event("AUTOMATION", f"Organized directory: {target_dir}", f"Moved {moved_count} files")

            return f"📁 **Organized Directory**: `{target_dir}`\nSuccessfully sorted **{moved_count}** files into subfolders."
        except Exception as e:
            return f"Error organizing directory: {e}"

    def apply_workspace_preset(self, preset_name: str) -> str:
        """Applies a named workspace preset (work, gaming, dev, focus)."""
        from automation.workspace_presets import WorkspacePresetManager
        manager = WorkspacePresetManager(computer_automation=self)
        return manager.apply_preset(preset_name)

    def git_workflow_command(self, action: str, branch: str = None, message: str = "Update via Jarvis", repo_path: str = ".") -> str:
        """Executes Git operations (status, checkout, commit, push, pull)."""
        try:
            repo = Path(repo_path).resolve()
            if not (repo / ".git").exists():
                return f"⚠️ No git repository found at `{repo}`."

            action = action.lower().strip()
            if action in ["status", "check status"]:
                cmd = "git status --short"
            elif action in ["checkout", "create branch", "branch"] and branch:
                cmd = f"git checkout -b {branch}" if "create" in action else f"git checkout {branch}"
            elif action in ["commit", "save", "commit all"]:
                cmd = f'git add . && git commit -m "{message}"'
            elif action in ["push"]:
                cmd = "git push"
            elif action in ["pull"]:
                cmd = "git pull"
            else:
                return f"⚠️ Unsupported git action: {action}"

            res = subprocess.run(cmd, shell=True, cwd=str(repo), capture_output=True, text=True)
            output = res.stdout.strip() or res.stderr.strip()
            return f"⚙️ **Git Action ({action})**:\n```\n{output}\n```"
        except Exception as e:
            return f"Git command failed: {e}"

