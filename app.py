from fastapi import FastAPI, Request
from routers import auth, clients  # Importas tus routers
from models.seed import seed_db

app = FastAPI()

# Incluís los routers
app.include_router(auth.router)
app.include_router(clients.router)

## Seeders
@app.on_event("startup")
def on_startup():
    seed_db()

# Siempre genero la varible user para ser leida en jinja
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    from routers.auth import get_current_user_from_cookie 
    
    # IMPORTANTE: Inicializar explícitamente como None si falla
    user = None
    try:
        user = get_current_user_from_cookie(request)
    except Exception:
        user = None
        
    request.state.user = user  # Ahora 'user' siempre existe en el estado
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "Bienvenido a la App"}

# gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000