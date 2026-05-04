import requests
import json
import datetime
import os

# --- PREENCHA COM SEUS DADOS ---
USUARIO_GRAFANA = "REDACTED_EMAIL"
SENHA_GRAFANA = "REDACTED_PASSWORD"
# -------------------------------

def gerar_payload_dinamico(nome_servidor, nome_metrica):
    """Monta o JSON idêntico ao do navegador para evitar o Erro 400"""
    agora_ms = int(datetime.datetime.now().timestamp() * 1000)
    cinco_min_atras_ms = agora_ms - (5 * 60 * 1000)

    return {
        "queries": [
            {
                "application": {"filter": ""},
                "datasource": {
                    "type": "alexanderzobnin-zabbix-datasource",
                    "uid": "jfm5kV0nk"
                },
                "datasourceId": 38, # <-- ESTE ERA O GRANDE CULPADO DO ERRO 400
                "functions": [],
                "group": {"filter": "/^(DIGYCOM)$/"},
                "host": {"filter": f"/^{nome_servidor}$/"},
                "intervalMs": 60000,
                "item": {"filter": nome_metrica},
                "itemTag": {"filter": ""},
                "maxDataPoints": 100,
                "options": {
                    "disabledDataAlignment": False,
                    "showDisabledItems": False,
                    "skipEmptyValues": False
                },
                "proxy": {"filter": ""},
                "queryType": "0",
                "refId": "A",
                "resultFormat": "time_series",
                "table": {"skipEmptyValues": False},
                "tags": {"filter": ""},
                "trigger": {"filter": ""},
                "triggers": {"acknowledged": 2, "count": True, "minSeverity": 3}
            }
        ],
        "range": {
            "from": "now-5m",
            "to": "now",
            "raw": {"from": "now-5m", "to": "now"}
        },
        "from": str(cinco_min_atras_ms),
        "to": str(agora_ms)
    }

def rodar_teste_api_dinamica():
    sessao = requests.Session()
    
    # Adicionando os cabeçalhos obrigatórios do Grafana
    sessao.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": "15" # Passaporte para a sua organização
    })
    
    login_url = "https://grafana.example.com/login"
    query_url = "https://monitor.advant.com.br/api/ds/query"
    
    credenciais = {"user": USUARIO_GRAFANA, "password": SENHA_GRAFANA}
    
    print("1. Realizando login...")
    try:
        sessao.post(login_url, json=credenciais).raise_for_status()
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return

    payload = gerar_payload_dinamico("APL-730", "Total memory")
    
    print(f"2. Buscando dados de memória do APL-730...")
    resposta = sessao.post(query_url, json=payload)
    
    try:
        resposta.raise_for_status() # Verifica se deu 200 OK
        dados_crus = resposta.json()
        
        # Salva o resultado
        os.makedirs("temp", exist_ok=True)
        caminho_arquivo = "temp/resposta_zabbix.json"
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_crus, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Sucesso absoluto! Os dados foram salvos em {caminho_arquivo}")
        
    except requests.exceptions.HTTPError as e:
        # Se falhar novamente, isso vai nos dizer EXATAMENTE o motivo!
        print(f"❌ Erro 400 persistiu. O Grafana disse: {resposta.text}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    rodar_teste_api_dinamica()