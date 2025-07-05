import asyncio
import multiprocessing
import os

import uvicorn

from app.DatabaseLogic import database


def run_celery():
    os.system("celery -A app.celery_app worker --loglevel=info --pool=solo")


if __name__ == "__main__":
    celery_process = multiprocessing.Process(target=run_celery)
    celery_process.start()
    try:
        uvicorn.run("app.core:app", host="0.0.0.0", port=8000, reload=True)
    finally:
        celery_process.terminate()
        celery_process.join()
    celery_process = multiprocessing.Process(target=run_celery())
    celery_process.start()
    asyncio.run(database.create_database())
    uvicorn.run(app="app.core:app")
