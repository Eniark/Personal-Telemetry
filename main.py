from dotenv import load_dotenv
import uvicorn
import os
from api import app
load_dotenv()

if __name__ == "__main__":
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    uvicorn.run(
        "main:app", host=HOST, port=PORT, reload=True
    )