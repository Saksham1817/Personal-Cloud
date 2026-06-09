<div align="center">

# ☁️ Personal Cloud Server

**A self-hosted cloud storage server built from scratch.**
Upload, preview & sync files from any device — no Google Drive, no iCloud, no third-party services. Your data, your hardware, your rules.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-orange?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-purple?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

## 🚀 What is this?

A fully functional personal cloud server running on my own hardware — an old laptop repurposed as a 24/7 server. Built entirely from scratch using Python and FastAPI with no external cloud services.

Access it from any device on the network, upload photos from your phone, preview files in the browser, and manage everything through a clean dark mode UI.

---

## ✨ Features

- 🔐 **JWT Authentication** — secure register/login with bcrypt password hashing
- 📁 **File Management** — upload, preview, download and delete any file type
- 🖼️ **Photo Sync** — upload photos from phone, auto-generates thumbnails
- 🔍 **Duplicate Detection** — SHA-256 hashing prevents duplicate uploads
- 📊 **Storage Stats** — real-time disk usage dashboard
- 🌙 **Dark Mode UI** — clean web interface accessible from any browser
- 📱 **Mobile Ready** — works from iPhone and Android browsers
- 🗂️ **Auto Organization** — photos sorted by year/month automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy ORM |
| Auth | JWT tokens, bcrypt |
| Frontend | HTML, CSS, Vanilla JS |
| Storage | Local filesystem |
| Server | Uvicorn ASGI |

---

## 📁 Project Structure

## 📁 Project Structure

```
personal-cloud-server/
├── app/
│   ├── main.py          # FastAPI app, CORS, routing
│   ├── database.py      # SQLite connection & session
│   ├── models.py        # User & File database models
│   ├── auth.py          # JWT create/verify, bcrypt
│   └── routers/
│       ├── users.py     # /users — register, login, profile
│       ├── files.py     # /files — upload, download, delete, stats
│       └── photos.py    # /photos — upload, list, thumbnails
├── static/
│   └── index.html       # Full dark mode web UI
├── requirements.txt
└── README.md
---

## ⚙️ Setup & Installation

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/personal-cloud-server.git
cd personal-cloud-server
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**5. Open in browser**

http://localhost:8000

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/users/register` | ❌ | Create new account |
| `POST` | `/users/login` | ❌ | Login, get JWT token |
| `GET` | `/users/me` | ✅ | Get your profile |
| `POST` | `/files/upload` | ✅ | Upload any file |
| `GET` | `/files/list` | ✅ | List all your files |
| `GET` | `/files/download/{id}` | ✅ | Download a file |
| `DELETE` | `/files/delete/{id}` | ✅ | Delete a file |
| `GET` | `/files/storage-stats` | ✅ | Disk usage stats |
| `POST` | `/photos/upload` | ✅ | Upload a photo |
| `GET` | `/photos/list` | ✅ | List all photos |
| `GET` | `/photos/thumbnail/{id}` | ✅ | Get thumbnail |

---

## 🔒 Security

- Passwords hashed with **bcrypt** — never stored in plain text
- All protected routes require a valid **JWT token**
- Duplicate files detected via **SHA-256 hash** — no redundant storage
- Files served only to their **owner** — no cross-user access

---

## 💡 Motivation

Built this as a hands-on systems project to understand how cloud storage actually works under the hood — from HTTP file transfer and database design to authentication and network configuration. Everything runs on repurposed hardware with zero cloud costs.

---

<div align="center">
Built with ❤️ from scratch — no tutorials, no boilerplate
</div>