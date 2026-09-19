'''
Markdown hash registry.

Keeps a set of unique hashes of the questions already saved as markdown files,
so the same question is not persisted twice. The set is persisted to a JSON
file next to this module so it survives across runs.
'''
import hashlib
import json
from pathlib import Path

# Registry of question hashes (in-memory set)
markdownhash: dict[str, str] = dict()

# Persistence file living beside this module
_HASH_FILE = Path(__file__).resolve().parent / "markdownhash.json"


def _load() -> None:
    """Load previously registered hashes from disk into the in-memory dict."""
    if _HASH_FILE.exists():
        try:
            data = json.loads(_HASH_FILE.read_text())
            if isinstance(data, dict):
                markdownhash.update(data)
            else:
                print("Data is not in the correct format")
                raise ValueError("Data is not in the correct format")
        except json.JSONDecodeError:
            pass


def _save() -> None:
    """Persist the in-memory hash dict to disk."""
    sorted_dict = {k: markdownhash[k] for k in sorted(markdownhash)}
    _HASH_FILE.write_text(json.dumps(sorted_dict, indent=2))


def question_hash(question: str) -> str:
    """Stable unique hash of the question (SHA-256, first 16 hex chars)."""
    return hashlib.sha256(question.strip().lower().encode()).hexdigest()[:16]


def register_question_hash(question: str,questionsummary: str) -> str:
    """Hash the question, add it to the markdownhash set, and persist.

    Returns the hash. Returns "" if the question hash was already registered
    (i.e. this question has been saved before).
    """
    _load()
    mdh = question_hash(question)

    if mdh in markdownhash:
        return ""

    markdownhash[mdh]=questionsummary    
    _save()
    
    return mdh
