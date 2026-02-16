"""
中间件模块
提供请求追踪、错误处理等中间件
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成追踪 ID
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        # 记录请求开始
        start_time = time.time()
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"trace_id": trace_id}
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 记录请求完成
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {duration:.3f}s",
                extra={"trace_id": trace_id, "duration": duration}
            )
            
            # 添加追踪 ID 到响应头
            response.headers["X-Trace-ID"] = trace_id
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {str(e)} - Duration: {duration:.3f}s",
                extra={"trace_id": trace_id, "duration": duration},
                exc_info=True
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """统一错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "ValidationError",
                    "message": str(e),
                    "trace_id": getattr(request.state, "trace_id", None)
                }
            )
        
        except PermissionError as e:
            logger.warning(f"Permission denied: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "PermissionDenied",
                    "message": str(e),
                    "trace_id": getattr(request.state, "trace_id", None)
                }
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "trace_id": getattr(request.state, "trace_id", None)
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的限流中间件"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {ip: [(timestamp, count)]}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 清理过期记录
        current_time = time.time()
        if client_ip in self.requests:
            self.requests[client_ip] = [
                (ts, count) for ts, count in self.requests[client_ip]
                if current_time - ts < self.window_seconds
            ]
        
        # 检查请求数
        if client_ip in self.requests:
            total_requests = sum(count for _, count in self.requests[client_ip])
            if total_requests >= self.max_requests:
                logger.warning(
                    f"Rate limit exceeded for {client_ip}",
                    extra={"client_ip": client_ip}
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "RateLimitExceeded",
                        "message": "Too many requests"
                    }
                )
        
        # 记录请求
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append((current_time, 1))
        
        return await call_next(request)

