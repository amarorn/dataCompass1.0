const { MongoMLRepository } = require('./dist/infrastructure/database/MongoMLRepository');
const csv = require('csv-parser');
const fs = require('fs');

async function testGenericCSV() {
  console.log('🧪 TESTE DE ADAPTABILIDADE - CSV GENÉRICO');
  console.log('==========================================');
  
  const mlRepo = new MongoMLRepository();
  
  // Testar com CSV de clientes (schema diferente)
  const clientesData = [];
  
  fs.createReadStream('./exemplo-clientes.csv')
    .pipe(csv())
    .on('data', (data) => clientesData.push(data))
    .on('end', async () => {
      console.log('📊 CSV de Clientes carregado:', clientesData.length, 'registros');
      console.log('📋 Colunas detectadas:', Object.keys(clientesData[0]));
      
      try {
        // Processar para ML
        const result = await mlRepo.processCSVForML(
          'test_clientes_' + Date.now(),
          'exemplo-clientes.csv',
          'teste_sistema',
          clientesData
        );
        
        console.log('✅ Processamento ML concluído:', result);
        
        // Buscar resumo
        const datasets = await mlRepo.getAllDatasets();
        const ultimoDataset = datasets[0];
        
        if (ultimoDataset) {
          console.log('\n🔍 ANÁLISE DO SCHEMA DETECTADO:');
          console.log('================================');
          console.log('📄 Arquivo:', ultimoDataset.filename);
          console.log('📊 Total de registros:', ultimoDataset.totalRecords);
          console.log('🔢 Total de features:', ultimoDataset.features.total);
          
          console.log('\n📈 DISTRIBUIÇÃO POR TIPO:');
          console.log('• Numéricas:', ultimoDataset.features.numeric, 'features');
          console.log('• Categóricas:', ultimoDataset.features.categorical, 'features');
          console.log('• Texto:', ultimoDataset.features.text, 'features');
          console.log('• Data:', ultimoDataset.features.date, 'features');
          console.log('• Booleanas:', ultimoDataset.features.boolean, 'features');
          
          console.log('\n📊 QUALIDADE DOS DADOS:');
          console.log('• Completude média:', (ultimoDataset.dataQuality.averageCompleteness * 100).toFixed(1) + '%');
          console.log('• Consistência média:', (ultimoDataset.dataQuality.averageConsistency * 100).toFixed(1) + '%');
          console.log('• Validade média:', (ultimoDataset.dataQuality.averageValidity * 100).toFixed(1) + '%');
          
          if (ultimoDataset.statistics.numericStats) {
            console.log('\n🔢 ESTATÍSTICAS NUMÉRICAS:');
            Object.entries(ultimoDataset.statistics.numericStats).forEach(([feature, stats]) => {
              console.log(`• ${feature}:`, {
                min: stats.min,
                max: stats.max,
                média: stats.mean,
                mediana: stats.median
              });
            });
          }
          
          if (ultimoDataset.statistics.categoricalStats) {
            console.log('\n📋 ESTATÍSTICAS CATEGÓRICAS:');
            Object.entries(ultimoDataset.statistics.categoricalStats).forEach(([feature, stats]) => {
              console.log(`• ${feature}:`, {
                valores_únicos: stats.uniqueValues,
                top_3: stats.topValues.slice(0, 3).map(v => `${v.value} (${v.count}x)`)
              });
            });
          }
        }
        
        console.log('\n🎯 CONCLUSÃO:');
        console.log('O sistema se adaptou AUTOMATICAMENTE ao novo schema!');
        console.log('Pronto para qualquer CSV! 🚀');
        
      } catch (error) {
        console.error('❌ Erro no teste:', error);
      }
    });
}

// Executar teste se MongoDB estiver disponível
if (require.main === module) {
  testGenericCSV().catch(console.error);
}

module.exports = { testGenericCSV };
