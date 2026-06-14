import re
import unicodedata


def slugify(text: str, max_len: int = 50) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].rstrip("-")


def make_filename(rank: int, view_count: int, description: str) -> str:
    slug = slugify(description) or "video"
    return f"Top_{rank:02d}_{view_count}_{slug}.mp4"
