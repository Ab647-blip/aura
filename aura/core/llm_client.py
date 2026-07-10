import google.generativeai as genai
from typing import List, Dict, Any
import time

from aura.core.config import API_KEY, MODEL, MAX_TOKENS


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(f"API Error {status_code}: {message}")
        self.status_code = status_code


class APIConnectionError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Connection Error: {message}")


def call_llm(
    messages: List[Dict[str, str]], 
    system: str = "", 
    model: str = MODEL,
    max_tokens: int = MAX_TOKENS
) -> Dict[str, Any]:
    
    genai.configure(api_key=API_KEY)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": max_tokens,
    }
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    model_instance = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction=system if system else None,
    )
    
    chat = model_instance.start_chat(history=[])
    
    for msg in messages:
        if msg["role"] == "user":
            try:
                chat.send_message(msg["content"])
            except Exception as e:
                pass
    
    user_message = messages[-1]["content"] if messages else ""
    
    try:
        response = chat.send_message(user_message)
        
        return {
            "text": response.text,
            "raw_response": response,
            "usage": {
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count,
            }
        }
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            raise APIError(429, "Rate limit exceeded. Wait a moment and try again.")
        elif "503" in error_str:
            raise APIError(503, "Service unavailable. Try again later.")
        elif "NOT_FOUND" in error_str:
            raise APIError(404, f"Model '{model}' not found. Check your model name.")
        elif "connection" in error_str.lower():
            raise APIConnectionError(str(e))
        else:
            raise