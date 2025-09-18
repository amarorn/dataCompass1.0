import { exec } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { WhatsAppService } from '../../infrastructure/external/WhatsAppService';

export interface ChartGenerationResult {
    success: boolean;
    charts: string[];
    message: string;
    error?: string;
}

export class ChartGeneratorService {
    private whatsappService: WhatsAppService;
    private pythonEnvPath: string;

    constructor() {
        this.whatsappService = new WhatsAppService();
        this.pythonEnvPath = path.join(process.cwd(), 'venv_datacompass', 'bin', 'activate');
    }

    async generateAndSendCharts(messageId: string, filename: string, from: string): Promise<ChartGenerationResult> {
        try {
            console.log(`📊 Gerando gráficos para ${filename} (${messageId})`);
            
            // 1. Gerar gráficos usando Python
            const chartPaths = await this.generateCharts(messageId, filename);
            
            if (chartPaths.length === 0) {
                return {
                    success: false,
                    charts: [],
                    message: 'Nenhum gráfico foi gerado',
                    error: 'Falha na geração de gráficos'
                };
            }

            // 2. Enviar gráficos via WhatsApp
            const sendResults = await this.sendChartsToWhatsApp(chartPaths, from, filename);
            
            // 3. Limpar arquivos temporários (opcional)
            await this.cleanupCharts(chartPaths);
            
            return {
                success: true,
                charts: chartPaths,
                message: `${chartPaths.length} gráficos enviados com sucesso para ${from}`,
            };

        } catch (error) {
            console.error('❌ Erro ao gerar e enviar gráficos:', error);
            return {
                success: false,
                charts: [],
                message: 'Erro ao gerar gráficos',
                error: error instanceof Error ? error.message : 'Erro desconhecido'
            };
        }
    }

    private async generateCharts(messageId: string, filename: string): Promise<string[]> {
        return new Promise((resolve, reject) => {
            console.log(`🐍 Executando script Python para ${messageId}`);
            
            // Usar o arquivo pandas_analysis.py que já funciona
            const command = `source ${this.pythonEnvPath} && python pandas_analysis.py "${messageId}"`;
            
            exec(command, { cwd: process.cwd() }, (error, stdout, stderr) => {
                if (error) {
                    console.error('❌ Erro na execução do Python:', error);
                    console.error('❌ Stderr:', stderr);
                    reject(error);
                    return;
                }

                if (stderr) {
                    console.warn('⚠️ Warnings do Python:', stderr);
                }

                console.log('✅ Saída do Python:', stdout);

                // Procurar pelos arquivos PNG gerados no diretório atual
                const fs = require('fs');
                const path = require('path');
                
                try {
                    const files = fs.readdirSync(process.cwd());
                    const pngFiles = files.filter((file: string) => file.endsWith('.png'));
                    
                    if (pngFiles.length > 0) {
                        const fullPaths = pngFiles.map((file: string) => path.join(process.cwd(), file));
                        console.log(`📊 Gráficos encontrados: ${fullPaths.length}`);
                        fullPaths.forEach((filePath: string) => {
                            console.log(`   • ${path.basename(filePath)}`);
                        });
                        resolve(fullPaths);
                    } else {
                        console.error('❌ Nenhum arquivo PNG encontrado');
                        resolve([]);
                    }
                } catch (fsError) {
                    console.error('❌ Erro ao listar arquivos:', fsError);
                    resolve([]);
                }
            });
        });
    }

    private async sendChartsToWhatsApp(chartPaths: string[], to: string, filename: string): Promise<boolean[]> {
        const results: boolean[] = [];
        
        console.log(`📱 Enviando ${chartPaths.length} gráficos para ${to}`);
        
        // Enviar mensagem introdutória
        const introMessage = `📊 *Análise Exploratória Concluída!*

📄 *Arquivo:* ${filename}
📈 *Gráficos gerados:* ${chartPaths.length}

Os gráficos com insights detalhados serão enviados a seguir:`;

        try {
            await this.whatsappService.sendMessage(to, introMessage);
            console.log('✅ Mensagem introdutória enviada');
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem introdutória:', error);
        }

        // Aguardar um pouco antes de enviar os gráficos
        await new Promise(resolve => setTimeout(resolve, 2000));

        for (let i = 0; i < chartPaths.length; i++) {
            const chartPath = chartPaths[i];
            
            try {
                // Verificar se o arquivo existe
                await fs.access(chartPath);
                
                // Determinar o tipo de gráfico pelo nome do arquivo
                let caption = '';
                if (chartPath.includes('distribuicoes')) {
                    caption = '📊 *Distribuições das Variáveis*\n\nEste gráfico mostra a distribuição de cada variável numérica com média e mediana destacadas.';
                } else if (chartPath.includes('resumo_executivo')) {
                    caption = '📈 *Resumo Executivo*\n\nVisão geral dos principais indicadores e métricas do seu dataset.';
                } else if (chartPath.includes('insights')) {
                    caption = '💡 *Insights Automáticos*\n\nAnálise detalhada com recomendações baseadas nos seus dados.';
                } else {
                    caption = `📊 Gráfico ${i + 1} de ${chartPaths.length}`;
                }

                // Enviar o gráfico
                const success = await this.whatsappService.sendDocument(to, chartPath, caption);
                results.push(success);
                
                if (success) {
                    console.log(`✅ Gráfico ${i + 1}/${chartPaths.length} enviado: ${path.basename(chartPath)}`);
                } else {
                    console.error(`❌ Falha ao enviar gráfico ${i + 1}/${chartPaths.length}: ${path.basename(chartPath)}`);
                }

                // Aguardar entre envios para evitar rate limiting
                if (i < chartPaths.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 3000));
                }

            } catch (error) {
                console.error(`❌ Erro ao enviar gráfico ${chartPath}:`, error);
                results.push(false);
            }
        }

        // Enviar mensagem final
        const successCount = results.filter(r => r).length;
        const finalMessage = `✅ *Análise Concluída!*

📊 *Gráficos enviados:* ${successCount}/${chartPaths.length}
🎯 *Status:* ${successCount === chartPaths.length ? 'Todos enviados com sucesso!' : 'Alguns gráficos falharam'}

💡 *Dica:* Use estes insights para tomar decisões baseadas em dados!

🔗 *APIs disponíveis:*
• \`/raw\` - dados brutos
• \`/analysis\` - análise completa
• \`/ml\` - dados para machine learning`;

        try {
            await this.whatsappService.sendMessage(to, finalMessage);
            console.log('✅ Mensagem final enviada');
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem final:', error);
        }

        return results;
    }

    private async cleanupCharts(chartPaths: string[]): Promise<void> {
        console.log(`🧹 Limpando ${chartPaths.length} arquivos temporários...`);
        
        for (const chartPath of chartPaths) {
            try {
                await fs.unlink(chartPath);
                console.log(`🗑️ Arquivo removido: ${path.basename(chartPath)}`);
            } catch (error) {
                console.warn(`⚠️ Não foi possível remover ${chartPath}:`, error);
            }
        }

        // Remover diretório temporário se estiver vazio
        try {
            const chartsDir = path.dirname(chartPaths[0]);
            if (chartsDir.includes('temp_charts')) {
                await fs.rmdir(chartsDir);
                console.log('🗑️ Diretório temporário removido');
            }
        } catch (error) {
            // Diretório não vazio ou não existe, ignorar
        }
    }
}
