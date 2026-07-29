import psutil
import datetime
from typing import Dict, List, Type
from tools.base_tool import BaseTool

class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluates mathematical expressions safely (e.g. 15 * 4 + 100)."

    def execute(self, params: Dict[str, str]) -> str:
        expr = params.get("expression", "").strip()
        if not expr:
            return "Error: No mathematical expression provided."
        try:
            # Safe restricted eval for numbers and standard math operations
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expr):
                return "Error: Expression contains invalid characters."
            result = eval(expr, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {e}"


class SystemMonitorTool(BaseTool):
    @property
    def name(self) -> str:
        return "system_monitor"

    @property
    def description(self) -> str:
        return "Displays real-time hardware status including CPU usage, RAM memory, and disk usage."

    def execute(self, params: Dict[str, str]) -> str:
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            
            batt_str = f"{battery.percent}% ({'Plugged in' if battery.power_plugged else 'Discharging'})" if battery else "N/A"
            
            return (
                "### System Hardware Status\n"
                f"• **CPU Utilization**: {cpu}%\n"
                f"• **RAM Memory**: {ram.percent}% used ({round(ram.used/(1024**3), 2)} GB / {round(ram.total/(1024**3), 2)} GB)\n"
                f"• **Storage Disk**: {disk.percent}% used ({round(disk.used/(1024**3), 2)} GB free)\n"
                f"• **Battery Status**: {batt_str}"
            )
        except Exception as e:
            return f"System monitor error: {e}"


class ToolRegistry:
    """Registry that dynamically manages and routes tool calls."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Register default built-in tools
        self.register(CalculatorTool())
        self.register(SystemMonitorTool())
        try:
            from tools.web_agent import WebNavigatorAgentTool
            self.register(WebNavigatorAgentTool())
        except Exception as e:
            print(f"[ToolRegistry Notice] WebNavigatorAgentTool notice: {e}")

    def register(self, tool: BaseTool):
        self._tools[tool.name.lower()] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name.lower())

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def execute_tool(self, tool_name: str, params: Dict[str, str]) -> str:
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Tool '{tool_name}' is not registered."
        return tool.execute(params)

