import os
from dotenv import load_dotenv
from typing import NoReturn

def setup_openai_config() -> None:
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not os.getenv('OPENAI_ORG_ID'):
        raise ValueError("OPENAI_ORG_ID not found in environment variables")

def setup_app_config() -> None:
    load_dotenv()
    setup_openai_config()