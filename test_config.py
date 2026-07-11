import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aura.core.config import  MODEL,API_KEY, get_config, validate_config, MissingAPIKeyError
from aura.core.llm_client import call_llm, APIError


def main():
    print("=" * 60)
    print("Testing Aura Configuration (Gemini)")
    print("=" * 60)
    
    try:
        print(f"Model being used: {MODEL}")
        print("\nTest 1: Loading API Key")
        api_key = API_KEY
        print(f"API Key loaded: {api_key[:10]}...")
        print(f"Key length: {len(api_key)} characters")
        
        print("\nTest 2: Loading Full Configuration")
        config = get_config()
        for key, value in config.items():
            if key == 'api_key':
                print(f"{key}: {value[:10]}...")
            else:
                print(f"{key}: {value}")
        
        print("\nTest 3: Validating Configuration")
        if validate_config():
            print("Configuration validation passed!")
        
        print("\nTest 4: Testing Gemini Connection")
        print(f"Using model: {config['model']}")
        
        test_response = call_llm(
            messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
            max_tokens=20
        )
        print(f"Response: {test_response['text']}")
        print(f"Input tokens: {test_response['usage']['input_tokens']}")
        print(f"Output tokens: {test_response['usage']['output_tokens']}")
        
        print("\n" + "=" * 60)
        print("All tests passed! Gemini is ready.")
        print("=" * 60)
        return 0
        
    except MissingAPIKeyError as e:
        print(f"\n{e}")
        return 1
    except APIError as e:
        print(f"\nAPI Error: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())