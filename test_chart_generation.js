#!/usr/bin/env node

/**
 * Script de teste para verificar a geração e envio automático de gráficos
 */

const { ChartGeneratorService } = require('./dist/application/services/ChartGeneratorService');

async function testChartGeneration() {
    console.log('🧪 TESTE DE GERAÇÃO E ENVIO DE GRÁFICOS');
    console.log('=' .repeat(50));
    console.log('');
    
    try {
        // Usar dados do CSV que já foi processado
        const messageId = 'wamid.HBgMNTU4NDk4NjcxMTg4FQIAEhgUM0FCNjk3QTZFNjZDQURCRDVFNzMA';
        const filename = 'vendas.csv';
        const from = '558498671188';
        
        console.log('📊 Dados do teste:');
        console.log(`   • Message ID: ${messageId}`);
        console.log(`   • Arquivo: ${filename}`);
        console.log(`   • De: ${from}`);
        console.log('');
        
        // Instanciar o serviço
        const chartService = new ChartGeneratorService();
        
        console.log('🚀 Iniciando geração de gráficos...');
        console.log('');
        
        // Gerar e enviar gráficos
        const result = await chartService.generateAndSendCharts(messageId, filename, from);
        
        console.log('');
        console.log('📋 RESULTADO DO TESTE:');
        console.log('=' .repeat(30));
        console.log(`✅ Sucesso: ${result.success}`);
        console.log(`📊 Gráficos: ${result.charts.length}`);
        console.log(`💬 Mensagem: ${result.message}`);
        
        if (result.error) {
            console.log(`❌ Erro: ${result.error}`);
        }
        
        if (result.charts.length > 0) {
            console.log('');
            console.log('📁 Gráficos gerados:');
            result.charts.forEach((chart, index) => {
                console.log(`   ${index + 1}. ${chart}`);
            });
        }
        
        console.log('');
        console.log('🎉 TESTE CONCLUÍDO!');
        
    } catch (error) {
        console.error('❌ Erro no teste:', error);
        console.error(error.stack);
    }
}

// Executar teste se chamado diretamente
if (require.main === module) {
    testChartGeneration().then(() => {
        console.log('');
        console.log('✅ Script de teste finalizado');
        process.exit(0);
    }).catch(error => {
        console.error('💥 Falha no teste:', error);
        process.exit(1);
    });
}

module.exports = { testChartGeneration };
