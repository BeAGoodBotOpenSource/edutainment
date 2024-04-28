import os

import openai
from dotenv import load_dotenv

load_dotenv()
debug_status = os.getenv("DEBUG") == "TRUE"
openai.api_key = os.getenv("OPENAI_API_KEY")

whitelist_origins = (
    [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://35.160.120.126",
        "http://44.233.151.27",
        "https://edutainment.onrender.com",
        "http://34.211.200.85",
    ]
    if debug_status
    else [
        "https://edutainment.onrender.com",
    ]
)

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_PROD_USERNAME')}:{os.getenv('DB_PROD_PASSWORD')}"
        f"@{os.getenv('DB_PROD_HOSTNAME')}/{os.getenv('DB_PROD_DB_NAME')}"
    )
