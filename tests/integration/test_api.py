"""
测试 FastAPI 主应用
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app, manager
from backend.core.conversation import conversation_history
from backend.core.role import role_identifier


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    """每个测试后清理"""
    yield
    conversation_history.clear()
    role_identifier.clear_role_features()
    manager.active_connections.clear()


class TestMainAPI:
    """测试主 API"""
    
    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "0.1.0"
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_stats(self, client):
        """测试获取统计信息"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "conversation" in data
        assert "connections" in data
    
    def test_clear_conversation(self, client):
        """测试清空对话"""
        # 先添加一些对话
        from backend.core.role import Role
        conversation_history.add_turn(Role.TEACHER, "Hello")
        
        response = client.post("/api/conversation/clear")
        assert response.status_code == 200
        
        # 验证已清空
        stats = conversation_history.get_stats()
        assert stats["total_turns"] == 0
    
    def test_get_conversation_history(self, client):
        """测试获取对话历史"""
        from backend.core.role import Role
        
        # 添加对话
        conversation_history.add_turn(Role.TEACHER, "Hello")
        conversation_history.add_turn(Role.STUDENT, "Hi")
        
        response = client.get("/api/conversation/history")
        assert response.status_code == 200
        data = response.json()
        assert "l1_cache" in data
        assert "l2_cache" in data
        assert "stats" in data
        assert len(data["l1_cache"]) == 2


class TestWebSocket:
    """测试 WebSocket 端点"""
    
    def test_websocket_connect(self, client):
        """测试 WebSocket 连接"""
        with client.websocket_connect("/ws/audio") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
    
    def test_websocket_ping_pong(self, client):
        """测试心跳"""
        with client.websocket_connect("/ws/audio") as websocket:
            # 跳过连接消息
            websocket.receive_json()
            
            # 发送 ping
            websocket.send_json({"type": "ping"})
            
            # 接收 pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    def test_websocket_transcript_teacher(self, client):
        """测试教师发言转写"""
        with client.websocket_connect("/ws/audio") as websocket:
            # 跳过连接消息
            websocket.receive_json()
            
            # 发送教师发言
            websocket.send_json({
                "type": "transcript",
                "text": "今天我们学习 Python 基础",
                "is_final": True
            })
            
            # 接收状态消息
            status_msg = websocket.receive_json()
            assert status_msg["type"] == "status"
            
            # 接收角色识别结果
            role_msg = websocket.receive_json()
            assert role_msg["type"] == "role_identified"
            assert "role" in role_msg
            assert "text" in role_msg
    
    def test_websocket_unknown_type(self, client):
        """测试未知消息类型"""
        with client.websocket_connect("/ws/audio") as websocket:
            # 跳过连接消息
            websocket.receive_json()
            
            # 发送未知类型
            websocket.send_json({"type": "unknown"})
            
            # 接收错误消息
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "未知的消息类型" in data["message"]


class TestStreamWebSocket:
    """测试流式 WebSocket"""
    
    def test_stream_websocket_connect(self, client):
        """测试流式 WebSocket 连接"""
        with client.websocket_connect("/ws/stream") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
    
    def test_stream_websocket_ping(self, client):
        """测试流式 WebSocket 心跳"""
        with client.websocket_connect("/ws/stream") as websocket:
            # 跳过连接消息
            websocket.receive_json()
            
            # 发送 ping
            websocket.send_json({"type": "ping"})
            
            # 接收 pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    def test_stream_generate_empty_question(self, client):
        """测试空问题"""
        with client.websocket_connect("/ws/stream") as websocket:
            # 跳过连接消息
            websocket.receive_json()
            
            # 发送空问题
            websocket.send_json({
                "type": "generate",
                "question": ""
            })
            
            # 接收错误消息
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "不能为空" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

