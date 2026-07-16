from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import database

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    if "user" in request.session:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_profile = database.get_user_profile(username)
    
    if user_profile:
        # 1. Block login if account is waiting for approval
        if not user_profile["approved"]:
            return HTMLResponse(
                content="<h3>Registration Pending</h3>Your account is currently waiting for administrator approval. Please check back later. <br><br><a href='/'>Go back</a>", 
                status_code=403
            )
        
        # 2. Block login if account is suspended
        if not user_profile["isenable"]:
            return HTMLResponse(
                content="<h3>Account Suspended</h3>Your account has been suspended. Please contact an administrator. <br><br><a href='/'>Go back</a>", 
                status_code=403
            )
        
        # 3. Check hashed password securely
        if database.verify_password(user_profile["password"], password):
            request.session["user"] = username
            request.session["isadmin"] = user_profile["isadmin"]
            return RedirectResponse(url="/dashboard", status_code=303) 
            
    return HTMLResponse(
        content="Invalid username or password. <a href='/'>Go back</a>", 
        status_code=401
    )

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.post("/register")
def handle_register(username: str = Form(...), password: str = Form(...)):
    if database.register_user(username, password):
        return HTMLResponse(
            content="<h3>Registration Request Submitted!</h3>Your profile has been saved. An administrator must approve your account before you can log in. <br><br><a href='/'>Click here to return to login</a>", 
            status_code=201
        )
    return HTMLResponse(
        content="That username is already taken. <a href='/register'>Try a different one</a>", 
        status_code=400
    )

# ==========================================
# USER DASHBOARD ROUTE
# ==========================================

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = request.session.get("user")
    isadmin = request.session.get("isadmin", False)
    
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    records = database.get_game_records(user)
    games = database.get_all_games()
    
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={
            "user": user, 
            "isadmin": isadmin, 
            "records": records, 
            "games": games
        }
    )

# ==========================================
# ADMIN ROUTES (User Management)
# ==========================================

@router.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request):
    user = request.session.get("user")
    isadmin = request.session.get("isadmin", False)
    
    if not user or not isadmin:
        return RedirectResponse(url="/dashboard", status_code=302)
        
    all_users = database.get_all_users()
    return templates.TemplateResponse(
        request=request, 
        name="admin_users.html", 
        context={"user": user, "users": all_users}
    )

@router.post("/admin/approve/{target_username}")
def approve_user(request: Request, target_username: str):
    """Processes newly requested registration signups."""
    user = request.session.get("user")
    isadmin = request.session.get("isadmin", False)
    
    if not user or not isadmin:
        return RedirectResponse(url="/dashboard", status_code=302)
        
    database.approve_user(target_username)
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/admin/toggle/{target_username}")
def toggle_user(request: Request, target_username: str, current_status: int = Form(...)):
    user = request.session.get("user")
    isadmin = request.session.get("isadmin", False)
    
    if not user or not isadmin:
        return RedirectResponse(url="/dashboard", status_code=302)
        
    if user == target_username:
        return HTMLResponse("You cannot disable your own admin account! <a href='/admin/users'>Go back</a>", status_code=400)
        
    new_status = 0 if current_status == 1 else 1
    database.set_user_status(target_username, new_status)
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/admin/toggle-role/{target_username}")
def toggle_admin_role(request: Request, target_username: str, current_role: int = Form(...)):
    user = request.session.get("user")
    isadmin = request.session.get("isadmin", False)
    
    if not user or not isadmin:
        return RedirectResponse(url="/dashboard", status_code=302)
        
    if user == target_username:
        return HTMLResponse("You cannot demote yourself from Admin status! <a href='/admin/users'>Go back</a>", status_code=400)
        
    new_role = 0 if current_role == 1 else 1
    database.set_admin_status(target_username, new_role)
    return RedirectResponse(url="/admin/users", status_code=303)


# ==========================================
# GAME RECORDS CRUD
# ==========================================

@router.post("/game/add")
def add_record(request: Request, game_name: str = Form(...), playtime: str = Form(...), levels: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    database.add_game_record(user, game_name, playtime, levels)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/game/edit/{record_id}", response_class=HTMLResponse)
def edit_record_page(request: Request, record_id: int):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    record = database.get_single_record(record_id, user)
    if not record:
        return HTMLResponse("Record not found or unauthorized.", status_code=404)
        
    games = database.get_all_games()
    
    return templates.TemplateResponse(
        request=request, 
        name="edit_record.html", 
        context={
            "user": user, 
            "record": record, 
            "games": games
        }
    )

@router.post("/game/edit/{record_id}")
def handle_edit_record(
    request: Request, 
    record_id: int, 
    game_name: str = Form(...), 
    playtime: str = Form(...), 
    levels: str = Form(...)
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    database.update_game_record(record_id, user, game_name, playtime, levels)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/game/delete/{record_id}")
def delete_record(request: Request, record_id: int):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
        
    database.delete_game_record(record_id, user)
    return RedirectResponse(url="/dashboard", status_code=303)