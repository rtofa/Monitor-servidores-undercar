from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

# Importando a nova arquitetura
from app.services.grafana_api import coletar_metricas_api
from app.services.state_manager import atualizar_banco_e_alertar
from app.services.chatbee import enviar_alerta_chatbee

router = APIRouter(tags=["Monitoramento Manual"])

@router.post("/verificar-agora")
def disparar_varredura_manual(db: Session = Depends(get_db)):
    """
    Rota para forçar a varredura das métricas imediatamente (botão manual no painel).
    """
    # 1. Puxa os dados via API do Zabbix (Super Rápido)
    dados_da_api = coletar_metricas_api()
    
    if not dados_da_api:
        return {"status": "erro", "mensagem": "Falha ao conectar com a API do Grafana/Zabbix."}

    # 2. Grava no banco de dados e descobre quem caiu/voltou
    novas_quedas, recuperados = atualizar_banco_e_alertar(db, dados_da_api)
    
    # 3. Lógica de alertas via Chatbee (WhatsApp Oficial)
    if novas_quedas:
        print("Queda manual detectada! Enviando alerta via Chatbee...")
        enviar_alerta_chatbee(novas_quedas)
        
        return {
            "status": "alerta", 
            "mensagem": "Varredura concluída. Quedas detectadas e alertas disparados!",
            "novas_quedas": novas_quedas
        }
        
    elif recuperados:
        return {
            "status": "sucesso", 
            "mensagem": f"Varredura concluída. Servidores recuperados: {recuperados}",
            "recuperados": recuperados
        }
        
    return {
        "status": "sucesso", 
        "mensagem": "Varredura concluída. Todos os servidores operacionais e banco de dados atualizado com as novas métricas de CPU e RAM."
    }