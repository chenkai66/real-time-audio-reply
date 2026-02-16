"""
测试日志模块
"""
import pytest
import logging
import json
from backend.utils.logger import (
    StructuredFormatter,
    setup_logging,
    get_logger,
    log_with_trace
)


class TestStructuredFormatter:
    """测试 StructuredFormatter 类"""
    
    def test_format_basic(self):
        """测试基本格式化"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert data["module"] == "test"
        assert data["line"] == 10
        assert "timestamp" in data
    
    def test_format_with_trace_id(self):
        """测试带追踪ID的格式化"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.trace_id = "test-trace-123"
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data["trace_id"] == "test-trace-123"
    
    def test_format_with_exception(self):
        """测试带异常的格式化"""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=exc_info
            )
            
            result = formatter.format(record)
            data = json.loads(result)
            
            assert "exception" in data
            assert "ValueError" in data["exception"]


class TestSetupLogging:
    """测试 setup_logging 函数"""
    
    def test_setup_basic(self):
        """测试基本设置"""
        setup_logging(level="INFO", structured=False)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0
    
    def test_setup_structured(self):
        """测试结构化日志设置"""
        setup_logging(level="DEBUG", structured=True)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        
        # 检查是否有结构化格式化器
        has_structured = any(
            isinstance(h.formatter, StructuredFormatter)
            for h in root_logger.handlers
        )
        assert has_structured


class TestGetLogger:
    """测试 get_logger 函数"""
    
    def test_get_logger(self):
        """测试获取日志器"""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)


class TestLogWithTrace:
    """测试 log_with_trace 函数"""
    
    def test_log_with_trace(self):
        """测试带追踪ID的日志"""
        logger = get_logger("test")
        
        # 这个测试主要确保函数不会抛出异常
        log_with_trace(logger, "info", "Test message", trace_id="test-123")
        log_with_trace(logger, "warning", "Warning message")
        log_with_trace(logger, "error", "Error message", trace_id="error-456")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

