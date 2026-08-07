from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL=os.getenv("BASE_URL")
EMAIL=os.getenv("EMAIL")
PASSWORD=os.getenv("PASSWORD")
BROWSER=os.getenv("BROWSER")
HEADLESS=os.getenv("HEADLESS")