import os
import sqlite3 
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# This looks for 'SESSION_KEY' on Render. 
# If it's not found (on your computer), it falls back to your old secret key so nothing breaks!
SECRET_KEY = os.getenv("SESSION_KEY", "super-secret-random-string")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")

# DATABASE 

def init_db():
    """Creates the database file and pre-loads your users if they don't exist."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    
    # Pre-populate your users (ryan and xindong) if the table is totally empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("ryan", "12345"))
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("xindong", "00000"))
        conn.commit()
        
    conn.close()

# Run the database setup immediately when the app starts
init_db()

# ==========================================
# ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    if "user" in request.session:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    # 1. Connect to the SQLite database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
                
    # 2. Look up the user (Using '?' handles security to prevent SQL injection!)
    # select password FROM users WHERE username = 'a ; delete from users;'
    cursor.execute("SELECT password FROM users WHERE username = ? and is_enable = 1", (username,))
    result = cursor.fetchone() # Returns a tuple like ('12345',) or None if not found
    conn.close()
    
    # 3. Check if the user exists and the password matches
    if result and result[0] == password:
        request.session["user"] = username
        request.session["is_login"] = True
        # request.session["is_admin"] = ?? according to database user record

        return RedirectResponse(url="/dashboard", status_code=303) 
    
    return HTMLResponse(
        content="Invalid username or password. <a href='/'>Go back</a>", 
        status_code=401
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)