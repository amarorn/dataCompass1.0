import { IUserRepository } from '../../domain/repositories/IUserRepository';
export interface WhatsAppMessage {
    id: string;
    from: string;
    timestamp: string;
    type: 'text' | 'image' | 'audio' | 'video' | 'document' | 'location';
    text?: {
        body: string;
    };
}
export interface RegistrationResult {
    success: boolean;
    message: string;
    shouldRespond: boolean;
    responseMessage?: string;
}
export declare class WhatsAppRegistrationService {
    private authService;
    constructor(userRepository: IUserRepository);
    processMessage(message: WhatsAppMessage): Promise<RegistrationResult>;
    private isRegistrationCommand;
    private isHelpCommand;
    private isStatusCommand;
    private handleRegistration;
    private parseRegistrationData;
    private parseWithPipeFormat;
    private parseWithKeyValueFormat;
    private parseWithPositionalFormat;
    private handleHelp;
    private handleStatus;
    private getRegistrationHelpMessage;
}
//# sourceMappingURL=WhatsAppRegistrationService.d.ts.map