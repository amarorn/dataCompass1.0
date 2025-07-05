"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppRegistrationService = void 0;
const AuthService_1 = require("../../domain/services/AuthService");
const User_1 = require("../../domain/entities/User");
class WhatsAppRegistrationService {
    constructor(userRepository) {
        this.authService = new AuthService_1.AuthService(userRepository);
    }
    async processMessage(message) {
        // Verificar se a mensagem tem texto
        if (!message.text?.body) {
            return {
                success: false,
                message: 'Mensagem sem texto',
                shouldRespond: false
            };
        }
        const messageText = message.text.body.trim();
        // Verificar se é um comando de registro
        if (this.isRegistrationCommand(messageText)) {
            return await this.handleRegistration(message);
        }
        // Verificar se é um comando de ajuda
        if (this.isHelpCommand(messageText)) {
            return this.handleHelp();
        }
        // Verificar se é um comando de status
        if (this.isStatusCommand(messageText)) {
            return await this.handleStatus(message);
        }
        // Não é um comando reconhecido
        return {
            success: false,
            message: 'Comando não reconhecido',
            shouldRespond: false
        };
    }
    isRegistrationCommand(text) {
        const registrationPatterns = [
            /^\/registrar\s+/i,
            /^\/register\s+/i,
            /^registrar\s+/i,
            /^register\s+/i,
            /^cadastrar\s+/i,
            /^signup\s+/i
        ];
        return registrationPatterns.some(pattern => pattern.test(text));
    }
    isHelpCommand(text) {
        const helpPatterns = [
            /^\/help$/i,
            /^\/ajuda$/i,
            /^help$/i,
            /^ajuda$/i,
            /^como\s+registrar/i,
            /^como\s+cadastrar/i
        ];
        return helpPatterns.some(pattern => pattern.test(text));
    }
    isStatusCommand(text) {
        const statusPatterns = [
            /^\/status$/i,
            /^status$/i,
            /^meu\s+status/i,
            /^minha\s+conta/i
        ];
        return statusPatterns.some(pattern => pattern.test(text));
    }
    async handleRegistration(message) {
        try {
            if (!message.text?.body) {
                return {
                    success: false,
                    message: 'Mensagem sem texto',
                    shouldRespond: true,
                    responseMessage: this.getRegistrationHelpMessage()
                };
            }
            const registrationData = this.parseRegistrationData(message.text.body);
            if (!registrationData) {
                return {
                    success: false,
                    message: 'Formato de registro inválido',
                    shouldRespond: true,
                    responseMessage: this.getRegistrationHelpMessage()
                };
            }
            // Adicionar telefone do WhatsApp aos dados
            registrationData.phone = message.from;
            const result = await this.authService.register(registrationData);
            if (result.success) {
                return {
                    success: true,
                    message: 'Usuário registrado com sucesso',
                    shouldRespond: true,
                    responseMessage: `🎉 *Cadastro realizado com sucesso!*\n\n` +
                        `✅ *Nome:* ${registrationData.name}\n` +
                        `✅ *Email:* ${registrationData.email}\n` +
                        `✅ *Telefone:* ${registrationData.phone}\n` +
                        `${registrationData.company ? `✅ *Empresa:* ${registrationData.company}\n` : ''}` +
                        `\n🔐 Sua conta foi criada e você já pode fazer login!\n\n` +
                        `📱 Para acessar sua conta, use:\n` +
                        `*Email:* ${registrationData.email}\n` +
                        `*Senha:* [a senha que você definiu]\n\n` +
                        `🎯 Bem-vindo(a) à Data Compass!`
                };
            }
            else {
                return {
                    success: false,
                    message: result.message,
                    shouldRespond: true,
                    responseMessage: `❌ *Erro no cadastro:*\n\n${result.message}\n\n` +
                        `${result.error?.details ? result.error.details.join('\n') + '\n\n' : ''}` +
                        `💡 Digite *ajuda* para ver o formato correto.`
                };
            }
        }
        catch (error) {
            console.error('Error in handleRegistration:', error);
            return {
                success: false,
                message: 'Erro interno do servidor',
                shouldRespond: true,
                responseMessage: '❌ *Erro interno do servidor*\n\nTente novamente em alguns minutos.'
            };
        }
    }
    parseRegistrationData(text) {
        try {
            // Formatos aceitos:
            // /registrar nome:João Silva email:joao@email.com senha:123456 empresa:MinhaEmpresa
            // registrar João Silva | joao@email.com | 123456 | MinhaEmpresa
            // cadastrar nome=João Silva email=joao@email.com senha=123456
            // Remover comando inicial
            const cleanText = text.replace(/^(\/registrar|\/register|registrar|register|cadastrar|signup)\s+/i, '');
            // Tentar formato com separadores |
            if (cleanText.includes('|')) {
                return this.parseWithPipeFormat(cleanText);
            }
            // Tentar formato com chave:valor
            if (cleanText.includes(':') || cleanText.includes('=')) {
                return this.parseWithKeyValueFormat(cleanText);
            }
            // Tentar formato posicional simples
            return this.parseWithPositionalFormat(cleanText);
        }
        catch (error) {
            console.error('Error parsing registration data:', error);
            return null;
        }
    }
    parseWithPipeFormat(text) {
        const parts = text.split('|').map(part => part.trim());
        if (parts.length < 3) {
            return null;
        }
        return {
            name: parts[0],
            email: parts[1],
            password: parts[2],
            company: parts[3] || undefined,
            role: User_1.UserRole.USER
        };
    }
    parseWithKeyValueFormat(text) {
        const data = {};
        const separator = text.includes('=') ? '=' : ':';
        // Dividir por espaços, mas manter valores com espaços
        const pairs = text.match(/\w+[:=][^\s:=]+(?:\s+[^\s:=]+)*/g);
        if (!pairs) {
            return null;
        }
        pairs.forEach(pair => {
            const [key, ...valueParts] = pair.split(separator);
            const value = valueParts.join(separator).trim();
            const normalizedKey = key.toLowerCase().trim();
            if (normalizedKey === 'nome' || normalizedKey === 'name') {
                data.name = value;
            }
            else if (normalizedKey === 'email') {
                data.email = value;
            }
            else if (normalizedKey === 'senha' || normalizedKey === 'password') {
                data.password = value;
            }
            else if (normalizedKey === 'empresa' || normalizedKey === 'company') {
                data.company = value;
            }
        });
        if (!data.name || !data.email || !data.password) {
            return null;
        }
        return {
            name: data.name,
            email: data.email,
            password: data.password,
            company: data.company,
            role: User_1.UserRole.USER
        };
    }
    parseWithPositionalFormat(text) {
        // Formato: Nome Email Senha [Empresa]
        const parts = text.split(/\s+/);
        if (parts.length < 3) {
            return null;
        }
        // Assumir que o nome pode ter múltiplas palavras
        // Email deve conter @
        // Senha é a próxima após email
        // Empresa é opcional
        let emailIndex = -1;
        for (let i = 0; i < parts.length; i++) {
            if (parts[i].includes('@')) {
                emailIndex = i;
                break;
            }
        }
        if (emailIndex === -1 || emailIndex === 0 || emailIndex >= parts.length - 1) {
            return null;
        }
        const name = parts.slice(0, emailIndex).join(' ');
        const email = parts[emailIndex];
        const password = parts[emailIndex + 1];
        const company = parts.slice(emailIndex + 2).join(' ') || undefined;
        return {
            name,
            email,
            password,
            company,
            role: User_1.UserRole.USER
        };
    }
    handleHelp() {
        return {
            success: true,
            message: 'Ajuda enviada',
            shouldRespond: true,
            responseMessage: this.getRegistrationHelpMessage()
        };
    }
    async handleStatus(message) {
        // Implementar verificação de status do usuário
        // Por enquanto, retornar mensagem genérica
        return {
            success: true,
            message: 'Status enviado',
            shouldRespond: true,
            responseMessage: `📊 *Status da sua conta:*\n\n` +
                `📱 *Telefone:* ${message.from}\n` +
                `⏰ *Última consulta:* ${new Date().toLocaleString('pt-BR')}\n\n` +
                `💡 Para mais informações, acesse nossa plataforma web.`
        };
    }
    getRegistrationHelpMessage() {
        return `📝 *Como se cadastrar via WhatsApp:*\n\n` +
            `*Formato 1 (Recomendado):*\n` +
            `\`registrar Nome | email@exemplo.com | senha123 | Empresa\`\n\n` +
            `*Formato 2:*\n` +
            `\`registrar nome:João Silva email:joao@email.com senha:123456\`\n\n` +
            `*Formato 3:*\n` +
            `\`registrar João Silva joao@email.com 123456 MinhaEmpresa\`\n\n` +
            `*Exemplos:*\n` +
            `• \`registrar Maria Santos | maria@email.com | senha123\`\n` +
            `• \`cadastrar nome:João email:joao@teste.com senha:abc123\`\n\n` +
            `*Campos obrigatórios:*\n` +
            `✅ Nome completo\n` +
            `✅ Email válido\n` +
            `✅ Senha (mínimo 6 caracteres)\n\n` +
            `*Campos opcionais:*\n` +
            `• Empresa/Organização\n\n` +
            `💡 *Outros comandos:*\n` +
            `• \`ajuda\` - Ver esta mensagem\n` +
            `• \`status\` - Ver status da conta`;
    }
}
exports.WhatsAppRegistrationService = WhatsAppRegistrationService;
//# sourceMappingURL=WhatsAppRegistrationService.js.map