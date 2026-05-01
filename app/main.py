from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.api.routes import router
from app.services.scraper import verificar_servidores
from app.services.whatsapp import enviar_relatorio_whatsapp

def rotina_diaria_automatica():
    """Função invocada pelo agendador todos os dias"""
    print("Iniciando varredura agendada das 05:00...")
    caminho_imagem, tem_erro, servidores_com_erro = verificar_servidores()
    if caminho_imagem:
        enviar_relatorio_whatsapp(caminho_imagem, tem_erro, servidores_com_erro)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup inicial: Liga o agendador em background
    scheduler = BackgroundScheduler()
    scheduler.add_job(rotina_diaria_automatica, 'cron', hour=5, minute=0)
    scheduler.start()
    
    yield # O FastAPI roda aqui
    
    # Teardown: Desliga o agendador ao encerrar o servidor
    scheduler.shutdown()

# Instância baseada na identidade da assessoria
app = FastAPI(title="Monitoramento Fluxo Alpha", lifespan=lifespan)

# Adiciona o agrupamento de rotas
app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "online", "service": "API de Monitoramento Ativa"}