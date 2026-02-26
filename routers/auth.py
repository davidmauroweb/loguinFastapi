from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt

from models.db import SessionLocal, User
from core.security import verify_password, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Autenticación"])
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#Obtengo el usuario de la cookie
def get_current_user_from_cookie(request: Request):
    # 1. Buscamos la cookie que guardamos en el login
    token = request.cookies.get("access_token")
    
    if not token or not token.startswith("Bearer "):
        return None
        
    try:
        # 2. Limpiamos el string para quedarnos solo con el JWT
        token_clean = token.replace("Bearer ", "")
        
        # 3. Validamos el token con nuestra SECRET_KEY
        payload = jwt.decode(token_clean, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 4. Devolvemos los datos del usuario (id, username, rol)
        return payload 
    except Exception:
        # Si el token expiró o es falso, devolvemos None
        return None

@router.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def do_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # 1. BUSCAMOS al usuario (Esto define 'usuario_db')
    usuario_db = db.query(User).filter(User.username == username).first()

    # 2. VALIDAMOS (Si no existe o la pass no coincide)
    if not usuario_db or not verify_password(password, usuario_db.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": {}, 
            "error": "Credenciales inválidas"
        })

    # 3. RECIÉN AQUÍ usamos 'usuario_db' porque ya sabemos que existe
    token_data = {
        "sub": str(usuario_db.id), 
        "role": usuario_db.rol,
        "username": usuario_db.username
    }
    
    # 4. GENERAMOS EL TOKEN
    token = create_access_token(data=token_data)

    # 5. REDIRIGIMOS Y SETEAMOS COOKIE
    response = RedirectResponse(url="/clients", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    
    return response

@router.get("/logout")
async def logout():
    # 1. Creamos la respuesta de redirección al login
    response = RedirectResponse(url="/auth/login", status_code=303)
    
    # 2. Borramos la cookie 'access_token' del navegador
    response.delete_cookie(key="access_token")
    
    # 3. Enviamos la respuesta para que el navegador limpie la sesión
    return response