"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.asyncHandler = exports.createError = exports.errorHandler = void 0;
const errorHandler = (error, req, res, next) => {
    const statusCode = error.statusCode || 500;
    const message = error.message || 'Internal Server Error';
    // Log do erro
    console.error(`[ERROR] ${new Date().toISOString()} - ${req.method} ${req.path}:`, {
        message: error.message,
        stack: error.stack,
        statusCode,
        body: req.body,
        params: req.params,
        query: req.query
    });
    // Resposta para o cliente
    res.status(statusCode).json({
        success: false,
        error: {
            message,
            statusCode,
            timestamp: new Date().toISOString(),
            path: req.path,
            method: req.method
        },
        // Incluir stack trace apenas em desenvolvimento
        ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
    });
};
exports.errorHandler = errorHandler;
const createError = (message, statusCode = 500) => {
    const error = new Error(message);
    error.statusCode = statusCode;
    error.isOperational = true;
    return error;
};
exports.createError = createError;
const asyncHandler = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
exports.asyncHandler = asyncHandler;
//# sourceMappingURL=errorHandler.js.map