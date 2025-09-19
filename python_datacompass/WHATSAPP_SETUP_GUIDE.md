# 🔧 Guia de Configuração - WhatsApp Business API

## 📋 Pré-requisitos

### 1. **Conta Meta Business**
- Acesse: https://business.facebook.com/
- Crie uma conta business
- Verifique sua conta com documentos empresariais

### 2. **Número de Telefone**
- Número comercial verificado
- Não pode ser número pessoal
- Recomendado: número fixo ou celular empresarial

### 3. **Domínio Público**
- Para produção: domínio próprio com HTTPS
- Para testes: usar ngrok (https://ngrok.com/)

## 🚀 Passo a Passo Detalhado

### **Passo 1: Criar Aplicação no Meta for Developers**

1. **Acesse**: https://developers.facebook.com/
2. **Clique em**: "Meus Apps" → "Criar App"
3. **Selecione**: "Negócios" → "Criar"
4. **Preencha**:
   - Nome do App: `DataCompass WhatsApp`
   - Email de contato: seu email
   - Finalidade: "Outras"

### **Passo 2: Adicionar WhatsApp Business API**

1. **No painel da aplicação**:
   - Clique em "Adicionar Produto"
   - Procure "WhatsApp Business API"
   - Clique em "Configurar"

2. **Configurações iniciais**:
   - Selecione sua conta business
   - Adicione número de telefone
   - Verifique o número via SMS

### **Passo 3: Obter Credenciais**

#### **3.1 Access Token**
1. **No painel WhatsApp**:
   - Vá para "API Setup"
   - Copie o "Temporary access token" (válido por 24h)
   - Para produção: gere um token permanente

#### **3.2 Phone Number ID**
1. **Na mesma página**:
   - Copie o "Phone number ID"
   - Este é um número único para seu número de telefone

#### **3.3 Webhook Secret**
1. **Configure o webhook**:
   - URL: `https://seu-dominio.com/api/whatsapp/webhook`
   - Verify Token: `datacompass_webhook_2025`
   - Webhook Secret: será gerado automaticamente

### **Passo 4: Configurar Webhook**

#### **4.1 Para Testes (usando ngrok)**

```bash
# Instalar ngrok
npm install -g ngrok

# Expor aplicação local
ngrok http 8000

# Copiar URL HTTPS gerada
# Exemplo: https://abc123.ngrok.io
```

#### **4.2 Configurar no Meta**
1. **URL do Webhook**: `https://sua-url-ngrok.com/api/whatsapp/webhook`
2. **Verify Token**: `datacompass_webhook_2025`
3. **Campos do Webhook**: `messages`, `message_status`

### **Passo 5: Atualizar Arquivo .env**

```bash
# WhatsApp Business API Configuration
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_WEBHOOK_VERIFY_TOKEN=datacompass_webhook_2025
WHATSAPP_WEBHOOK_SECRET=seu-webhook-secret-aqui
```

## 🔐 Segurança e Melhores Práticas

### **1. Tokens de Acesso**
- **Temporário**: Válido por 24h (para testes)
- **Permanente**: Para produção (nunca expire)
- **Renovação**: Configure renovação automática

### **2. Webhook Security**
- Sempre use HTTPS
- Valide assinatura do webhook
- Implemente rate limiting

### **3. Backup de Credenciais**
- Armazene em variáveis de ambiente
- Use serviços de secrets (AWS Secrets Manager, etc.)
- Nunca commite credenciais no código

## 🧪 Testando a Configuração

### **1. Verificar Status**
```bash
curl -X GET "http://localhost:8000/api/whatsapp/status"
```

### **2. Enviar Mensagem de Teste**
```bash
curl -X POST "http://localhost:8000/api/whatsapp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "5511999999999",
    "message": "Teste de configuração",
    "type": "text"
  }'
```

### **3. Verificar Webhook**
```bash
curl -X GET "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=datacompass_webhook_2025"
```

## 📊 Monitoramento

### **1. Logs da Aplicação**
- Monitore logs para erros de API
- Verifique rate limits
- Acompanhe delivery status

### **2. Meta Business Manager**
- Monitore uso da API
- Verifique qualidade da mensagem
- Acompanhe métricas de entrega

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **1. "Invalid Access Token"**
- Verifique se o token está correto
- Confirme se não expirou
- Gere um novo token se necessário

#### **2. "Webhook Verification Failed"**
- Verifique se a URL está acessível
- Confirme o verify token
- Teste com curl manualmente

#### **3. "Phone Number Not Verified"**
- Complete a verificação via SMS
- Aguarde alguns minutos após verificação
- Verifique no Meta Business Manager

#### **4. "Rate Limit Exceeded"**
- Aguarde antes de enviar mais mensagens
- Implemente backoff exponencial
- Monitore limites no painel Meta

## 📞 Suporte

### **Recursos Oficiais**
- **Documentação**: https://developers.facebook.com/docs/whatsapp
- **Suporte Meta**: https://business.facebook.com/support
- **Comunidade**: https://developers.facebook.com/community

### **Limites da API**
- **Mensagens gratuitas**: 1.000 por mês
- **Rate limit**: 250 mensagens por segundo
- **Tamanho da mensagem**: 4.096 caracteres

## ✅ Checklist de Configuração

- [ ] Conta Meta Business criada
- [ ] Aplicação criada no Meta for Developers
- [ ] WhatsApp Business API adicionado
- [ ] Número de telefone verificado
- [ ] Access token obtido
- [ ] Phone Number ID copiado
- [ ] Webhook configurado
- [ ] Arquivo .env atualizado
- [ ] Teste de envio realizado
- [ ] Webhook verificado
- [ ] Logs monitorados

---

**⚠️ Importante**: Mantenha suas credenciais seguras e nunca as compartilhe publicamente!
