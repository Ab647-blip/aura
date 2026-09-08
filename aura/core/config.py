import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
OUTPUT_DIR = PROJECT_ROOT / "output"

load_dotenv(ENV_FILE)
class MissingAPIKeyError(Exception):
       "Raised when GOOGLE_API_KEY is missing."


class ConfigurationError(Exception):
      "Raised when configuration is invalid."

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise MissingAPIKeyError(
        "GOOGLE_API_KEY was not found.\n"
    )

MODEL = os.getenv("AURA_MODEL", "gemini-2.5-flash")

MAX_TOKENS = int(os.getenv("AURA_MAX_TOKENS", "1024"))

TEMPERATURE = float(os.getenv("AURA_TEMPERATURE", "0.7"))

TOP_P = float(os.getenv("AURA_TOP_P", "0.95"))

TOP_K = int(os.getenv("AURA_TOP_K", "40"))

CONTEXT_BUDGET = int(os.getenv("AURA_CONTEXT_BUDGET", "6000"))

EMBED_MODEL = os.getenv("AURA_EMBED_MODEL", "gemini-embedding-001")

DOCS_DIR = PROJECT_ROOT / "docs"
INDEX_PATH = PROJECT_ROOT / "store" / "index.json"
LOG_PATH = PROJECT_ROOT / "logs" / "decisions.jsonl"


def validate_config() -> bool:

    if not MODEL:
        raise ConfigurationError("Model name cannot be empty.")

    if MAX_TOKENS <= 0:
        raise ConfigurationError("MAX_TOKENS must be greater than zero.")

    if CONTEXT_BUDGET <= 0:
        raise ConfigurationError("CONTEXT_BUDGET must be greater than zero.")

    if not (0 <= TEMPERATURE <= 2):
        raise ConfigurationError("TEMPERATURE must be between 0 and 2.")

    if not (0 <= TOP_P <= 1):
        raise ConfigurationError("TOP_P must be between 0 and 1.")
    
    if TOP_K <= 0:
        raise ConfigurationError("TOP_K must be greater than zero.")

    return True


def get_config() -> dict[str, Any]:

    return {
        "api_key": API_KEY,
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "context_budget": CONTEXT_BUDGET,
        "project_root": str(PROJECT_ROOT),
        "output_dir": str(OUTPUT_DIR),
    }