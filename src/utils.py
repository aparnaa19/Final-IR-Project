# Utility functions - HTML parsing and text extraction helpers

from pathlib import Path
from bs4 import BeautifulSoup
import re
def read_clean_html(path: Path) -> str:  # Extract and clean text from HTML file, removing tags and normalizing whitespace
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "lxml")  
        for tag in soup.select("script, style, meta, link"):  # Remove non-content tags
            tag.decompose()
        text = soup.get_text(separator=" ")  # Extract text    
        text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
        return text
     
    except Exception as exc:
        print(f"[WARN] Failed to read {path}: {exc}")
        return ""

def ensure_directories(*paths):  # Extract and clean text from HTML file, removing tags and normalizing whitespace
    for path in paths:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory ready: {path}")