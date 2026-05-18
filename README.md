# Monitor Servidores Undercar

Plataforma de monitoramento de servidores com coleta de metricas via Grafana/Zabbix, alertas por WhatsApp (Chatwoot) e ligacoes automaticas (Twilio). Pensado para operacao 24x7 com rotinas agendadas e persistencia de estados.

## Destaques

- Coleta rapida de metricas por API (CPU e RAM) com tolerancia a falhas.
- Snapshot automatico do dashboard do Grafana para evidenciar incidentes.
- Alertas multicanal: mensagem com evidencias e ligacao TTS.
- Persistencia de estados no PostgreSQL para evitar alertas duplicados.
- API FastAPI para consulta e integracoes futuras.

## Como funciona

1) Agendador executa a rotina periodica.
2) API do Grafana/Zabbix retorna as metricas por servidor.
3) O estado e atualizado no banco e as mudancas sao detectadas.
4) Em caso de queda, o sistema envia print + mensagem e dispara ligacao.

## Stack

- FastAPI + Pydantic Settings
- PostgreSQL + SQLAlchemy + Alembic
- Playwright (screenshot do Grafana)
- APScheduler (rotina periodica)
- Chatwoot + Twilio (alertas)

## Configuracao

1) Copie o arquivo de exemplo e preencha as variaveis:

```
cp .env.exemple .env
```

2) Ajuste os valores no .env (Grafana, Chatwoot, Twilio e Banco).

## Executar localmente

Subir banco com Docker:

```
docker-compose up -d
```

Instalar dependencias:

```
pip install -r requirements.txt
```

Instalar browsers do Playwright (se necessario):

```
playwright install
```

Subir a API:

```
python -m uvicorn app.main:app --reload
```

## Testes

```
pytest -q
```

## Observacoes de seguranca

- Nao suba o .env para o repositorio.
- Mantenha credenciais rotacionadas e use tokens com escopo minimo.

## Por que este projeto se destaca

- Envolve integracao real com sistemas de monitoramento e mensageria.
- Resolve um problema operacional concreto (alerta e evidencias).
- Arquitetura simples, clara e pronta para evolucao (API + servicos).
