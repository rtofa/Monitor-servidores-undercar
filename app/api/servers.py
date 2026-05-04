from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import ServerState
from app.schemas import ServerStateResponse

router = APIRouter(prefix="/servers", tags=["Dashboard"])

@router.get("/", response_model=List[ServerStateResponse])
def listar_status_servidores(db: Session = Depends(get_db)):
    """
    Retorna o status atual e histórico de todos os servidores.
    """
    return db.query(ServerState).all()