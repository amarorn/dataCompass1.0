# 📋 Exemplo Prático - Configuração WhatsApp Business API

## 🎯 Cenário de Exemplo

Vamos configurar o WhatsApp Business API para um negócio fictício:

**Empresa**: Loja Virtual TechStore  
**Número**: +55 11 99999-9999  
**Domínio**: techstore.com.br

## 🔧 Passo a Passo Prático

### **1. Obter Credenciais no Meta for Developers**

#### **1.1 Acessar Meta for Developers**
1. Vá para: https://developers.facebook.com/
2. Faça login com sua conta Meta Business
3. Clique em "Meus Apps" → "Criar App"

#### **1.2 Criar Aplicação**
```
Nome do App: TechStore WhatsApp
Tipo: Negócios
Finalidade: Outras
Email: contato@techstore.com.br
```

#### **1.3 Adicionar WhatsApp Business API**
1. No painel da aplicação, clique "Adicionar Produto"
2. Selecione "WhatsApp Business API"
3. Clique "Configurar"

#### **1.4 Configurar Número**
1. Adicione o número: +55 11 99999-9999
2. Verifique via SMS
3. Aguarde aprovação (pode levar alguns minutos)

#### **1.5 Obter Credenciais**
Após configuração, você terá:

```bash
# Exemplo de credenciais (NÃO use essas - são fictícias)
Access Token: EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Phone Number ID: 123456789012345
Webhook Secret: abc123def456ghi789jkl012mno345pqr678stu901vwx234
```

### **2. Configurar Webhook**

#### **2.1 Para Testes Locais (ngrok)**

```bash
# Instalar ngrok
brew install ngrok/ngrok/ngrok  # macOS
# ou baixar de https://ngrok.com/download

# Configurar authtoken
ngrok config add-authtoken SEU_AUTHTOKEN_AQUI

# Expor aplicação local
ngrok http 8000
```

**Resultado**:
```
Session Status: online
Web Interface: http://127.0.0.1:4040
Forwarding: https://abc123def.ngrok.io -> http://localhost:8000
```

#### **2.2 Configurar no Meta**
1. **URL do Webhook**: `https://abc123def.ngrok.io/api/whatsapp/webhook`
2. **Verify Token**: `datacompass_webhook_2025`
3. **Campos**: `messages`, `message_status`

### **3. Usar Script de Configuração**

```bash
# Navegar para o diretório
cd /Users/joseamaro/Documents/Projeto/dataCompass1.0/python_datacompass

# Executar script de configuração
python setup_whatsapp.py
```

**Entrada de exemplo**:
```
🔧 DataCompass - Configuração WhatsApp Business API
==================================================

📋 Por favor, forneça suas credenciais do WhatsApp Business API:

🔑 Access Token: EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📱 Phone Number ID: 123456789012345
🔐 Webhook Secret: abc123def456ghi789jkl012mno345pqr678stu901vwx234
✅ Verify Token (padrão: datacompass_webhook_2025): datacompass_webhook_2025
```

### **4. Testar Configuração**

#### **4.1 Verificar Status**
```bash
curl -X GET "http://localhost:8000/api/whatsapp/api/whatsapp/status"
```

**Resposta esperada**:
```json
{
  "success": true,
  "message": "WhatsApp integration status",
  "data": {
    "configured": true,
    "configuration": {
      "access_token": true,
      "phone_number_id": true,
      "webhook_secret": true,
      "configured": true
    },
    "environment": "production"
  }
}
```

#### **4.2 Enviar Mensagem de Teste**
```bash
curl -X POST "http://localhost:8000/api/whatsapp/api/whatsapp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "5511999999999",
    "message": "Olá! Esta é uma mensagem de teste da TechStore. 🛍️",
    "type": "text"
  }'
```

**Resposta esperada**:
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "to": "5511999999999",
    "message": "Olá! Esta é uma mensagem de teste da TechStore. 🛍️",
    "message_id": "wamid.HBgNNTUxMTk5OTk5OTk5FQIAEhgUM0E4MjlGNzY4M0Y4QjE4RkI4QzAA",
    "simulated": false
  }
}
```

### **5. Configurar para Produção**

#### **5.1 Domínio Próprio**
```bash
# Configurar DNS
# A record: api.techstore.com.br -> IP_DO_SERVIDOR

# Configurar SSL (Let's Encrypt)
certbot --nginx -d api.techstore.com.br

# Atualizar webhook no Meta
# URL: https://api.techstore.com.br/api/whatsapp/webhook
```

#### **5.2 Deploy com Docker**
```bash
# Build da imagem
docker build -t datacompass-python .

# Executar container
docker run -d \
  -p 8000:8000 \
  -e WHATSAPP_TOKEN="EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -e WHATSAPP_PHONE_NUMBER_ID="123456789012345" \
  -e WHATSAPP_WEBHOOK_SECRET="abc123def456ghi789jkl012mno345pqr678stu901vwx234" \
  --name datacompass-app \
  datacompass-python
```

## 🧪 Casos de Teste

### **Teste 1: Mensagem Simples**
```bash
curl -X POST "http://localhost:8000/api/whatsapp/api/whatsapp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "5511999999999",
    "message": "Olá! Como posso ajudar você hoje?",
    "type": "text"
  }'
```

### **Teste 2: Mensagem com Template**
```bash
curl -X POST "http://localhost:8000/api/whatsapp/api/whatsapp/template" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "5511999999999",
    "template_name": "hello_world",
    "language_code": "pt_BR",
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "João"
          }
        ]
      }
    ]
  }'
```

### **Teste 3: Processamento de Mensagem**
```bash
curl -X POST "http://localhost:8000/api/whatsapp/api/whatsapp/test" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quero comprar um produto de R$ 150,00",
    "from_number": "5511999999999"
  }'
```

## 📊 Monitoramento

### **Logs da Aplicação**
```bash
# Ver logs em tempo real
docker logs -f datacompass-app

# Ou se executando localmente
tail -f logs/app.log
```

### **Métricas do WhatsApp**
1. Acesse: https://business.facebook.com/
2. Vá para "WhatsApp Manager"
3. Clique em "Analytics"
4. Monitore:
   - Mensagens enviadas
   - Taxa de entrega
   - Respostas dos clientes

## 🚨 Troubleshooting

### **Problema: "Invalid Access Token"**
```bash
# Verificar token no Meta for Developers
# Gerar novo token se necessário
# Atualizar arquivo .env
```

### **Problema: "Webhook Verification Failed"**
```bash
# Verificar se ngrok está rodando
# Confirmar URL no Meta
# Testar manualmente:
curl "https://abc123def.ngrok.io/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=datacompass_webhook_2025"
```

### **Problema: "Phone Number Not Verified"**
```bash
# Verificar no Meta Business Manager
# Completar verificação via SMS
# Aguardar alguns minutos
```

## ✅ Checklist Final

- [ ] ✅ Aplicação criada no Meta for Developers
- [ ] ✅ WhatsApp Business API configurado
- [ ] ✅ Número de telefone verificado
- [ ] ✅ Credenciais obtidas (Access Token, Phone Number ID, Webhook Secret)
- [ ] ✅ Webhook configurado (ngrok ou domínio próprio)
- [ ] ✅ Arquivo .env atualizado
- [ ] ✅ Aplicação reiniciada
- [ ] ✅ Teste de envio realizado com sucesso
- [ ] ✅ Webhook verificado
- [ ] ✅ Logs monitorados

---

**🎉 Parabéns! Sua integração WhatsApp Business API está funcionando!**
