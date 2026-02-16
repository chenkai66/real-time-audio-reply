"""
测试缓存模块
"""
import pytest
import time
from backend.utils.cache import SimpleCache, cache_key, cached, global_cache


class TestSimpleCache:
    """测试 SimpleCache 类"""
    
    def test_init(self):
        """测试初始化"""
        cache = SimpleCache(default_ttl=60)
        assert cache.default_ttl == 60
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_set_and_get(self):
        """测试设置和获取"""
        cache = SimpleCache()
        cache.set("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_get_nonexistent(self):
        """测试获取不存在的键"""
        cache = SimpleCache()
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    def test_ttl_expiration(self):
        """测试过期时间"""
        cache = SimpleCache(default_ttl=1)
        cache.set("key1", "value1")
        
        # 立即获取应该成功
        assert cache.get("key1") == "value1"
        
        # 等待过期
        time.sleep(1.1)
        
        # 过期后应该返回 None
        assert cache.get("key1") is None
    
    def test_custom_ttl(self):
        """测试自定义过期时间"""
        cache = SimpleCache(default_ttl=10)
        cache.set("key1", "value1", ttl=1)
        
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_delete(self):
        """测试删除"""
        cache = SimpleCache()
        cache.set("key1", "value1")
        
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False
    
    def test_clear(self):
        """测试清空"""
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_cleanup(self):
        """测试清理过期缓存"""
        cache = SimpleCache(default_ttl=1)
        cache.set("key1", "value1")
        cache.set("key2", "value2", ttl=10)
        
        time.sleep(1.1)
        
        cleaned = cache.cleanup()
        assert cleaned == 1
        assert len(cache.cache) == 1
        assert cache.get("key2") == "value2"
    
    def test_get_stats(self):
        """测试获取统计信息"""
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss
        
        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["total_requests"] == 2


class TestCacheKey:
    """测试 cache_key 函数"""
    
    def test_same_args(self):
        """测试相同参数生成相同键"""
        key1 = cache_key("arg1", "arg2", kwarg1="value1")
        key2 = cache_key("arg1", "arg2", kwarg1="value1")
        assert key1 == key2
    
    def test_different_args(self):
        """测试不同参数生成不同键"""
        key1 = cache_key("arg1", "arg2")
        key2 = cache_key("arg1", "arg3")
        assert key1 != key2
    
    def test_kwargs_order(self):
        """测试关键字参数顺序不影响键"""
        key1 = cache_key(a=1, b=2)
        key2 = cache_key(b=2, a=1)
        assert key1 == key2


class TestCachedDecorator:
    """测试 cached 装饰器"""
    
    def test_cached_function(self):
        """测试缓存函数"""
        call_count = 0
        
        @cached(ttl=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用应该使用缓存
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1
        
        # 不同参数应该重新计算
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cached_with_custom_cache(self):
        """测试使用自定义缓存实例"""
        custom_cache = SimpleCache(default_ttl=5)
        
        @cached(ttl=5, cache_instance=custom_cache)
        def func(x):
            return x + 1
        
        func(1)
        func(1)
        
        stats = custom_cache.get_stats()
        assert stats["hits"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

