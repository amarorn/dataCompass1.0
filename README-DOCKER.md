# 🐳 DataCompass 1.0 - Docker Setup

Sistema completo com MongoDB para análise de dados via WhatsApp.

## 🚀 Início Rápido

### 1. Pré-requisitos
- Docker
- Docker Compose
- Tokens do WhatsApp Business API

### 2. Configuração

```bash
# Copiar configurações
cp .env.docker .env

# Editar com seus tokens
nano .env
```

### 3. Inicializar

```bash
# Usar script automático
./docker-start.sh

# Ou manualmente
docker-compose up -d
```

## 📊 Serviços Incluídos

### 🌐 Aplicação Node.js
- **Porta:** 3000
- **Health:** http://localhost:3000/health
- **Webhook:** http://localhost:3000/api/whatsapp/webhook

### 🗄️ MongoDB
- **Porta:** 27017
- **Database:** datacompass
- **Usuário:** datacompass_user
- **Senha:** datacompass_app_2025

### 🖥️ MongoDB Express (Interface Web)
- **Porta:** 8081
- **URL:** http://localhost:8081
- **Login:** admin / datacompass2025

## 📋 APIs Principais

### CSV Processing
```bash
# Listar CSVs processados
GET /api/whatsapp/csv

# Dados específicos do CSV
GET /api/whatsapp/csv/:id

# Análise detalhada
GET /api/whatsapp/csv/:id/analysis
```

### Mensagens
```bash
# Histórico completo
GET /api/messages/history

# Mensagens recebidas
GET /api/messages/received

# Mensagens por usuário
GET /api/messages/user/:phone
```

## 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do MongoDB
docker-compose logs -f mongo

# Parar serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reiniciar apenas a aplicação
docker-compose restart app

# Reconstruir e reiniciar
docker-compose up -d --build
```

## 📱 Configuração WhatsApp

### Webhook URL
```
https://SEU_DOMINIO/api/whatsapp/webhook
```

### Verify Token
```
datacompass_webhook_2025
```

### Eventos Necessários
- `messages` ✅

## 🗂️ Estrutura de Dados

### CSV Processado
```javascript
{
  "_id": "mongodb_id",
  "id": "message_id",
  "filename": "vendas.csv",
  "from": "558498671188",
  "processedAt": "2025-09-18T10:00:00Z",
  "data": [...], // Dados do CSV
  "summary": {
    "rows": 100,
    "columns": ["nome", "valor", "data"],
    "insights": ["Dataset médio", "Dados completos"]
  },
  "analysis": {...} // Análise detalhada
}
```

### Mensagem
```javascript
{
  "_id": "mongodb_id",
  "id": "wamid.xxx",
  "from": "558498671188",
  "message": "Texto da mensagem",
  "timestamp": "2025-09-18T10:00:00Z",
  "type": "received" // ou "sent"
}
```

## 🔒 Segurança

- ✅ Usuário não-root no container
- ✅ MongoDB com autenticação
- ✅ Variáveis de ambiente para secrets
- ✅ Health checks configurados
- ✅ Network isolation

## 🚨 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs app

# Verificar configurações
docker-compose config
```

### MongoDB não conecta
```bash
# Verificar se MongoDB está rodando
docker-compose ps mongo

# Verificar logs do MongoDB
docker-compose logs mongo

# Testar conexão
docker-compose exec mongo mongosh -u admin -p datacompass2025
```

### Webhook não recebe mensagens
1. Verificar se URL pública está configurada
2. Verificar se webhook está configurado no Facebook
3. Verificar logs da aplicação
4. Testar endpoint manualmente

## 📈 Monitoramento

### Métricas Disponíveis
- Total de CSVs processados
- Mensagens recebidas/enviadas
- Usuários ativos
- Status da aplicação

### Logs Estruturados
- Timestamp
- Nível (info, error, debug)
- Contexto (webhook, csv, database)
- Dados relevantes

## 🔄 Backup e Restore

### Backup MongoDB
```bash
# Backup completo
docker-compose exec mongo mongodump -u admin -p datacompass2025 --authenticationDatabase admin -d datacompass -o /backup

# Copiar backup
docker cp datacompass-mongo:/backup ./backup
```

### Restore MongoDB
```bash
# Copiar backup
docker cp ./backup datacompass-mongo:/backup

# Restaurar
docker-compose exec mongo mongorestore -u admin -p datacompass2025 --authenticationDatabase admin -d datacompass /backup/datacompass
```

## 🎯 Próximos Passos

1. ✅ Sistema básico funcionando
2. ✅ MongoDB integrado
3. ✅ CSV processing
4. ✅ APIs completas
5. 🔄 Deploy em produção
6. 📊 Dashboard web
7. 🤖 IA para insights avançados

---

**🎉 Seu DataCompass 1.0 está pronto para processar CSVs via WhatsApp com persistência MongoDB!**
