from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Autenticação"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def autenticar_usuario(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Valida as credenciais do usuário.
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="E-mail ou senha incorretos."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Usuário inativo."
        )

    # Nota Arquitetural: Para a evolução do painel, o ideal é substituir
    # esse retorno em JSON por um Token JWT padrão de mercado usando a biblioteca PyJWT.
    return {
        "status": "success", 
        "message": "Autenticado com sucesso", 
        "user_id": user.id,
        "username": user.username
    }