"""用户管理服务"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import jwt

from xiaoai_media.config import get_data_dir


class User:
    """用户模型"""
    def __init__(self, username: str, password_hash: str, role: str = "user", 
                 created_at: str = None, last_login: str = None, enabled: bool = True):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
        self.enabled = enabled
    
    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "enabled": self.enabled
        }
    
    def to_safe_dict(self) -> dict:
        """返回不包含密码的用户信息"""
        return {
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "enabled": self.enabled
        }


class UserService:
    """用户管理服务"""
    
    SECRET_KEY = "xiaoai-media-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
    
    def __init__(self):
        # 使用 DATA_DIR/.xiaoai_media 目录
        data_dir = get_data_dir()
        self.xiaoai_dir = data_dir / ".xiaoai_media"
        self.xiaoai_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.xiaoai_dir / "users.json"
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """确保用户文件存在，如果不存在则创建默认管理员"""
        if not self.users_file.exists():
            default_admin = User(
                username="admin",
                password_hash=self._hash_password("admin123"),
                role="admin"
            )
            self._save_users([default_admin])
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> list[User]:
        """加载所有用户"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [User(**user_data) for user_data in data]
    
    def _save_users(self, users: list[User]):
        """保存用户列表"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump([user.to_dict() for user in users], f, ensure_ascii=False, indent=2)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        users = self._load_users()
        password_hash = self._hash_password(password)
        
        for i, user in enumerate(users):
            if user.username == username and user.password_hash == password_hash:
                # 检查用户是否被禁用
                if not user.enabled:
                    return None
                
                # 更新最近登录时间
                user.last_login = datetime.now().isoformat()
                users[i] = user
                self._save_users(users)
                return user
        return None
    
    def create_access_token(self, username: str, role: str) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": username,
            "role": role,
            "exp": expire
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user(self, username: str) -> Optional[User]:
        """获取用户信息"""
        users = self._load_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    def list_users(self) -> list[User]:
        """列出所有用户"""
        return self._load_users()
    
    def create_user(self, username: str, password: str, role: str = "user") -> User:
        """创建新用户"""
        users = self._load_users()
        
        # 检查用户名是否已存在
        if any(u.username == username for u in users):
            raise ValueError(f"用户名 {username} 已存在")
        
        new_user = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role
        )
        users.append(new_user)
        self._save_users(users)
        return new_user
    
    def update_user(self, username: str, password: Optional[str] = None, role: Optional[str] = None, 
                    new_username: Optional[str] = None, enabled: Optional[bool] = None) -> User:
        """更新用户信息"""
        users = self._load_users()
        
        # 如果要修改用户名，先检查新用户名是否已存在
        if new_username and new_username != username:
            if any(u.username == new_username for u in users):
                raise ValueError(f"用户名 {new_username} 已存在")
        
        for user in users:
            if user.username == username:
                # 检查是否尝试禁用管理员用户
                if enabled is not None and not enabled and user.role == "admin":
                    raise ValueError("不能禁用管理员账户")
                
                if password:
                    user.password_hash = self._hash_password(password)
                if role:
                    user.role = role
                if new_username:
                    user.username = new_username
                if enabled is not None:
                    user.enabled = enabled
                self._save_users(users)
                return user
        
        raise ValueError(f"用户 {username} 不存在")
    
    def delete_user(self, username: str):
        """删除用户"""
        if username == "admin":
            raise ValueError("不能删除管理员账户")
        
        users = self._load_users()
        users = [u for u in users if u.username != username]
        self._save_users(users)
    
    def enable_user(self, username: str) -> User:
        """启用用户"""
        return self.update_user(username, enabled=True)
    
    def disable_user(self, username: str) -> User:
        """禁用用户"""
        if username == "admin":
            raise ValueError("不能禁用管理员账户")
        return self.update_user(username, enabled=False)


# 全局用户服务实例
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """获取用户服务实例"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
