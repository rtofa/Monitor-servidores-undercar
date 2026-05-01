import requests
from app.core.config import settings

def enviar_relatorio_whatsapp(caminho_imagem: str, tem_erro: bool, servidores_com_erro: list) -> bool:
    if tem_erro:
        # Pega a lista ['APL-00', 'DC1'] e transforma em texto: "APL-00, DC1"
        nomes_falha = ", ".join(servidores_com_erro) if servidores_com_erro else "Desconhecido"
        mensagem = f"⚠️ *Atenção!* O robô identificou instabilidade. Servidor(es) fora do verde: *{nomes_falha}*. Segue o print para verificação imediata."
    else:
        mensagem = "✅ *Bom dia!* Relatório das 05:00: Todos os servidores estão operacionais e na cor verde."

    headers = {
        'api_access_token': settings.chatwoot_token
    }
    data = {
        'content': mensagem,
        'message_type': 'outgoing',
        'private': 'false' 
    }
    
    try:
        with open(caminho_imagem, 'rb') as f:
            files = {'attachments[]': (caminho_imagem, f, 'image/png')}
            response = requests.post(
                settings.chatwoot_api_url, 
                headers=headers, 
                data=data, 
                files=files
            )
            response.raise_for_status()
            return True
            
    except Exception as e:
        print(f"Erro ao comunicar com API do Chatwoot: {e}")
        return False