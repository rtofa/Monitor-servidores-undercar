from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone, timedelta

from app.api import monitor, servers, auth
from app.db.database import SessionLocal

# Importações da nova arquitetura
from app.services.grafana_api import coletar_metricas_api
from app.services.state_manager import atualizar_banco_e_alertar
from app.services.chatbee import enviar_alerta_chatbee

# Fuso horário de Brasília (UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))

def rotina_diaria_automatica():
    agora = datetime.now(FUSO_BRASILIA)
    if 7 <= agora.hour < 19:
        print("Fora do horário de monitoramento (19:00 às 07:00). Pulando...")
        return
        
    if (agora.hour == 23 and agora.minute >= 58) or (agora.hour == 0 and agora.minute <= 12):
        print("Janela de reinício de servidores (23:58 às 00:12). Pulando...")
        return

    print("Iniciando varredura via API do Zabbix/Grafana...")
    db = SessionLocal()
    
    try:
        # 1. Busca os dados super rápidos pela API
        dados_da_api = coletar_metricas_api()
        
        if not dados_da_api:
            print("Falha ao comunicar com a API do Grafana. Abortando ciclo.")
            return

        # 2. Atualiza o PostgreSQL e verifica mudanças de estado
        novas_quedas, recuperados = atualizar_banco_e_alertar(db, dados_da_api)
        
        # 3. Lógica de Alertas via Chatbee (WhatsApp Oficial)
        if novas_quedas:
            print(f"Queda detectada! Enviando alerta via Chatbee...")
            enviar_alerta_chatbee(novas_quedas)
            
        elif recuperados:
            print(f"Servidores recuperados: {recuperados}. Banco atualizado.")
        else:
            print("Métricas atualizadas no banco. Nenhum novo incidente (Regra Anti-Spam respeitada).")
            
    except Exception as e:
        print(f"Erro interno na rotina: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # Para testar a API, você pode colocar minutes=1. Em prod, use minutes=5 ou o que preferir.
    scheduler.add_job(rotina_diaria_automatica, 'interval', minutes=5)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Monitoramento Servidores Undercar", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitor.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "online"}