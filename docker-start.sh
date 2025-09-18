#!/bin/bash

# Script para inicializar DataCompass 1.0 com MongoDB

echo "🚀 Iniciando DataCompass 1.0 com MongoDB"
echo "======================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando .env.docker..."
    cp .env.docker .env
    echo "📝 IMPORTANTE: Edite o arquivo .env com seus tokens do WhatsApp!"
    echo ""
    echo "Tokens necessários:"
    echo "- WHATSAPP_TOKEN"
    echo "- WHATSAPP_PHONE_NUMBER_ID"
    echo "- FACEBOOK_APP_ID"
    echo "- FACEBOOK_APP_SECRET"
    echo ""
    read -p "Pressione Enter após configurar o arquivo .env..."
fi

# Criar diretório temp se não existir
mkdir -p temp

echo "🏗️  Construindo containers..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d

echo "⏳ Aguardando MongoDB inicializar..."
sleep 10

echo "🔍 Verificando status dos serviços..."
docker-compose ps

echo ""
echo "✅ DataCompass 1.0 iniciado com sucesso!"
echo ""
echo "🌐 Serviços disponíveis:"
echo "   • API: http://localhost:3000"
echo "   • Health: http://localhost:3000/health"
echo "   • MongoDB Express: http://localhost:8081 (admin/datacompass2025)"
echo ""
echo "📊 APIs principais:"
echo "   • GET /api/whatsapp/csv - Lista CSVs processados"
echo "   • GET /api/messages/history - Histórico de mensagens"
echo "   • POST /api/whatsapp/webhook - Webhook do WhatsApp"
echo ""
echo "🔧 Comandos úteis:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Parar: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo ""
echo "📱 Configure seu webhook do WhatsApp para:"
echo "   https://SEU_DOMINIO/api/whatsapp/webhook"
