#!/bin/bash

echo "🧪 TESTE DE TUNNEL CLOUDFLARE - WhatsApp Webhook"
echo "=============================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}❌ Uso: ./test-tunnel.sh https://sua-url-cloudflare.trycloudflare.com${NC}"
    echo ""
    echo -e "${YELLOW}📋 Exemplo:${NC}"
    echo "./test-tunnel.sh https://abc123.trycloudflare.com"
    echo ""
    exit 1
fi

TUNNEL_URL="$1"
WEBHOOK_URL="$TUNNEL_URL/api/whatsapp/webhook"

echo -e "${BLUE}🔍 Testando tunnel: $TUNNEL_URL${NC}"
echo ""

# Teste 1: Health Check
echo -e "${YELLOW}1. Testando Health Check...${NC}"
if curl -s "$TUNNEL_URL/health" | grep -q "OK"; then
    echo -e "${GREEN}   ✅ Health check funcionando${NC}"
else
    echo -e "${RED}   ❌ Health check falhou${NC}"
    exit 1
fi

# Teste 2: Webhook Verification
echo -e "${YELLOW}2. Testando Webhook Verification...${NC}"
WEBHOOK_TEST=$(curl -s "$WEBHOOK_URL?hub.mode=subscribe&hub.verify_token=datacompass_webhook_2025&hub.challenge=test123")
if [ "$WEBHOOK_TEST" = "test123" ]; then
    echo -e "${GREEN}   ✅ Webhook verification funcionando${NC}"
else
    echo -e "${RED}   ❌ Webhook verification falhou${NC}"
    echo "   Resposta: $WEBHOOK_TEST"
    exit 1
fi

# Teste 3: Status da API WhatsApp
echo -e "${YELLOW}3. Testando Status WhatsApp API...${NC}"
if curl -s "$TUNNEL_URL/api/whatsapp/status" | grep -q "configured.*true"; then
    echo -e "${GREEN}   ✅ WhatsApp API configurada${NC}"
else
    echo -e "${RED}   ❌ WhatsApp API não configurada${NC}"
fi

echo ""
echo -e "${GREEN}🎉 TUNNEL FUNCIONANDO PERFEITAMENTE!${NC}"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo "1. Acesse: https://developers.facebook.com/apps/"
echo "2. Vá em: WhatsApp > Configuration > Webhooks"
echo "3. Configure:"
echo -e "   ${BLUE}URL:${NC} $WEBHOOK_URL"
echo -e "   ${BLUE}Token:${NC} datacompass_webhook_2025"
echo "4. ✅ Marque os campos:"
echo "   • messages (OBRIGATÓRIO)"
echo "   • message_deliveries"  
echo "   • message_reads"
echo "5. Clique em 'Verify and Save'"
echo ""
echo -e "${YELLOW}🧪 Para testar depois:${NC}"
echo "• Envie uma mensagem pelo WhatsApp"
echo "• Responda a mensagem"
echo "• Execute: curl http://localhost:3000/api/messages/received"
echo ""
