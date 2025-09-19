#!/usr/bin/env python3
"""
Script para configurar credenciais do WhatsApp Business API
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("🔧 DataCompass - Configuração WhatsApp Business API")
    print("=" * 50)

def get_user_input():
    """Coleta informações do usuário"""
    print("\n📋 Por favor, forneça suas credenciais do WhatsApp Business API:")
    print("(Você pode encontrar essas informações em https://developers.facebook.com/)")
    
    # Coletar credenciais
    access_token = input("\n🔑 Access Token: ").strip()
    phone_number_id = input("📱 Phone Number ID: ").strip()
    webhook_secret = input("🔐 Webhook Secret: ").strip()
    
    # Verificar token existente
    verify_token = input("✅ Verify Token (padrão: datacompass_webhook_2025): ").strip()
    if not verify_token:
        verify_token = "datacompass_webhook_2025"
    
    return {
        'access_token': access_token,
        'phone_number_id': phone_number_id,
        'webhook_secret': webhook_secret,
        'verify_token': verify_token
    }

def validate_credentials(creds):
    """Valida as credenciais fornecidas"""
    print("\n🔍 Validando credenciais...")
    
    errors = []
    
    if not creds['access_token']:
        errors.append("Access Token é obrigatório")
    
    if not creds['phone_number_id']:
        errors.append("Phone Number ID é obrigatório")
    
    if not creds['webhook_secret']:
        errors.append("Webhook Secret é obrigatório")
    
    if not creds['verify_token']:
        errors.append("Verify Token é obrigatório")
    
    if errors:
        print("❌ Erros encontrados:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Credenciais válidas!")
    return True

def update_env_file(creds):
    """Atualiza o arquivo .env com as credenciais"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    print("\n📝 Atualizando arquivo .env...")
    
    # Ler arquivo atual
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Atualizar credenciais
    updated_lines = []
    for line in lines:
        if line.startswith('WHATSAPP_TOKEN='):
            updated_lines.append(f'WHATSAPP_TOKEN={creds["access_token"]}\n')
        elif line.startswith('WHATSAPP_PHONE_NUMBER_ID='):
            updated_lines.append(f'WHATSAPP_PHONE_NUMBER_ID={creds["phone_number_id"]}\n')
        elif line.startswith('WHATSAPP_WEBHOOK_VERIFY_TOKEN='):
            updated_lines.append(f'WHATSAPP_WEBHOOK_VERIFY_TOKEN={creds["verify_token"]}\n')
        elif line.startswith('WHATSAPP_WEBHOOK_SECRET='):
            updated_lines.append(f'WHATSAPP_WEBHOOK_SECRET={creds["webhook_secret"]}\n')
        else:
            updated_lines.append(line)
    
    # Escrever arquivo atualizado
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Arquivo .env atualizado com sucesso!")
    return True

def test_configuration():
    """Testa a configuração"""
    print("\n🧪 Testando configuração...")
    
    # Verificar se a aplicação está rodando
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicação está rodando")
        else:
            print("❌ Aplicação não está respondendo corretamente")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a aplicação: {e}")
        print("💡 Certifique-se de que a aplicação está rodando em http://localhost:8000")
        return False
    
    # Testar status do WhatsApp
    try:
        response = requests.get("http://localhost:8000/api/whatsapp/api/whatsapp/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('configured'):
                print("✅ WhatsApp configurado corretamente!")
                return True
            else:
                print("⚠️ WhatsApp não está totalmente configurado")
                print(f"   Status: {data}")
                return False
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {e}")
        return False

def print_next_steps():
    """Imprime próximos passos"""
    print("\n🚀 Próximos Passos:")
    print("1. Configure o webhook no Meta for Developers:")
    print("   - URL: https://seu-dominio.com/api/whatsapp/webhook")
    print("   - Verify Token: datacompass_webhook_2025")
    print("   - Campos: messages, message_status")
    print()
    print("2. Para testes locais, use ngrok:")
    print("   - ngrok http 8000")
    print("   - Use a URL HTTPS gerada no webhook")
    print()
    print("3. Reinicie a aplicação para carregar as novas credenciais")
    print()
    print("4. Teste enviando uma mensagem:")
    print("   curl -X POST http://localhost:8000/api/whatsapp/api/whatsapp/send \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"to\": \"5511999999999\", \"message\": \"Teste\"}'")

def main():
    print_banner()
    
    # Verificar se está no diretório correto
    if not Path(".env").exists():
        print("❌ Execute este script no diretório python_datacompass/")
        sys.exit(1)
    
    # Coletar credenciais
    creds = get_user_input()
    
    # Validar credenciais
    if not validate_credentials(creds):
        sys.exit(1)
    
    # Atualizar arquivo .env
    if not update_env_file(creds):
        sys.exit(1)
    
    # Testar configuração
    test_configuration()
    
    # Próximos passos
    print_next_steps()
    
    print("\n✅ Configuração concluída!")

if __name__ == "__main__":
    main()
