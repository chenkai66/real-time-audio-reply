"""
缓存管理模块
提供简单的内存缓存功能
"""
import time
from typing import Any, Optional, Dict, Tuple
from functools import wraps
import hashlib
import json


class SimpleCache:
    """简单的内存缓存"""
    
    def __init__(self, default_ttl: int = 300):
        """
        初始化缓存
        
        Args:
            default_ttl: 默认过期时间（秒）
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回 None
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, expire_time = self.cache[key]
        
        # 检查是否过期
        if time.time() > expire_time:
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果不指定使用默认值
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expire_time = time.time() + ttl
        self.cache[key] = (value, expire_time)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def cleanup(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的缓存数量
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self.cache.items()
            if current_time > expire_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


def cache_key(*args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        缓存键
    """
    # 将参数序列化为字符串
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    
    # 生成哈希
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, cache_instance: Optional[SimpleCache] = None):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        cache_instance: 缓存实例，如果不指定使用全局缓存
        
    Returns:
        装饰器函数
    """
    _cache = cache_instance or global_cache
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_value = _cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            _cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator


# 全局缓存实例
global_cache = SimpleCache(default_ttl=300)

