#!/bin/bash

# 用户认证功能测试脚本

BASE_URL="http://localhost:8000/api"

echo "=========================================="
echo "XiaoAI Media 用户认证功能测试"
echo "=========================================="
echo ""

# 测试登录
echo "1. 测试登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "登录响应: $LOGIN_RESPONSE"
echo ""

# 提取 token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败，无法获取 token"
  exit 1
fi

echo "✅ 登录成功，获得 token"
echo ""

# 测试获取当前用户信息
echo "2. 测试获取当前用户信息..."
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

echo "用户信息: $ME_RESPONSE"
echo ""

if echo "$ME_RESPONSE" | grep -q "admin"; then
  echo "✅ 获取用户信息成功"
else
  echo "❌ 获取用户信息失败"
  exit 1
fi
echo ""

# 测试列出所有用户（管理员权限）
echo "3. 测试列出所有用户..."
USERS_RESPONSE=$(curl -s -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN")

echo "用户列表: $USERS_RESPONSE"
echo ""

if echo "$USERS_RESPONSE" | grep -q "admin"; then
  echo "✅ 列出用户成功"
else
  echo "❌ 列出用户失败"
  exit 1
fi
echo ""

# 测试创建用户
echo "4. 测试创建用户..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","role":"user"}')

echo "创建用户响应: $CREATE_RESPONSE"
echo ""

if echo "$CREATE_RESPONSE" | grep -q "testuser"; then
  echo "✅ 创建用户成功"
else
  echo "⚠️  创建用户失败（可能已存在）"
fi
echo ""

# 测试删除用户
echo "5. 测试删除用户..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/users/testuser" \
  -H "Authorization: Bearer $TOKEN")

echo "删除用户响应: $DELETE_RESPONSE"
echo ""

if echo "$DELETE_RESPONSE" | grep -q "已删除"; then
  echo "✅ 删除用户成功"
else
  echo "⚠️  删除用户失败"
fi
echo ""

# 测试无效 token
echo "6. 测试无效 token..."
INVALID_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer invalid_token")

echo "无效 token 响应: $INVALID_RESPONSE"
echo ""

if echo "$INVALID_RESPONSE" | grep -q "401\|未授权\|无效"; then
  echo "✅ 无效 token 正确拒绝"
else
  echo "❌ 无效 token 处理失败"
fi
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
