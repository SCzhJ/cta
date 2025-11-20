from pathlib import Path
from datetime import datetime

def verify_path(path: Path) -> None:
    """Verify if a path exists, if not, create it."""
    if not path.exists():
        path.mkdir(parents=True)

def get_date_str() -> str:
    """Get current date string in format YYYY-MM-DD."""
    return datetime.now().strftime('%Y-%m-%d')