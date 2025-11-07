# Instruções de Instalação

## Pré-requisitos
- Docker e Docker Compose instalados

## Instalação e Execução

### Subir todos os serviços (Backend + Frontend + Database)
```bash
docker compose up --build
```

Isso irá:
1. Construir e iniciar o banco PostgreSQL (porta 5432)
2. Construir e iniciar o backend Django (porta 80)
3. Construir e iniciar o frontend React (porta 8000)
4. Aplicar migrações automaticamente

### Acessar as aplicações
- **Frontend React**: http://localhost:8000
- **Backend API**: http://localhost:80
- **Banco PostgreSQL**: localhost:5432

## Estrutura do Projeto

```
realmate_challenge/
 ├── conversations/
 │    ├── models.py
 │    ├── serializers.py
 │    ├── views.py
 │    ├── urls.py
 │    └── services/
 │         └── webhook_service.py
 ├── logs/
 │    └── webhook.log
frontend/
 ├── src/
 │    ├── App.js
 │    └── components/
 │         ├── ConversationList.js
 │         └── ConversationDetail.js
```

## Endpoints da API

### Webhook (POST)
```bash
curl -X POST http://localhost:80/webhook/ \
-H "Content-Type: application/json" \
-d '{"type": "NEW_CONVERSATION", "timestamp": "2025-02-21T10:20:41.349308", "data": {"id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"}}'
```

### Listar conversas (GET)
```bash
curl http://localhost:80/conversations/
```

### Detalhes da conversa (GET)
```bash
curl http://localhost:80/conversations/6a41b347-8d80-4ce9-84ba-7af66f369f6a/
```

#### Formato dos Webhooks

Os eventos virão no seguinte formato:

##### Novo evento de conversa iniciada

```json
{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-02-21T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

##### Novo evento de mensagem recebida

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:42.349308",
    "data": {
        "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
        "direction": "RECEIVED",
        "content": "Olá, tudo bem?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

##### Novo evento de mensagem enviada

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:44.349308",
    "data": {
        "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
        "direction": "SENT",
        "content": "Tudo ótimo e você?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

##### Novo evento de conversa encerrada

```json
{
    "type": "CLOSE_CONVERSATION",
    "timestamp": "2025-02-21T10:20:45.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

## Eventos do Webhook

### NEW_CONVERSATION
```json
{
  "type": "NEW_CONVERSATION",
  "timestamp": "2025-02-21T10:20:41.349308",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

### NEW_MESSAGE
```json
{
  "type": "NEW_MESSAGE",
  "timestamp": "2025-02-21T10:20:44.349308",
  "data": {
    "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
    "direction": "SENT",
    "content": "Olá! Como posso ajudar?",
    "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

### CLOSE_CONVERSATION
```json
{
  "type": "CLOSE_CONVERSATION",
  "timestamp": "2025-02-21T10:25:00.000000",
  "data": {
    "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
  }
}
```

## Logs

Os logs estruturados são salvos em duas formas:

1. **Tabela do banco de dados**: Os logs são armazenados na tabela `WebhookLog` no PostgreSQL, permitindo consultas e análises estruturadas.

2. **Arquivo de log** (opcional): Os logs também podem ser salvos em `logs/webhook.log` no formato JSON.

Formato dos logs:

```json
{
  "event": "NEW_MESSAGE",
  "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
  "status": "success",
  "timestamp": "2025-11-05T10:06:00",
  "message": "Mensagem criada com sucesso na conversa 6a41b347-8d80-4ce9-84ba-7af66f369f6a"
}
```

Os logs podem ser visualizados e gerenciados através do Django Admin em `http://localhost:80/admin/`.

## Frontend

O frontend React está disponível em http://localhost:8000 e permite:
- Listar todas as conversas
- Ver detalhes de uma conversa específica
- Visualizar mensagens com direcionalidade (SENT/RECEIVED)
- Ver status das conversas (OPEN/CLOSED)

## Desenvolvimento Local (sem Docker)

### Backend
```bash
poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```


