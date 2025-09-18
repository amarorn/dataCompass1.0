#!/bin/bash

echo "🔧 CONFIGURAÇÃO AUTOMÁTICA DO WEBHOOK WHATSAPP"
echo "=============================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}❌ Uso: ./configure-webhook.sh https://sua-url-cloudflare.trycloudflare.com${NC}"
    echo ""
    echo -e "${YELLOW}📋 Exemplo:${NC}"
    echo "./configure-webhook.sh https://xyz789-abc123.trycloudflare.com"
    echo ""
    exit 1
fi

TUNNEL_URL="$1"
WEBHOOK_URL="$TUNNEL_URL/api/whatsapp/webhook"

echo -e "${BLUE}🌐 URL do Tunnel: $TUNNEL_URL${NC}"
echo -e "${BLUE}📡 URL do Webhook: $WEBHOOK_URL${NC}"
echo ""

# Executar teste completo
echo -e "${YELLOW}🧪 Executando teste completo...${NC}"
./test-tunnel.sh "$TUNNEL_URL"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 TUNNEL FUNCIONANDO PERFEITAMENTE!${NC}"
    echo ""
    echo -e "${YELLOW}📋 CONFIGURAÇÃO NO FACEBOOK DEVELOPER CONSOLE:${NC}"
    echo "=============================================="
    echo ""
    echo -e "${BLUE}1. Acesse:${NC} https://developers.facebook.com/apps/"
    echo -e "${BLUE}2. Vá em:${NC} WhatsApp > Configuration > Webhooks"
    echo ""
    echo -e "${YELLOW}3. Configure os campos:${NC}"
    echo -e "   ${GREEN}Callback URL:${NC} $WEBHOOK_URL"
    echo -e "   ${GREEN}Verify Token:${NC} datacompass_webhook_2025"
    echo ""
    echo -e "${YELLOW}4. ✅ MARQUE ESTES CAMPOS (OBRIGATÓRIO):${NC}"
    echo "   ☑️ messages          (para receber respostas dos usuários)"
    echo "   ☑️ message_deliveries (status de entrega)"
    echo "   ☑️ message_reads     (status de leitura)"
    echo ""
    echo -e "${YELLOW}5. Clique em:${NC} 'Verify and Save'"
    echo ""
    echo -e "${YELLOW}🧪 TESTE FINAL:${NC}"
    echo "1. Envie uma mensagem template via API"
    echo "2. Responda no seu WhatsApp"
    echo -e "3. Execute: ${BLUE}curl http://localhost:3000/api/messages/received${NC}"
    echo ""
    echo -e "${GREEN}✨ Depois disso, as respostas aparecerão automaticamente na API!${NC}"
    echo ""
else
    echo -e "${RED}❌ Erro no teste do tunnel. Verifique se está rodando corretamente.${NC}"
fi
