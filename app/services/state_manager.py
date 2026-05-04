from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import ServerState

def analisar_estado_e_alertar(db: Session, servidores_com_erro_atual: list) -> tuple[list, list]:
    """
    Analisa a lista atual de erros contra o banco de dados.
    Retorna: (novas_quedas, servidores_recuperados)
    """
    agora = datetime.utcnow()
    
    # Busca todos os servidores cadastrados
    servidores_db = db.query(ServerState).all()
    mapa_db = {s.server_name: s for s in servidores_db}

    novas_quedas = []
    recuperados = []

    # 1. Verifica quem caiu
    for nome in servidores_com_erro_atual:
        if nome not in mapa_db:
            # Servidor novo que já foi registrado com falha
            novo_servidor = ServerState(
                server_name=nome, 
                status="OFFLINE", 
                last_checked=agora, 
                status_changed_at=agora
            )
            db.add(novo_servidor)
            novas_quedas.append(nome)
        else:
            servidor = mapa_db[nome]
            servidor.last_checked = agora
            if servidor.status == "ONLINE":
                # Mudança de estado: Estava Online, agora está Offline
                servidor.status = "OFFLINE"
                servidor.status_changed_at = agora
                novas_quedas.append(nome)

    # 2. Verifica quem voltou (Estava OFFLINE, mas não está mais na lista de erros)
    for servidor in servidores_db:
        if servidor.status == "OFFLINE" and servidor.server_name not in servidores_com_erro_atual:
            servidor.status = "ONLINE"
            servidor.status_changed_at = agora
            servidor.last_checked = agora
            recuperados.append(servidor.server_name)
        elif servidor.status == "ONLINE" and servidor.server_name not in servidores_com_erro_atual:
            # Continua operando normalmente, apenas atualiza o timestamp
            servidor.last_checked = agora

    db.commit()
    return novas_quedas, recuperados