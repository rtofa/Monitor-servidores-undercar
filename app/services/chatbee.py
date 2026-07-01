import requests
import json
from datetime import datetime, timezone, timedelta
from app.core.config import settings

# Fuso horário de Brasília (UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))


def enviar_alerta_chatbee(servidores_offline: list) -> bool:
    """
    Envia alerta de queda de servidor via WhatsApp Oficial (Meta)
    usando a API do Chatbee com o template aprovado 'automacao_aviso_queda_servidor'.

    Variáveis do template:
        {{1}} = Nomes dos servidores offline (ex: "APL-01, VIRT-03")
        {{2}} = Horário do incidente (ex: "14:32")
    """
    nomes_falha = ", ".join(servidores_offline)
    agora_brasilia = datetime.now(FUSO_BRASILIA)
    horario_incidente = agora_brasilia.strftime("%H:%M")

    contatos = [
        {"numero": "5511993345150", "nome": "Adriano"},
        {"numero": "5514981212423", "nome": "Marcelo"}
    ]

    headers = {
        "Content-Type": "application/json",
        "api_access_token": settings.chatbee_api_token,
        "Authorization": f"Bearer {settings.chatbee_api_token}",
        "token": settings.chatbee_api_token,
        "x-api-key": settings.chatbee_api_token
    }

    sucesso_geral = True

    for contato in contatos:
        payload = {
            "contact_address": contato["numero"],
            "contact_custom_name": contato["nome"],
            "user_id": settings.chatbee_user_id,
            "department_id": settings.chatbee_department_id,
            "channel_type": "waba",
            "channel_id": settings.chatbee_channel_id,
            "received_at": agora_brasilia.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "type": "template",
            "payload": {
                "type": "template",
                "valid": True,
                "template": {
                    "name": "automacao_aviso_queda_servidor",
                    "language": {"code": "pt_BR"}
                },
                "components": [
                    {
                        "type": "BODY",
                        "parameters": [
                            {"parameter_name": "1", "type": "text", "text": nomes_falha},
                            {"parameter_name": "2", "type": "text", "text": horario_incidente}
                        ]
                    }
                ],
                "rendered_message": {
                    "body": {
                        "type": "text",
                        "text": (
                            f"🚨 *ALERTA DE INFRAESTRUTURA* 🚨\n\n"
                            f"O Cérebro de Monitoramento detectou falha de comunicação (OFFLINE) nos seguintes servidores:\n"
                            f"*{nomes_falha}*\n\n"
                            f"Horário do incidente: {horario_incidente}\n\n"
                            f"Por favor, acesse o painel de controle corporativo para auditar as métricas de CPU, RAM e restabelecer os serviços."
                        )
                    }
                }
            },
            "active": True
        }

        try:
            print(f"Enviando alerta Chatbee para {contato['numero']}...")
            print("=== PAYLOAD ENVIADO ===")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            print("=======================")
            
            response = requests.post(
                settings.chatbee_api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            print(f"Alerta Chatbee enviado com sucesso para {contato['numero']}!")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar alerta pelo Chatbee para {contato['numero']}: {e}")
            if e.response is not None:
                print(f"Detalhes do erro na API: {e.response.text}")
            sucesso_geral = False

    return sucesso_geral
