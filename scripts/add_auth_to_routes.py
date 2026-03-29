#!/usr/bin/env python3
"""批量为API路由添加登录态校验"""

import re
from pathlib import Path

# 需要处理的路由文件
ROUTE_FILES = [
    "backend/src/xiaoai_media/api/routes/music.py",
    "backend/src/xiaoai_media/api/routes/playlist.py",
    "backend/src/xiaoai_media/api/routes/proxy.py",
    "backend/src/xiaoai_media/api/routes/scheduler.py",
    "backend/src/xiaoai_media/api/routes/state.py",
]

def add_auth_to_file(file_path: str):
    """为单个文件添加登录态校验"""
    path = Path(file_path)
    if not path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    content = path.read_text()
    
    # 检查是否已经导入了get_current_user
    if "get_current_user" in content:
        print(f"✓ {file_path} 已经添加了登录态校验")
        return
    
    # 1. 添加get_current_user到导入语句
    import_pattern = r"from xiaoai_media\.api\.dependencies import ([^\n]+)"
    match = re.search(import_pattern, content)
    
    if match:
        imports = match.group(1)
        if "get_current_user" not in imports:
            new_imports = imports.rstrip() + ", get_current_user"
            content = re.sub(import_pattern, f"from xiaoai_media.api.dependencies import {new_imports}", content)
            print(f"  添加导入: get_current_user")
    
    # 2. 为所有路由函数添加current_user参数
    # 匹配函数定义，查找Depends(get_client)
    function_pattern = r"(@router\.(get|post|put|delete|patch)\([^\)]*\)\s*(?:async\s+)?def\s+\w+\([^)]*client:\s*XiaoAiClient\s*=\s*Depends\(get_client\))([^)]*)\):"
    
    def add_auth_param(match):
        before = match.group(1)
        after = match.group(3)
        # 如果已经有current_user参数，不添加
        if "current_user" in before or "current_user" in after:
            return match.group(0)
        # 添加current_user参数
        return f"{before}, current_user: dict = Depends(get_current_user){after}):"
    
    new_content = re.sub(function_pattern, add_auth_param, content, flags=re.MULTILINE | re.DOTALL)
    
    if new_content != content:
        path.write_text(new_content)
        print(f"✓ {file_path} 已添加登录态校验")
    else:
        print(f"⚠ {file_path} 未找到需要修改的函数")

def main():
    print("开始批量添加登录态校验...\n")
    
    for file_path in ROUTE_FILES:
        add_auth_to_file(file_path)
    
    print("\n完成！")

if __name__ == "__main__":
    main()
