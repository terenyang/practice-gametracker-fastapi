# 🎮 GameTracker

A modern, secure, and fully responsive web application built with Python and FastAPI. GameTracker allows users to log their gameplay sessions, track levels/benchmarks, and manage their gaming history. It also features a robust, multi-tier administrative system with an account approval pipeline.

---

## ✨ Features

### 👤 User Workspace
* **Interactive Dashboard:** Clean, card-based split-layout to view logged sessions and add new entries side-by-side.
* **Database-Driven Dropdowns:** Preset lists of games are pulled dynamically from SQLite rather than being hardcoded in HTML.
* **Private Sessions (CRUD):** Log new sessions, edit playtime/levels, and delete records. Strong backend validation ensures users can only edit or delete their own data.

### 🛡️ Administrative Controls
* **Admin Registry Panel:** Admins can view a complete directory of registered accounts.
* **Approval Pipeline:** New user registrations default to a "Pending" state. Admins must manually authorize profiles before they can log in.
* **Operational Access Controls:** Suspend or reactivate user accounts instantly.
* **Role Promotion:** Promote standard accounts to Administrator or demote them back to standard user in one click.

### 🔒 Enterprise-Grade Security
* **Password Hashing:** Passwords are never stored in plain-text. The system uses **PBKDF2 with SHA-256** and a unique random 16-byte salt per user.
* **Session Middleware Integration:** Secured using signed cookies and dynamically loaded production environment variables.
* **Protected Routes:** Unauthorized attempts to access dashboards, admin areas, or other users' sessions are automatically bounced back to safe screens.

---

## 🛠️ Tech Stack

* **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database:** SQLite 
* **Templating Engine:** Jinja2
* **Styling:** Modern Vanilla CSS (Sleek, responsive UI layout)
* **Package Manager:** `pip` or `uv`

---

## 🚀 Local Installation & Setup

Get GameTracker up and running on your local machine in just a few steps.

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/gametracker-fastapi.git](https://github.com/YOUR_USERNAME/gametracker-fastapi.git)
cd gametracker-fastapi