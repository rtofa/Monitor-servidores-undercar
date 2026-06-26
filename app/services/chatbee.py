import requests
from datetime import datetime
from app.core.config import settings


def enviar_alerta_chatbee(servidores_offline: list) -> bool:
    """
    Envia alerta de queda de servidor via WhatsApp Oficial (Meta)
    usando a API do Chatbee com o template aprovado 'automacao_aviso_queda_servidor'.

    Variáveis do template:
        {{1}} = Nomes dos servidores offline (ex: "APL-01, VIRT-03")
        {{2}} = Horário do incidente (ex: "14:32")
    """
    nomes_falha = ", ".join(servidores_offline)
    horario_incidente = datetime.now().strftime("%H:%M")

    payload = {
        "contact_address": "5511993345150",
        "contact_custom_name": "Adriano",
        "user_id": settings.chatbee_user_id,
        "department_id": settings.chatbee_department_id,
        "channel_type": "waba",
        "channel_id": settings.chatbee_channel_id,
        "received_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
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
                        {"type": "text", "text": nomes_falha},
                        {"type": "text", "text": horario_incidente}
                    ]
                }
            ],
            "template_data": {
                "_id": "6a3d24b311d57efbfdef8674",
                "id": "1543344257298869",
                "name": "automacao_aviso_queda_servidor",
                "components": [
                    {
                        "type": "BODY",
                        "text": (
                            "🚨 *ALERTA DE INFRAESTRUTURA* 🚨\n\n"
                            "O Cérebro de Monitoramento detectou falha de comunicação (OFFLINE) nos seguintes servidores:\n"
                            "*{{1}}*\n\n"
                            "Horário do incidente: {{2}}\n\n"
                            "Por favor, acesse o painel de controle corporativo para auditar as métricas de CPU, RAM e restabelecer os serviços."
                        ),
                        "example": {
                            "body_text": [["APL-00", "13:00"]]
                        }
                    }
                ],
                "category": "UTILITY",
                "language": "pt_BR",
                "status": "APPROVED",
                "waba_id": "915901774873066",
                "channel_uuid": "b093d349-4f15-4f1a-87e3-f778155c66a6",
                "customer_uuid": "7012b48c-99d7-4536-a1f9-101a0347b203",
                "disabled": False,
                "__v": 0,
                "quality_score": {"score": "UNKNOWN", "date": 1782476724},
                "rejected_reason": "NONE"
            },
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

    headers = {
        "Content-Type": "application/json",
        "api_access_token": settings.chatbee_api_token,
        "Authorization": f"Bearer {settings.chatbee_api_token}"
    }

    try:
        print(f"Enviando alerta Chatbee para 5511993345150 — Servidores: {nomes_falha}")
        response = requests.post(
            settings.chatbee_api_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        print("Alerta Chatbee enviado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao enviar alerta pelo Chatbee: {e}")
        return False
