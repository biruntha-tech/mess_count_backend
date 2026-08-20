from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, student, admin, notifications

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MessCount API", description="Backend API for MessCount React Frontend")

# Configure CORS so the React frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # For production, change to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(notifications.admin_router)

@app.get("/")
def root():
    return {"message": "Welcome to the MessCount API. Visit /docs for the Swagger UI."}
