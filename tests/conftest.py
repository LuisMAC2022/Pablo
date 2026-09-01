import os


os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-with-at-least-32-characters",
)
os.environ.setdefault("VISITANTES_SHEET_ID", "test-sheet")
os.environ.setdefault("PASSWORD_TEMPORAL_BIOLOGOS", "test-password")
os.environ.setdefault(
    "GOOGLE_CREDENTIALS_PATH",
    "/tmp/nonexistent-test-credentials.json",
)
