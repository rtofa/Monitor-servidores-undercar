from fastapi import APIRouter, HTTPException
from app.services.scraper import verificar_servidores
from app.services.whatsapp import enviar_relatorio_whatsapp

router = APIRouter()

@router.post("/trigger-check")
def disparar_verificacao_manual():
    caminho_imagem, tem_erro, servidores_com_erro = verificar_servidores()
    
    if not caminho_imagem:
        raise HTTPException(status_code=500, detail="Falha ao tentar gerar o print do Grafana.")
        
    sucesso_envio = enviar_relatorio_whatsapp(caminho_imagem, tem_erro, servidores_com_erro)
    
    if sucesso_envio:
        return {
            "status": "success", 
            "message": "Scraping concluído e mensagem enviada ao WhatsApp.", 
            "has_error": tem_erro
        }
    else:
        raise HTTPException(status_code=500, detail="O print foi gerado, mas houve falha no envio para o WhatsApp.")