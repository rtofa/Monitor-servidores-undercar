import requests
import datetime

USUARIO_GRAFANA = "REDACTED_EMAIL"
SENHA_GRAFANA = "REDACTED_PASSWORD"

# Nossa Fonte da Verdade de Servidores Monitorados
SERVIDORES_MONITORADOS = [
    "APL-00", "APL-01", "APL-02", "APL-03", "APL-04", "APL-05", "APL-06", "APL-07",
    "APL-730", "APL-740", "BDSQL-01", "BROKER1", "BROKER2", "DC1", "DC3", "DOMAIN_STATUS",
    "FTP", "POWERBI", "SQL1", "VIRT-01", "VIRT-02", "VIRT-03", "VIRT-04", "VIRT-05",
    "VIRT-06", "VIRT-07", "VIRT-09", "VIRT-10", "VIRT-11", "VIRT-12"
]

def _gerar_payload_dinamico(nome_servidor, nome_metrica):
    agora_ms = int(datetime.datetime.now().timestamp() * 1000)
    cinco_min_atras_ms = agora_ms - (5 * 60 * 1000)

    return {
        "queries": [
            {
                "application": {"filter": ""},
                "datasource": {"type": "alexanderzobnin-zabbix-datasource", "uid": "jfm5kV0nk"},
                "datasourceId": 38,
                "functions": [],
                "group": {"filter": "/^(DIGYCOM)$/"},
                "host": {"filter": f"/^{nome_servidor}$/"},
                "intervalMs": 60000,
                "item": {"filter": nome_metrica},
                "itemTag": {"filter": ""},
                "maxDataPoints": 100,
                "options": {"disabledDataAlignment": False, "showDisabledItems": False, "skipEmptyValues": False},
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
        "range": {"from": "now-5m", "to": "now", "raw": {"from": "now-5m", "to": "now"}},
        "from": str(cinco_min_atras_ms),
        "to": str(agora_ms)
    }

def _extrair_ultimo_valor(dados_json):
    try:
        valores = dados_json["results"]["A"]["frames"][0]["data"]["values"][1]
        if valores and len(valores) > 0:
            return valores[-1]
    except (KeyError, IndexError, TypeError):
        pass
    return None

def coletar_metricas_api() -> dict:
    """Varre a lista de servidores e devolve o Dicionário mestre com Status, CPU e RAM"""
    sessao = requests.Session()
    sessao.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": "15"
    })
    
    try:
        sessao.post("https://grafana.example.com/login", json={"user": USUARIO_GRAFANA, "password": SENHA_GRAFANA}).raise_for_status()
    except Exception as e:
        print(f"Erro de login na API: {e}")
        return {}

    dados_finais = {}
    query_url = "https://monitor.advant.com.br/api/ds/query"

    for servidor in SERVIDORES_MONITORADOS:
        dados_finais[servidor] = {"status": "ONLINE", "cpu_usage": None, "ram_usage": None}
        
        try:
            # Puxa a CPU primeiro (Funciona como nosso Heartbeat)
            resp_cpu = sessao.post(query_url, json=_gerar_payload_dinamico(servidor, "CPU utilization"))
            val_cpu = _extrair_ultimo_valor(resp_cpu.json())
            
            # Se a CPU retornou None, o servidor parou de responder ao Zabbix (Caiu)
            if val_cpu is None:
                 dados_finais[servidor]["status"] = "OFFLINE"
                 continue # Pula para o próximo servidor
                 
            # Se chegou aqui, está ONLINE!
            dados_finais[servidor]["status"] = "ONLINE"
            dados_finais[servidor]["cpu_usage"] = val_cpu

            # Busca RAM
            resp_ram = sessao.post(query_url, json=_gerar_payload_dinamico(servidor, "Total memory"))
            ram_bytes = _extrair_ultimo_valor(resp_ram.json())
            
            if ram_bytes:
                dados_finais[servidor]["ram_usage"] = round(ram_bytes / (1024**3), 2)

        except Exception as e:
            print(f"Falha de métrica no {servidor}: {e}")
            dados_finais[servidor]["status"] = "OFFLINE"

    return dados_finais