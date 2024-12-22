from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string

app = FastAPI()

# Initialize the database URL (SQLite in-memory database for simplicity)
DATABASE_URL = "sqlite:///./notes.db"

# Setup database engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the note model
Base = declarative_base()

# Encryption setup (this should be securely stored in production)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# Database Model for Notes
class Note(Base):
    __tablename__ = 'notes'
    code = Column(String, primary_key=True, index=True)
    content = Column(String)

# Initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Utility functions
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def encrypt_content(content):
    return cipher.encrypt(content.encode()).decode()

def decrypt_content(encrypted_content):
    try:
        return cipher.decrypt(encrypted_content.encode()).decode()
    except InvalidToken:
        return None

# Template setup
templates = Jinja2Templates(directory="templates")

# Create the database tables
init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
async def create_note(request: Request, content: str = Form(...)):
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    code = generate_code()
    encrypted_content = encrypt_content(content)

    db = SessionLocal()
    db_note = Note(code=code, content=encrypted_content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    db.close()

    return templates.TemplateResponse("note_created.html", {"request": request, "code": code})

@app.get("/retrieve", response_class=HTMLResponse)
async def retrieve(request: Request):
    return templates.TemplateResponse("retrieve.html", {"request": request})

@app.post("/note", response_class=HTMLResponse)
async def view_note(request: Request, code: str = Form(...)):
    db = SessionLocal()
    db_note = db.query(Note).filter(Note.code == code).first()

    if db_note is None:
        db.close()
        raise HTTPException(status_code=404, detail="Invalid code or note not found")

    decrypted_content = decrypt_content(db_note.content)
    if decrypted_content is None:
        db.close()
        raise HTTPException(status_code=500, detail="Failed to decrypt the note")

    # Delete the note after viewing
    db.delete(db_note)
    db.commit()
    db.close()

    return templates.TemplateResponse("view_note.html", {"request": request, "note": decrypted_content})

@app.exception_handler(404)
async def not_found_exception(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "message": "Page not found"}, status_code=404)

@app.exception_handler(500)
async def internal_error_exception(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "message": "Internal Server Error"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
