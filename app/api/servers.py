from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import ServerState, ServerEvent
from app.schemas import ServerStateResponse, ServerEventResponse

router = APIRouter(prefix="/servers", tags=["Dashboard"])

@router.get("/", response_model=List[ServerStateResponse])
def listar_status_servidores(db: Session = Depends(get_db)):
    return db.query(ServerState).all()

@router.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(ServerState).count()
    offline = db.query(ServerState).filter(ServerState.status == "OFFLINE").count()
    online = total - offline
    
    uptime = "100%" if total == 0 else f"{((online/total)*100):.2f}%"
    
    # Conta incidentes reais registrados na tabela de logs nas últimas 24h
    ontem = datetime.utcnow() - timedelta(days=1)
    incidentes_24h = db.query(ServerEvent).filter(
        ServerEvent.event_type == "OFFLINE",
        ServerEvent.timestamp >= ontem
    ).count()
    
    return {
        "uptime_global": uptime,
        "latencia_media": "12 ms", # Latência de ping varia muito, vamos deixar fixo por enquanto
        "incidentes_24h": incidentes_24h,
        "checks_24h": total * 288 
    }

@router.get("/events/", response_model=List[ServerEventResponse])
def get_events(db: Session = Depends(get_db)):
    # Retorna os últimos 20 eventos do sistema, do mais recente para o mais antigo
    return db.query(ServerEvent).order_by(ServerEvent.timestamp.desc()).limit(20).all()

@router.get("/{server_name}/erros")
def get_historico_erros(server_name: str, db: Session = Depends(get_db)):
    """
    Retorna o histórico exato de quantas vezes e em quais horários 
    um servidor específico caiu. Perfeito para o botão 'Detalhes'.
    """
    # Busca no banco apenas os eventos de QUEDA ("OFFLINE") deste servidor
    quedas = db.query(ServerEvent).filter(
        ServerEvent.server_name == server_name,
        ServerEvent.event_type == "OFFLINE"
    ).order_by(ServerEvent.timestamp.desc()).all()

    # Monta a resposta limpa para o Frontend
    historico_formatado = []
    for evento in quedas:
        historico_formatado.append({
            "horario": evento.timestamp.isoformat(), # Formato padrão que o React entende
            "mensagem": evento.message
        })

    return {
        "servidor": server_name,
        "total_quedas_registradas": len(quedas),
        "historico": historico_formatado
    }