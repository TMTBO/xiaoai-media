"""用户认证功能测试"""
import pytest
import json
from pathlib import Path
import tempfile
import shutil

from xiaoai_media.services.user_service import UserService, User


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def user_service(temp_data_dir, monkeypatch):
    """创建用户服务实例"""
    # 修改数据目录
    import xiaoai_media.config as config
    monkeypatch.setattr(config, 'DATA_DIR', temp_data_dir)
    
    service = UserService()
    return service


def test_default_admin_creation(user_service):
    """测试默认管理员账户创建"""
    users = user_service.list_users()
    assert len(users) == 1
    assert users[0].username == "admin"
    assert users[0].role == "admin"


def test_authenticate_success(user_service):
    """测试登录成功"""
    user = user_service.authenticate("admin", "admin123")
    assert user is not None
    assert user.username == "admin"
    assert user.role == "admin"


def test_authenticate_failure(user_service):
    """测试登录失败"""
    user = user_service.authenticate("admin", "wrongpassword")
    assert user is None
    
    user = user_service.authenticate("nonexistent", "password")
    assert user is None


def test_create_user(user_service):
    """测试创建用户"""
    new_user = user_service.create_user("testuser", "password123", "user")
    assert new_user.username == "testuser"
    assert new_user.role == "user"
    
    # 验证可以登录
    user = user_service.authenticate("testuser", "password123")
    assert user is not None
    assert user.username == "testuser"


def test_create_duplicate_user(user_service):
    """测试创建重复用户"""
    user_service.create_user("testuser", "password123", "user")
    
    with pytest.raises(ValueError, match="已存在"):
        user_service.create_user("testuser", "password456", "user")


def test_update_user_password(user_service):
    """测试更新用户密码"""
    user_service.create_user("testuser", "oldpassword", "user")
    
    # 更新密码
    user_service.update_user("testuser", password="newpassword")
    
    # 旧密码无法登录
    user = user_service.authenticate("testuser", "oldpassword")
    assert user is None
    
    # 新密码可以登录
    user = user_service.authenticate("testuser", "newpassword")
    assert user is not None


def test_update_user_role(user_service):
    """测试更新用户角色"""
    user_service.create_user("testuser", "password123", "user")
    
    # 更新角色
    updated_user = user_service.update_user("testuser", role="admin")
    assert updated_user.role == "admin"
    
    # 验证角色已更新
    user = user_service.get_user("testuser")
    assert user.role == "admin"


def test_delete_user(user_service):
    """测试删除用户"""
    user_service.create_user("testuser", "password123", "user")
    
    users = user_service.list_users()
    assert len(users) == 2  # admin + testuser
    
    user_service.delete_user("testuser")
    
    users = user_service.list_users()
    assert len(users) == 1
    assert users[0].username == "admin"


def test_delete_admin_user(user_service):
    """测试不能删除管理员账户"""
    with pytest.raises(ValueError, match="不能删除管理员账户"):
        user_service.delete_user("admin")


def test_create_access_token(user_service):
    """测试创建访问令牌"""
    token = user_service.create_access_token("testuser", "user")
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token(user_service):
    """测试验证令牌"""
    token = user_service.create_access_token("testuser", "user")
    
    payload = user_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["role"] == "user"


def test_verify_invalid_token(user_service):
    """测试验证无效令牌"""
    payload = user_service.verify_token("invalid.token.here")
    assert payload is None


def test_password_hashing(user_service):
    """测试密码哈希"""
    password = "testpassword123"
    hash1 = user_service._hash_password(password)
    hash2 = user_service._hash_password(password)
    
    # 相同密码应该产生相同的哈希
    assert hash1 == hash2
    
    # 哈希不应该等于原始密码
    assert hash1 != password
    
    # 哈希应该是固定长度的十六进制字符串
    assert len(hash1) == 64  # SHA-256 produces 64 hex characters


def test_user_persistence(user_service, temp_data_dir):
    """测试用户数据持久化"""
    # 创建用户
    user_service.create_user("testuser", "password123", "user")
    
    # 创建新的服务实例（模拟重启）
    new_service = UserService()
    new_service.users_file = temp_data_dir / "users.json"
    
    # 验证用户仍然存在
    users = new_service.list_users()
    assert len(users) == 2
    
    usernames = [u.username for u in users]
    assert "admin" in usernames
    assert "testuser" in usernames


def test_get_user(user_service):
    """测试获取用户信息"""
    user_service.create_user("testuser", "password123", "user")
    
    user = user_service.get_user("testuser")
    assert user is not None
    assert user.username == "testuser"
    assert user.role == "user"
    
    # 获取不存在的用户
    user = user_service.get_user("nonexistent")
    assert user is None


def test_user_to_safe_dict(user_service):
    """测试用户安全字典转换"""
    user = user_service.get_user("admin")
    safe_dict = user.to_safe_dict()
    
    # 应该包含这些字段
    assert "username" in safe_dict
    assert "role" in safe_dict
    assert "created_at" in safe_dict
    
    # 不应该包含密码哈希
    assert "password_hash" not in safe_dict


def test_update_admin_username(user_service):
    """测试可以修改 admin 用户名"""
    # 修改 admin 用户名
    updated_user = user_service.update_user("admin", new_username="superadmin")
    assert updated_user.username == "superadmin"
    assert updated_user.role == "admin"
    
    # 验证旧用户名不存在
    old_user = user_service.get_user("admin")
    assert old_user is None
    
    # 验证新用户名存在
    new_user = user_service.get_user("superadmin")
    assert new_user is not None
    assert new_user.username == "superadmin"
    assert new_user.role == "admin"
    
    # 验证可以用新用户名登录
    user = user_service.authenticate("superadmin", "admin123")
    assert user is not None
    assert user.username == "superadmin"


def test_update_username_duplicate(user_service):
    """测试修改用户名为已存在的用户名"""
    user_service.create_user("testuser", "password123", "user")
    
    # 尝试将 admin 用户名改为已存在的 testuser
    with pytest.raises(ValueError, match="已存在"):
        user_service.update_user("admin", new_username="testuser")
