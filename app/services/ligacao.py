import requests
from app.core.config import settings

def alertar_por_ligacao(servidores_com_erro: list) -> bool:
    nomes_falha = ", ".join(servidores_com_erro)
    
    twiml = (
        f"<Response>"
        f"<Say language='pt-BR' voice='Polly.Vitoria-Neural'>"
        f"Atenção. O robô de monitoramento identificou instabilidade. "
        f"Os seguintes servidores estão fora do verde: {nomes_falha}. "
        f"Verifique o relatório no seu WhatsApp."
        f"</Say>"
        f"</Response>"
    )

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Calls.json"
    
    payload = {
        "To": "REDACTED_PHONE", # Número do marcelo para a ligação do twilio 
        "From": settings.twilio_phone_number, # O número virtual que a Twilio vai emprestar
        "Twiml": twiml
    }

    try:
        print("Acionando Twilio para ligação de alerta TTS...")
        response = requests.post(
            url, 
            data=payload, 
            auth=(settings.twilio_account_sid, settings.twilio_auth_token)
        )
        response.raise_for_status()
        print("Ligação disparada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao disparar ligação pela Twilio: {e}")
        return False