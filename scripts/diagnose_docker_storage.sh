#!/bin/bash
# Docker 存储诊断脚本

echo "=== Docker 存储诊断 ==="
echo ""

# 检查容器是否运行
echo "1. 检查容器状态..."
docker ps -a | grep xiaoai-media
echo ""

# 检查宿主机目录
echo "2. 检查宿主机数据目录..."
ls -la ./data/ 2>/dev/null || echo "目录不存在或无权限访问"
echo ""

# 检查容器内目录
echo "3. 检查容器内数据目录..."
docker exec xiaoai-media ls -la /data/ 2>/dev/null || echo "无法访问容器或目录"
echo ""

# 检查容器内权限
echo "4. 检查容器内用户和权限..."
docker exec xiaoai-media id
docker exec xiaoai-media stat /data 2>/dev/null || echo "无法获取目录状态"
echo ""

# 测试写入权限
echo "5. 测试容器内写入权限..."
docker exec xiaoai-media touch /data/.test_write 2>/dev/null && \
  docker exec xiaoai-media rm /data/.test_write && \
  echo "✓ 写入权限正常" || \
  echo "✗ 写入权限失败"
echo ""

# 查看最近的日志
echo "6. 查看最近的容器日志..."
docker logs xiaoai-media --tail 50
echo ""

echo "=== 诊断完成 ==="
