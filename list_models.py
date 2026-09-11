from google import genai
from aura.core.config import (
    API_KEY,
)

client = genai.Client(api_key=API_KEY)

for model in client.models.list():
    print(model.name)