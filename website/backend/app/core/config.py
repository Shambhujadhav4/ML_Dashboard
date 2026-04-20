from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


@dataclass(slots=True)
class Settings:
    app_name: str = "DataPilot API"
    api_prefix: str = "/api"
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv(
            "DATAPILOT_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
    )


settings = Settings()
