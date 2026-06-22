from __future__ import annotations

import os


DB_PATH = os.getenv("DB_PATH", "data/hub.db")
KEY_FILE = os.getenv("KEY_FILE", "data/hub.key")
