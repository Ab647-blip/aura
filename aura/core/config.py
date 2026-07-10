import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


class MissingAPIKeyError(Exception):
    def __init__(self):
        super().__init__(
            "\n" + "=" * 60 + "\n"
            "GOOGLE_API_KEY not found in environment variables!\n"
        )


class ConfigurationError(Exception):
    def __init__(self, message: str):
        super().__init__(f"\nConfiguration Error: {message}\n")


def get_api_key() -> str:
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise MissingAPIKeyError()
    
    if api_key == "your-gemini-api-key-here":
        raise MissingAPIKeyError()
    
    api_key = api_key.strip()
    return api_key


def get_config() -> Dict[str, Any]:
    return {
        "api_key": get_api_key(),
        "model": os.getenv("AURA_MODEL", "gemini-2.5-pro-exp-03-25"),
        "max_tokens": int(os.getenv("AURA_MAX_TOKENS", 1024)),
        "context_budget": int(os.getenv("AURA_CONTEXT_BUDGET", 6000)),
        "project_root": str(Path(__file__).parent.parent.parent),
        "output_dir": str(Path(__file__).parent.parent.parent / "output"),
    }


def validate_config() -> bool:
    try:
        config = get_config()
        
        model = config['model']
        if not model or not isinstance(model, str):
            raise ConfigurationError(f"Invalid model name: {model}")
        
        max_tokens = config['max_tokens']
        if max_tokens < 1 or max_tokens > 100000:
            raise ConfigurationError(f"Invalid max_tokens: {max_tokens}")
        
        context_budget = config['context_budget']
        if context_budget < 1:
            raise ConfigurationError(f"Invalid context_budget: {context_budget}")
        
        return True
        
    except MissingAPIKeyError:
        raise
    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed: {str(e)}")


try:
    _config = get_config()
    API_KEY = _config['api_key']
    MODEL = _config['model']
    MAX_TOKENS = _config['max_tokens']
    CONTEXT_BUDGET = _config['context_budget']
    PROJECT_ROOT = _config['project_root']
    OUTPUT_DIR = _config['output_dir']
except MissingAPIKeyError:
    API_KEY = None
    MODEL = "gemini-2.5-pro-exp-03-25"
    MAX_TOKENS = 1024
    CONTEXT_BUDGET = 6000
    PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
    OUTPUT_DIR = str(Path(__file__).parent.parent.parent / "output")