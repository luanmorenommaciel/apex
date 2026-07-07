import os
from datetime import datetime
from zoneinfo import ZoneInfo

SAO_PAULO_TIMEZONE = ZoneInfo("America/Sao_Paulo")


class Colorize:
    styles = {
        "default": 0,
        "bold": 1,
        "dim": 2,
        "italic": 3,
        "underline": 4,
        "blink": 5,
    }

    colors = {
        "red": 31,
        "green": 32,
        "yellow": 33,
        "cyan": 36,
        "default": 39,
        "on_red": 41,
    }

    @classmethod
    def get_color(cls, text: str, color: str = "default", style: str = "default") -> str:
        style_code = cls.styles.get(style, cls.styles["default"])
        color_code = cls.colors.get(color, cls.colors["default"])
        return f"[{style_code};{color_code}m{text}[0m"


class Logger:
    levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

    def __init__(self, level: str = "INFO"):
        self.current_level = self.levels.index("INFO")
        self.set_level(level)

    def set_level(self, level: str) -> None:
        normalized = level.upper()
        if normalized not in self.levels:
            raise ValueError(f"Invalid log level '{level}'. Expected one of {self.levels}")
        self.current_level = self.levels.index(normalized)

    @staticmethod
    def _execute(message: str) -> str:
        timestamp = datetime.now().astimezone(SAO_PAULO_TIMEZONE).strftime("%m/%d %H:%M:%S")
        full_message = f"[{timestamp}] - {message}"
        print(full_message)
        return full_message

    def debug(self, message: str) -> str | None:
        if self.levels.index("DEBUG") <= self.current_level:
            return self._execute(f"{Colorize.get_color('[Debug]:', color='green', style='bold')} {message}")
        return None

    def info(self, message: str) -> str | None:
        if self.levels.index("INFO") <= self.current_level:
            return self._execute(f"{Colorize.get_color('[Info]:', color='cyan', style='bold')} {message}")
        return None

    def warning(self, message: str) -> str | None:
        if self.levels.index("WARNING") <= self.current_level:
            return self._execute(f"{Colorize.get_color('[Warning]:', color='yellow', style='bold')} {message}")
        return None

    def warn(self, message: str) -> str | None:
        return self.warning(message)

    def error(self, message: str) -> str | None:
        if self.levels.index("ERROR") <= self.current_level:
            return self._execute(f"{Colorize.get_color('[Error]:', color='red', style='blink')} {message}")
        return None

    def critical(self, message: str) -> str | None:
        if self.levels.index("CRITICAL") <= self.current_level:
            return self._execute(f"{Colorize.get_color('[Critical]:', color='on_red', style='blink')} {message}")
        return None


logger = Logger(level=os.environ.get("SPARK_PLAT_LOG_LEVEL", "INFO"))

__all__ = ["Logger", "logger"]
