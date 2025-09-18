#!/usr/bin/env node

/**
 * Teste simples da funcionalidade de gráficos
 */

console.log('🧪 TESTE SIMPLES DE GRÁFICOS');
console.log('============================');
console.log('');

// Simular dados de um CSV processado
const testData = {
    messageId: 'wamid.HBgMNTU4NDk4NjcxMTg4FQIAEhgUM0FCNjk3QTZFNjZDQURCRDVFNzMA',
    filename: 'vendas.csv',
    from: '558498671188'
};

console.log('📊 Dados do teste:');
console.log(`   • Arquivo: ${testData.filename}`);
console.log(`   • De: ${testData.from}`);
console.log(`   • Message ID: ${testData.messageId.substring(0, 30)}...`);
console.log('');

console.log('🔄 Iniciando teste...');
console.log('');

// Teste 1: Verificar se a API está respondendo
console.log('1️⃣ Testando API...');
const http = require('http');

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/whatsapp/raw',
    method: 'GET'
};

const req = http.request(options, (res) => {
    if (res.statusCode === 200) {
        console.log('   ✅ API respondendo');
        
        // Teste 2: Testar geração de gráficos (simulado)
        console.log('');
        console.log('2️⃣ Testando geração de gráficos...');
        
        // Simular processo de geração
        setTimeout(() => {
            console.log('   📊 Gráfico 1: Distribuições (simulado)');
            console.log('   📈 Gráfico 2: Resumo Executivo (simulado)');
            console.log('   💡 Gráfico 3: Insights (simulado)');
            console.log('');
            
            // Teste 3: Simular envio
            console.log('3️⃣ Simulando envio via WhatsApp...');
            console.log('   📱 Enviando para:', testData.from);
            console.log('   📎 3 gráficos PNG');
            console.log('   💬 Mensagens explicativas');
            console.log('');
            
            console.log('✅ TESTE CONCLUÍDO!');
            console.log('');
            console.log('🚀 COMO TESTAR DE VERDADE:');
            console.log('1. Envie um CSV via WhatsApp');
            console.log('2. Aguarde mensagem "Processamento Iniciado"');
            console.log('3. Receba os gráficos automaticamente');
            console.log('4. Veja a confirmação final');
            console.log('');
            console.log('📱 Número para teste: +55 84 99867-1188');
            console.log('🔗 Webhook deve estar configurado no Facebook');
            
        }, 2000);
        
    } else {
        console.log('   ❌ API não está respondendo corretamente');
        console.log('   Status:', res.statusCode);
    }
});

req.on('error', (err) => {
    console.log('   ❌ Erro ao conectar com a API:', err.message);
    console.log('');
    console.log('🔧 SOLUÇÕES:');
    console.log('1. Verifique se o servidor está rodando: npm start');
    console.log('2. Teste manualmente: curl http://localhost:3000/api/whatsapp/raw');
});

req.end();
