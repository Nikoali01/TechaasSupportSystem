import sys

from fastapi import FastAPI
from app.routes import router

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        sys.exit(0)
