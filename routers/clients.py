from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt

router = APIRouter(prefix="/clients")
templates = Jinja2Templates(directory="templates")

# Dependencia para validar el usuario desde la Cookie
def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    try:
        token_data = token.split(" ")[1]
        payload = jwt.decode(token_data, "MI_CLAVE_SECRETA_SUPER_SEGURA", algorithms=["HS256"])
        return payload.get("sub")
    except:
        return None

@router.get("/", response_class=HTMLResponse)
async def list_clients(request: Request, user = Depends(get_current_user_from_cookie)):
    if not user:
        return RedirectResponse(url="/auth/login?error=SessionExpired", status_code=303)
    
    # Aquí traerías los clientes de la DB
    fake_clients = [{"id": 1, "name": "Empresa ACME"}]
    return templates.TemplateResponse("clients/list.html", {
        "request": request, 
        "user": user, 
        "clients": fake_clients
    })