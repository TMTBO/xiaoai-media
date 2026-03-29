"""测试用户最近登录时间和启用开关功能"""
import pytest
from datetime import datetime
from xiaoai_media.services.user_service import UserService, User


def test_user_model_with_new_fields():
    """测试用户模型包含新字段"""
    user = User(
        username="test",
        password_hash="hash123",
        role="user",
        last_login="2026-03-29T12:00:00",
        enabled=True
    )
    
    user_dict = user.to_dict()
    assert "last_login" in user_dict
    assert "enabled" in user_dict
    assert user_dict["last_login"] == "2026-03-29T12:00:00"
    assert user_dict["enabled"] is True
    
    safe_dict = user.to_safe_dict()
    assert "last_login" in safe_dict
    assert "enabled" in safe_dict
    assert "password_hash" not in safe_dict


def test_user_default_enabled():
    """测试用户默认启用"""
    user = User(username="test", password_hash="hash123")
    assert user.enabled is True


def test_authenticate_updates_last_login(tmp_path):
    """测试登录时更新最近登录时间"""
    # 创建临时用户服务
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    # 创建测试用户
    service.create_user("testuser", "password123", "user")
    
    # 第一次登录
    user = service.authenticate("testuser", "password123")
    assert user is not None
    assert user.last_login is not None
    first_login = user.last_login
    
    # 第二次登录
    user = service.authenticate("testuser", "password123")
    assert user is not None
    assert user.last_login is not None
    assert user.last_login >= first_login


def test_authenticate_disabled_user(tmp_path):
    """测试禁用用户无法登录"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    # 创建并禁用用户
    service.create_user("testuser", "password123", "user")
    service.disable_user("testuser")
    
    # 尝试登录
    user = service.authenticate("testuser", "password123")
    assert user is None


def test_enable_disable_user(tmp_path):
    """测试启用/禁用用户"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    # 创建用户
    user = service.create_user("testuser", "password123", "user")
    assert user.enabled is True
    
    # 禁用用户
    user = service.disable_user("testuser")
    assert user.enabled is False
    
    # 启用用户
    user = service.enable_user("testuser")
    assert user.enabled is True


def test_cannot_disable_admin(tmp_path):
    """测试不能禁用管理员账户"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    service.create_user("admin", "admin123", "admin")
    
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.disable_user("admin")


def test_cannot_disable_admin_via_update(tmp_path):
    """测试不能通过 update_user 禁用管理员账户"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    service.create_user("admin", "admin123", "admin")
    
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.update_user("admin", enabled=False)


def test_update_user_enabled_field(tmp_path):
    """测试通过 update_user 更新启用状态"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    service.create_user("testuser", "password123", "user")
    
    # 禁用用户
    user = service.update_user("testuser", enabled=False)
    assert user.enabled is False
    
    # 启用用户
    user = service.update_user("testuser", enabled=True)
    assert user.enabled is True



def test_cannot_disable_any_admin_role_user(tmp_path):
    """测试不能禁用任何角色为 admin 的用户"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    # 创建一个角色为 admin 但用户名不是 admin 的用户
    service.create_user("superuser", "password123", "admin")
    
    # 尝试禁用应该失败
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.disable_user("superuser")
    
    # 尝试通过 update_user 禁用也应该失败
    with pytest.raises(ValueError, match="不能禁用管理员账户"):
        service.update_user("superuser", enabled=False)


def test_can_disable_regular_user(tmp_path):
    """测试可以禁用普通用户"""
    service = UserService()
    service.users_file = tmp_path / "users.json"
    
    # 创建普通用户
    service.create_user("regularuser", "password123", "user")
    
    # 禁用应该成功
    user = service.disable_user("regularuser")
    assert user.enabled is False
    
    # 通过 update_user 禁用也应该成功
    service.enable_user("regularuser")
    user = service.update_user("regularuser", enabled=False)
    assert user.enabled is False
