"""
性能监控模块
提供性能指标收集和统计功能
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import statistics


@dataclass
class Metric:
    """性能指标"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化指标收集器
        
        Args:
            max_history: 最大历史记录数
        """
        self.metrics: Dict[str, List[Metric]] = {}
        self.max_history = max_history
    
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录指标
        
        Args:
            name: 指标名称
            value: 指标值
            tags: 标签
        """
        metric = Metric(name=name, value=value, tags=tags or {})
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # 限制历史记录数量
        if len(self.metrics[name]) > self.max_history:
            self.metrics[name] = self.metrics[name][-self.max_history:]
    
    def get_stats(self, name: str, window_seconds: Optional[int] = None) -> Dict[str, float]:
        """
        获取指标统计信息
        
        Args:
            name: 指标名称
            window_seconds: 时间窗口（秒），如果不指定则统计所有
            
        Returns:
            统计信息字典
        """
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        # 过滤时间窗口
        metrics = self.metrics[name]
        if window_seconds:
            cutoff_time = datetime.now().timestamp() - window_seconds
            metrics = [
                m for m in metrics
                if m.timestamp.timestamp() > cutoff_time
            ]
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0],
            "p99": statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0],
        }
    
    def get_all_stats(self, window_seconds: Optional[int] = None) -> Dict[str, Dict[str, float]]:
        """
        获取所有指标的统计信息
        
        Args:
            window_seconds: 时间窗口（秒）
            
        Returns:
            所有指标的统计信息
        """
        return {
            name: self.get_stats(name, window_seconds)
            for name in self.metrics.keys()
        }
    
    def clear(self, name: Optional[str] = None) -> None:
        """
        清空指标
        
        Args:
            name: 指标名称，如果不指定则清空所有
        """
        if name:
            if name in self.metrics:
                self.metrics[name].clear()
        else:
            self.metrics.clear()


class Timer:
    """计时器上下文管理器"""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """
        初始化计时器
        
        Args:
            collector: 指标收集器
            metric_name: 指标名称
            tags: 标签
        """
        self.collector = collector
        self.metric_name = metric_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.record(self.metric_name, duration, self.tags)


# 全局指标收集器
global_metrics = MetricsCollector()


def timed(metric_name: str, collector: Optional[MetricsCollector] = None):
    """
    计时装饰器
    
    Args:
        metric_name: 指标名称
        collector: 指标收集器，如果不指定使用全局收集器
        
    Returns:
        装饰器函数
    """
    _collector = collector or global_metrics
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            with Timer(_collector, metric_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

