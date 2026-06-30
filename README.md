# Cérebro de Monitoramento Undercar 🧠

Este projeto é um sistema inteligente de monitoramento de servidores focado em **escalabilidade, prevenção de falsos positivos (Anti-Spam) e alertas em tempo real**. Ele consulta métricas do Zabbix/Grafana e notifica a equipe de infraestrutura via WhatsApp Oficial (API Chatbee) em caso de incidentes.

## 🏗️ Arquitetura do Sistema

O projeto foi construído usando uma stack moderna em Python e conteinerizada:

- **FastAPI**: Framework web de altíssima performance responsável por expor a API manual (`/api/v1/verificar-agora`).
- **APScheduler**: Biblioteca de agendamento em background (roda as varreduras de forma autônoma sem travar a API).
- **PostgreSQL + SQLAlchemy**: Banco de dados relacional para persistir o estado dos servidores e gerar o histórico de eventos, bloqueando alertas duplicados.
- **Docker & Docker Compose**: Empacota a aplicação e o banco em contêineres (`python:3.10-slim` e `postgres:15-alpine`).
- **Chatbee API**: Integração com a API de fila (Hermes) para envio dos modelos pré-aprovados pela Meta.

---

## ⚙️ Regras de Negócio e Lógica Principal

Qualquer programador que continuar o projeto precisa estar ciente das regras de negócio que blindam o sistema contra envio de spans e notificações incorretas:

### 1. Horário de Monitoramento
O sistema roda em background a cada **5 minutos**, mas só efetua varreduras e envia alertas no período **noturno**:
- **Horário de Atuação**: `19:00` até `07:00` (Horário de Brasília).
- Fora deste horário, o script pula o ciclo e não notifica.
- Arquivo: `app/main.py`.

### 2. Janela de Manutenção (Reinício de Servidores)
Foi criada uma janela onde é sabido que todos os servidores caem de propósito (reinício automático).
- **Janela Silenciada**: `23:50` às `01:00`.
- Se a varredura ocorrer dentro deste período, nenhuma ação é tomada.
- Arquivo: `app/main.py`.

### 3. Filtro de Servidores (Blacklist)
Alguns nomes de servidores retornados pela API devem ser completamente ignorados da análise (ex: servidores de teste em uma plataforma não relevante).
- Regra: Ignorar qualquer servidor que possua a string `"PL-00"` em seu nome (ex: `APL-00`).
- Arquivo: `app/services/grafana_api.py`.

### 4. Lógica de Persistência e Anti-Spam
Para evitar que o sistema envie uma mensagem no WhatsApp a cada 5 minutos para um servidor que já está caído há horas, usamos a tabela `ServerState`.
- O sistema varre os servidores e compara o status (`ONLINE` / `OFFLINE`) do Zabbix com o último status gravado no Postgres.
- Só dispara a notificação se o status no banco era `ONLINE` (ou se o servidor for novo no banco) e a medição atual for `OFFLINE`.
- Registra `ServerEvent` sempre que o status de um servidor muda, compondo uma linha do tempo útil para auditoria.
- Arquivo: `app/services/state_manager.py`.

---

## 💬 Integração Chatbee (WhatsApp Meta Oficial)

Devido às políticas rigorosas da API Oficial do WhatsApp (Meta), os alertas são disparados por meio de **Templates Aprovados**.

- **Template Aprovado**: `automacao_aviso_queda_servidor`
- **Gatilho**: Disparado pela função `enviar_alerta_chatbee()` em `app/services/chatbee.py`.
- **Payload**: O objeto enviado em JSON (`template_data`) obedece restritamente aos blocos exigidos pelo Chatbee e usa Headers específicos para autenticação:
  - `api_access_token`
  - `Authorization`
  - `token`
  - `x-api-key`
- **Fuso Horário**: Todos os disparos (no campo `{{2}}` de horário) formatam a hora utilizando UTC-3 (`America/Sao_Paulo`) para não exibir GMT+0 nas mensagens.

---

## 🚀 Setup e Deploy

### 1. Variáveis de Ambiente (`.env`)
Você precisa criar o arquivo `.env` na raiz do projeto, contendo as variáveis obrigatórias:
```env
# Banco de Dados (Use 'db' como host caso suba no docker)
POSTGRES_USER=admin
POSTGRES_PASSWORD=senha_forte
POSTGRES_DB=monitor_db
DATABASE_URL=postgresql://admin:senha_forte@db:5432/monitor_db

# Integração Chatbee
CHATBEE_API_URL=https://hermes-api.chatbee.com.br/api/v1/external/queue/new-message
CHATBEE_API_TOKEN=seu_token_aqui
CHATBEE_USER_ID=7037
CHATBEE_DEPARTMENT_ID=1623
CHATBEE_CHANNEL_ID=2975

# Grafana API
GRAFANA_URL_LOGIN=https://monitor.suaempresa.com.br/login
# ...
```

### 2. Rodando o Servidor
O sistema utiliza o `docker-compose` para simplificar a orquestração do PostreSQL com a API.
```bash
# Sobe o banco e a aplicação com hot-reload (re-build de imagens)
docker-compose up -d --build
```
> **Atenção (Portas e Proxy)**: A API roda na porta `8005` para evitar colisão com outros serviços. Use um Reverse Proxy (como o Nginx Proxy Manager) para apontar seu domínio público para o IP `localhost:8005`.

### 3. Disparo Manual / Teste
- Para forçar a verificação (ignora o cron), envie um POST:
  ```bash
  curl -X POST http://localhost:8005/api/v1/verificar-agora
  ```
- Para testar apenas a comunicação com o Chatbee (chegada da mensagem), rode:
  ```bash
  docker exec -it undercar_api python testar_chatbee.py
  ```
