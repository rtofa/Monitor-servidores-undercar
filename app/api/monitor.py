from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.scraper import verificar_servidores
from app.services.whatsapp import enviar_relatorio_whatsapp
from app.services.ligacao import alertar_por_ligacao
from app.services.state_manager import analisar_estado_e_alertar

router = APIRouter(prefix="/monitor", tags=["Monitoramento"])

@router.post("/trigger-check")
def disparar_verificacao_manual(db: Session = Depends(get_db)):
    caminho_imagem, tem_erro, servidores_com_erro = verificar_servidores()

    if not caminho_imagem:
        raise HTTPException(status_code=500, detail="Falha ao tentar gerar o print do Grafana.")

    novas_quedas, recuperados = analisar_estado_e_alertar(db, servidores_com_erro)

    if novas_quedas:
        sucesso_envio = enviar_relatorio_whatsapp(caminho_imagem, True, novas_quedas)
        if not sucesso_envio:
            raise HTTPException(status_code=500, detail="Print gerado, mas falha no envio do WhatsApp.")

        sucesso_ligacao = alertar_por_ligacao(novas_quedas)
        if not sucesso_ligacao:
            raise HTTPException(status_code=500, detail="WhatsApp enviado, mas falha na ligação.")

        return {
            "status": "success",
            "message": f"Instabilidade detectada. Alertas enviados para: {novas_quedas}",
            "has_error": True,
            "novas_quedas": novas_quedas
        }

    elif recuperados:
        return {
            "status": "success",
            "message": f"Servidores recuperados: {recuperados}",
            "has_error": False,
            "recuperados": recuperados
        }

    if tem_erro:
        return {
            "status": "success",
            "message": "Instabilidade continua. Nenhum novo alerta enviado (Regra Anti-Spam).",
            "has_error": True
        }

    return {
        "status": "success",
        "message": "Nenhuma instabilidade detectada. Todos os servidores operacionais.",
        "has_error": False
    }