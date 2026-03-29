"""用户认证路由"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

from xiaoai_media.services.user_service import get_user_service, User


router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str


class UserInfo(BaseModel):
    username: str
    role: str
    created_at: str
    last_login: Optional[str] = None
    enabled: bool = True


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    new_username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    enabled: Optional[bool] = None


def get_current_user(authorization: str = Header(None)) -> dict:
    """从请求头获取当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    
    token = authorization.replace("Bearer ", "")
    user_service = get_user_service()
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    return payload


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """要求管理员权限"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """用户登录"""
    user_service = get_user_service()
    user = user_service.authenticate(req.username, req.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误或账户已被禁用")
    
    token = user_service.create_access_token(user.username, user.role)
    
    return LoginResponse(
        token=token,
        username=user.username,
        role=user.role
    )


@router.get("/auth/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    user_service = get_user_service()
    user = user_service.get_user(current_user["sub"])
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserInfo(**user.to_safe_dict())


@router.get("/users", response_model=list[UserInfo])
async def list_users(admin: dict = Depends(require_admin)):
    """列出所有用户（管理员）"""
    user_service = get_user_service()
    users = user_service.list_users()
    return [UserInfo(**user.to_safe_dict()) for user in users]


@router.post("/users", response_model=UserInfo)
async def create_user(req: CreateUserRequest, admin: dict = Depends(require_admin)):
    """创建新用户（管理员）"""
    user_service = get_user_service()
    
    try:
        user = user_service.create_user(req.username, req.password, req.role)
        return UserInfo(**user.to_safe_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{username}", response_model=UserInfo)
async def update_user(username: str, req: UpdateUserRequest, current_user: dict = Depends(get_current_user)):
    """更新用户信息
    
    - 管理员可以更新任何用户
    - 普通用户只能更新自己的密码
    - admin 用户可以修改自己的用户名和密码
    """
    user_service = get_user_service()
    
    # 检查权限
    is_admin = current_user.get("role") == "admin"
    is_self = current_user.get("sub") == username
    
    # 如果不是管理员，只能修改自己的信息
    if not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="只能修改自己的信息")
    
    # 如果不是管理员，不能修改角色
    if not is_admin and req.role is not None:
        raise HTTPException(status_code=403, detail="无权修改用户角色")
    
    # 如果不是管理员，不能修改用户名
    if not is_admin and req.new_username is not None:
        raise HTTPException(status_code=403, detail="无权修改用户名")
    
    # 如果不是管理员，不能修改启用状态
    if not is_admin and req.enabled is not None:
        raise HTTPException(status_code=403, detail="无权修改用户启用状态")
    
    try:
        user = user_service.update_user(username, req.password, req.role, req.new_username, req.enabled)
        return UserInfo(**user.to_safe_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{username}")
async def delete_user(username: str, admin: dict = Depends(require_admin)):
    """删除用户（管理员）"""
    user_service = get_user_service()
    
    try:
        user_service.delete_user(username)
        return {"message": f"用户 {username} 已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{username}/enable", response_model=UserInfo)
async def enable_user(username: str, admin: dict = Depends(require_admin)):
    """启用用户（管理员）"""
    user_service = get_user_service()
    
    try:
        user = user_service.enable_user(username)
        return UserInfo(**user.to_safe_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users/{username}/disable", response_model=UserInfo)
async def disable_user(username: str, admin: dict = Depends(require_admin)):
    """禁用用户（管理员）"""
    user_service = get_user_service()
    
    try:
        user = user_service.disable_user(username)
        return UserInfo(**user.to_safe_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
