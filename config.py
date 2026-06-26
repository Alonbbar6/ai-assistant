import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"

CREDENTIALS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

GOOGLE_CLIENT_SECRETS_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRETS_FILE",
    str(CREDENTIALS_DIR / "google_credentials.json")
)
GOOGLE_TOKEN_FILE = str(CREDENTIALS_DIR / "google_token.json")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

EMAIL_FROM = os.getenv("EMAIL_FROM", "")

VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "en-US")
VOICE_RATE = int(os.getenv("VOICE_RATE", "175"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

SEARCH_ROOTS = [
    str(Path.home() / "Documents"),
    str(Path.home() / "Desktop"),
    str(Path.home() / "Downloads"),
]
SEARCH_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".py", ".js", ".ts", ".csv", ".json"}
