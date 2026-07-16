from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import database
from routes import router

# 1. Initialize the SQLite database on startup
database.init_db()

# 2. Spin up the Core FastAPI Server
app = FastAPI()

# 3. Add the secure cookie middleware
app.add_middleware(SessionMiddleware, secret_key="super-secret-random-string")

# 4. Plug in all the web routes from routes.py
app.include_router(router)