from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional


@dataclass
class SmtpConfig:
    server: str = 'localhost'
    port: int = 25
    username: Optional[str] = None
    password: Optional[str] = None


class SmtpConfigStore:
    """Persist SMTP configuration to a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.config = SmtpConfig()
        self.load()

    def load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.config = SmtpConfig(
                server=data.get('server', 'localhost'),
                port=data.get('port', 25),
                username=data.get('username'),
                password=data.get('password'),
            )

    def save(self) -> None:
        self.path.write_text(json.dumps(vars(self.config), indent=2))

    def update(self, config: SmtpConfig) -> None:
        self.config = config
        self.save()
