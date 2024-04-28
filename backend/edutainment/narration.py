import logging
import os

import requests
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)

_ = load_dotenv(find_dotenv())

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
DEBUG = os.getenv("DEBUG")
CHUNK_SIZE = 1024

voice_id = "ThT5KcBeYPX3keUQqHPh" 

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVEN_LABS_API_KEY,
}


def get_narration(text: str, id: str) -> str:
    """Save an mp3 file with narration and return the filename."""
    
    # Replace spaces with underscores in the text
    sanitized_text = text.replace(' ', '_')[:30]
    
    # Prepend the id to the filename
    filename = f"narration/{id[:8]}_{sanitized_text}.mp3"

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        narration = response.content

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(response.content)

    else:
        raise requests.ConnectionError(
            f"Expected status code 200, but got {response.status_code}"
        )

    return filename


if __name__ == "__main__":
    get_narration("the quick brown fox jumped over the lazy dog")
