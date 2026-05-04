from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

# Importando os novos roteadores modulares
from app.api import monitor, servers, auth

# Importando serviços e banco de dados para a rotina automática em background
from app.db.database import SessionLocal
from app.services.scraper import verificar_servidores
from app.services.whatsapp import enviar_relatorio_whatsapp
from app.services.ligacao import alertar_por_ligacao
from app.services.state_manager import analisar_estado_e_alertar

def rotina_diaria_automatica():
    """Função invocada pelo agendador com inteligência Anti-Spam e banco de dados."""
    print("Iniciando varredura agendada...")
    
    # Abrindo sessão do banco manualmente, pois estamos em uma thread de background
    db = SessionLocal()
    try:
        caminho_imagem, tem_erro, servidores_com_erro = verificar_servidores()
        
        if caminho_imagem:
            # Compara com o banco para garantir que é uma queda nova
            novas_quedas, recuperados = analisar_estado_e_alertar(db, servidores_com_erro)
            
            if novas_quedas:
                print(f"Instabilidade detectada! Disparando alertas para: {novas_quedas}")
                enviar_relatorio_whatsapp(caminho_imagem, True, novas_quedas)
                alertar_por_ligacao(novas_quedas)
            elif recuperados:
                print(f"Servidores recuperados: {recuperados}")
            elif tem_erro:
                print("Servidores continuam fora. Nenhum alerta novo disparado (Anti-Spam).")
            else:
                print("Varredura concluída. Todos os servidores operacionais e no verde.")
    except Exception as e:
        print(f"Erro interno na rotina agendada: {e}")
    finally:
        db.close()  # Muito importante para não vazar memória no servidor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup inicial: Liga o agendador em background
    scheduler = BackgroundScheduler()
    
    # Mantendo a sua rotina programada para as 05:00
    scheduler.add_job(rotina_diaria_automatica, 'cron', hour=5, minute=0)
    
    # Se quiser transformar a automação em 24/7 de verdade testando a cada 5 minutos:
    # scheduler.add_job(rotina_diaria_automatica, 'interval', minutes=5)
    
    scheduler.start()
    
    yield # O FastAPI roda aqui enquanto o servidor estiver online
    
    # Teardown: Desliga o agendador ao encerrar o servidor
    scheduler.shutdown()

# Instância baseada na identidade corporativa
app = FastAPI(title="Monitoramento Fluxo Alpha", lifespan=lifespan)

# Configuração de CORS (Libera o acesso para o Frontend React consumir os dados)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua "*" pela URL do seu domínio React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionando os agrupamentos de rotas na API
app.include_router(monitor.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "online", "service": "API de Monitoramento Ativa"}