export interface ChartGenerationResult {
    success: boolean;
    charts: string[];
    message: string;
    error?: string;
}
export declare class ChartGeneratorService {
    private whatsappService;
    private pythonEnvPath;
    constructor();
    generateAndSendCharts(messageId: string, filename: string, from: string): Promise<ChartGenerationResult>;
    private generateCharts;
    private sendChartsToWhatsApp;
    private cleanupCharts;
}
//# sourceMappingURL=ChartGeneratorService.d.ts.map