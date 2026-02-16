"""
测试性能监控模块
"""
import pytest
import time
from backend.utils.metrics import MetricsCollector, Timer, timed, global_metrics


class TestMetricsCollector:
    """测试 MetricsCollector 类"""
    
    def test_init(self):
        """测试初始化"""
        collector = MetricsCollector(max_history=100)
        assert collector.max_history == 100
        assert len(collector.metrics) == 0
    
    def test_record(self):
        """测试记录指标"""
        collector = MetricsCollector()
        collector.record("test_metric", 1.5)
        
        assert "test_metric" in collector.metrics
        assert len(collector.metrics["test_metric"]) == 1
        assert collector.metrics["test_metric"][0].value == 1.5
    
    def test_record_with_tags(self):
        """测试带标签的指标记录"""
        collector = MetricsCollector()
        collector.record("test_metric", 2.0, tags={"env": "test"})
        
        metric = collector.metrics["test_metric"][0]
        assert metric.tags["env"] == "test"
    
    def test_max_history(self):
        """测试历史记录限制"""
        collector = MetricsCollector(max_history=5)
        
        for i in range(10):
            collector.record("test_metric", float(i))
        
        assert len(collector.metrics["test_metric"]) == 5
        # 应该保留最新的 5 条
        assert collector.metrics["test_metric"][0].value == 5.0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        collector = MetricsCollector()
        
        for i in range(10):
            collector.record("test_metric", float(i))
        
        stats = collector.get_stats("test_metric")
        assert stats["count"] == 10
        assert stats["min"] == 0.0
        assert stats["max"] == 9.0
        assert stats["mean"] == 4.5
    
    def test_get_stats_empty(self):
        """测试空指标的统计"""
        collector = MetricsCollector()
        stats = collector.get_stats("nonexistent")
        assert stats == {}
    
    def test_get_all_stats(self):
        """测试获取所有统计信息"""
        collector = MetricsCollector()
        collector.record("metric1", 1.0)
        collector.record("metric2", 2.0)
        
        all_stats = collector.get_all_stats()
        assert "metric1" in all_stats
        assert "metric2" in all_stats
    
    def test_clear_specific(self):
        """测试清空特定指标"""
        collector = MetricsCollector()
        collector.record("metric1", 1.0)
        collector.record("metric2", 2.0)
        
        collector.clear("metric1")
        
        assert len(collector.metrics["metric1"]) == 0
        assert len(collector.metrics["metric2"]) == 1
    
    def test_clear_all(self):
        """测试清空所有指标"""
        collector = MetricsCollector()
        collector.record("metric1", 1.0)
        collector.record("metric2", 2.0)
        
        collector.clear()
        
        assert len(collector.metrics) == 0


class TestTimer:
    """测试 Timer 类"""
    
    def test_timer_context(self):
        """测试计时器上下文管理器"""
        collector = MetricsCollector()
        
        with Timer(collector, "test_duration"):
            time.sleep(0.1)
        
        assert "test_duration" in collector.metrics
        duration = collector.metrics["test_duration"][0].value
        assert 0.09 < duration < 0.15
    
    def test_timer_with_tags(self):
        """测试带标签的计时器"""
        collector = MetricsCollector()
        
        with Timer(collector, "test_duration", tags={"operation": "test"}):
            time.sleep(0.05)
        
        metric = collector.metrics["test_duration"][0]
        assert metric.tags["operation"] == "test"


class TestTimedDecorator:
    """测试 timed 装饰器"""
    
    def test_timed_function(self):
        """测试计时装饰器"""
        collector = MetricsCollector()
        
        @timed("func_duration", collector=collector)
        def slow_function():
            time.sleep(0.05)
            return "done"
        
        result = slow_function()
        
        assert result == "done"
        assert "func_duration" in collector.metrics
        duration = collector.metrics["func_duration"][0].value
        assert 0.04 < duration < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

