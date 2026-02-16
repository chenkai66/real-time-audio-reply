"""
测试中间件模块
"""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from backend.utils.middleware import (
    RequestTracingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware
)


@pytest.fixture
def app_with_tracing():
    """创建带追踪中间件的应用"""
    app = FastAPI()
    app.add_middleware(RequestTracingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
    
    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    return app


@pytest.fixture
def app_with_error_handling():
    """创建带错误处理中间件的应用"""
    app = FastAPI()
    app.add_middleware(ErrorHandlingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
    
    @app.get("/value_error")
    async def value_error_endpoint():
        raise ValueError("Validation failed")
    
    @app.get("/permission_error")
    async def permission_error_endpoint():
        raise PermissionError("Access denied")
    
    @app.get("/generic_error")
    async def generic_error_endpoint():
        raise RuntimeError("Something went wrong")
    
    return app


@pytest.fixture
def app_with_rate_limit():
    """创建带限流中间件的应用"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, max_requests=5, window_seconds=60)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
    
    return app


class TestRequestTracingMiddleware:
    """测试请求追踪中间件"""
    
    def test_adds_trace_id(self, app_with_tracing):
        """测试添加追踪ID"""
        client = TestClient(app_with_tracing)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Trace-ID" in response.headers
        assert len(response.headers["X-Trace-ID"]) > 0
    
    def test_different_trace_ids(self, app_with_tracing):
        """测试不同请求有不同的追踪ID"""
        client = TestClient(app_with_tracing)
        
        response1 = client.get("/test")
        response2 = client.get("/test")
        
        trace_id1 = response1.headers["X-Trace-ID"]
        trace_id2 = response2.headers["X-Trace-ID"]
        
        assert trace_id1 != trace_id2


class TestErrorHandlingMiddleware:
    """测试错误处理中间件"""
    
    def test_handles_value_error(self, app_with_error_handling):
        """测试处理 ValueError"""
        client = TestClient(app_with_error_handling)
        response = client.get("/value_error")
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "ValidationError"
        assert "Validation failed" in data["message"]
    
    def test_handles_permission_error(self, app_with_error_handling):
        """测试处理 PermissionError"""
        client = TestClient(app_with_error_handling)
        response = client.get("/permission_error")
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "PermissionDenied"
    
    def test_handles_generic_error(self, app_with_error_handling):
        """测试处理通用错误"""
        client = TestClient(app_with_error_handling)
        response = client.get("/generic_error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "InternalServerError"
    
    def test_successful_request(self, app_with_error_handling):
        """测试正常请求"""
        client = TestClient(app_with_error_handling)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}


class TestRateLimitMiddleware:
    """测试限流中间件"""
    
    def test_allows_requests_under_limit(self, app_with_rate_limit):
        """测试限制内的请求"""
        client = TestClient(app_with_rate_limit)
        
        # 发送 5 个请求（限制内）
        for i in range(5):
            response = client.get("/test")
            assert response.status_code == 200
    
    def test_blocks_requests_over_limit(self, app_with_rate_limit):
        """测试超过限制的请求"""
        client = TestClient(app_with_rate_limit)
        
        # 发送 5 个请求（限制内）
        for i in range(5):
            client.get("/test")
        
        # 第 6 个请求应该被限流
        response = client.get("/test")
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "RateLimitExceeded"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

