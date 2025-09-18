#!/bin/bash

echo "🧪 TESTE DE WEBHOOK - DataCompass WhatsApp"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Checklist de Configuração:${NC}"
echo ""
echo "1. ✅ Servidor rodando em localhost:3000"
echo "2. ⏳ Tunnel público ativo (ngrok/cloudflare)"
echo "3. ⏳ Webhook configurado no Facebook Developer Console"
echo "4. ⏳ Campos 'messages' marcados no webhook"
echo ""

# Testar se servidor está rodando
echo -e "${YELLOW}🔍 Testando servidor local...${NC}"
if curl -s http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}✅ Servidor local funcionando${NC}"
else
    echo -e "${RED}❌ Servidor local não está respondendo${NC}"
    exit 1
fi

# Testar webhook local
echo -e "${YELLOW}🔍 Testando webhook local...${NC}"
WEBHOOK_TEST=$(curl -s "http://localhost:3000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=datacompass_webhook_2025&hub.challenge=test123")
if [ "$WEBHOOK_TEST" = "test123" ]; then
    echo -e "${GREEN}✅ Webhook local funcionando${NC}"
else
    echo -e "${RED}❌ Webhook local com problema${NC}"
fi

echo ""
echo -e "${YELLOW}📱 Para testar recebimento de mensagens:${NC}"
echo "1. Configure o tunnel público"
echo "2. Atualize a URL no Facebook Developer Console"
echo "3. Envie uma mensagem pelo WhatsApp"
echo "4. Responda a mensagem"
echo "5. Execute: curl http://localhost:3000/api/messages/received"
echo ""

echo -e "${YELLOW}🔧 URLs importantes:${NC}"
echo "• Health Check: http://localhost:3000/health"
echo "• Mensagens Recebidas: http://localhost:3000/api/messages/received"
echo "• Status WhatsApp: http://localhost:3000/api/whatsapp/status"
echo "• Webhook Local: http://localhost:3000/api/whatsapp/webhook"
