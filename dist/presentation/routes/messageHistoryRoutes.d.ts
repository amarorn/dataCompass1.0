declare const router: import("express-serve-static-core").Router;
interface MessageHistory {
    id: string;
    from: string;
    message: string;
    timestamp: string;
    type: 'sent' | 'received';
    analysis?: {
        type: string;
        sentiment: string;
        value?: number;
        category?: string;
    };
}
export declare function addToHistory(message: MessageHistory): void;
export { router as messageHistoryRoutes };
//# sourceMappingURL=messageHistoryRoutes.d.ts.map