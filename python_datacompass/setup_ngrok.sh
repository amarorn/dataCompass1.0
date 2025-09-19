#!/bin/bash

# Script para configurar ngrok para testes do WhatsApp webhook

echo "🔧 Configurando ngrok para WhatsApp webhook"
echo "============================================="

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não está instalado!"
    echo ""
    echo "📥 Instale o ngrok:"
    echo "   macOS: brew install ngrok/ngrok/ngrok"
    echo "   Linux: wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
    echo "   Windows: https://ngrok.com/download"
    echo ""
    echo "🔑 Configure sua authtoken:"
    echo "   ngrok config add-authtoken SEU_AUTHTOKEN"
    exit 1
fi

# Verificar se a aplicação está rodando
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Aplicação não está rodando na porta 8000!"
    echo "💡 Execute: python main_no_db.py"
    exit 1
fi

echo "✅ Aplicação detectada na porta 8000"

# Obter authtoken se não configurado
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo ""
    echo "🔑 Configure seu authtoken do ngrok:"
    echo "   Acesse: https://dashboard.ngrok.com/get-started/your-authtoken"
    read -p "   Digite seu authtoken: " authtoken
    
    if [ -n "$authtoken" ]; then
        ngrok config add-authtoken "$authtoken"
        echo "✅ Authtoken configurado!"
    else
        echo "❌ Authtoken é obrigatório para usar ngrok"
        exit 1
    fi
fi

# Iniciar ngrok
echo ""
echo "🚀 Iniciando ngrok..."
echo "   URL será: https://abc123.ngrok.io"
echo ""
echo "📋 Configure no Meta for Developers:"
echo "   Webhook URL: https://SEU_URL_NGROK.ngrok.io/api/whatsapp/webhook"
echo "   Verify Token: datacompass_webhook_2025"
echo ""
echo "⏹️  Pressione Ctrl+C para parar o ngrok"
echo ""

# Iniciar ngrok em background e capturar URL
ngrok http 8000 --log=stdout | while read line; do
    if [[ $line == *"started tunnel"* ]]; then
        url=$(echo "$line" | grep -o 'https://[^.]*\.ngrok\.io')
        echo ""
        echo "✅ Ngrok iniciado!"
        echo "🌐 URL pública: $url"
        echo "🔗 Webhook URL: $url/api/whatsapp/webhook"
        echo ""
        echo "📋 Copie esta URL e configure no Meta for Developers"
    fi
    echo "$line"
done
