from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import ServerState, ServerEvent # <-- Importe o ServerEvent aqui

def atualizar_banco_e_alertar(db: Session, dados_api: dict) -> tuple[list, list]:
    agora = datetime.utcnow()
    servidores_db = db.query(ServerState).all()
    mapa_db = {s.server_name: s for s in servidores_db}

    novas_quedas = []
    recuperados = []

    for nome, metricas in dados_api.items():
        status_atual = metricas["status"]
        
        if nome not in mapa_db:
            novo_servidor = ServerState(
                server_name=nome, status=status_atual,
                cpu_usage=metricas["cpu_usage"], ram_usage=metricas["ram_usage"],
                last_checked=agora, status_changed_at=agora
            )
            db.add(novo_servidor)
            if status_atual == "OFFLINE":
                novas_quedas.append(nome)
                # Registra o log da primeira queda
                db.add(ServerEvent(server_name=nome, event_type="OFFLINE", message=f"{nome} identificado como OFFLINE.", timestamp=agora))
        else:
            servidor = mapa_db[nome]
            servidor.last_checked = agora
            servidor.cpu_usage = metricas["cpu_usage"]
            servidor.ram_usage = metricas["ram_usage"]
            
            if servidor.status == "ONLINE" and status_atual == "OFFLINE":
                servidor.status = "OFFLINE"
                servidor.status_changed_at = agora
                novas_quedas.append(nome)
                # Grava o log da queda
                db.add(ServerEvent(server_name=nome, event_type="OFFLINE", message=f"Queda detectada no servidor {nome}.", timestamp=agora))
                
            elif servidor.status == "OFFLINE" and status_atual == "ONLINE":
                servidor.status = "ONLINE"
                servidor.status_changed_at = agora
                recuperados.append(nome)
                # Grava o log da recuperação
                db.add(ServerEvent(server_name=nome, event_type="ONLINE", message=f"Servidor {nome} voltou a operar.", timestamp=agora))

    db.commit()
    return novas_quedas, recuperados