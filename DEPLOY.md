# 部署说明

## 本地开发部署

### 方式一：直接运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
python backend/main.py
```

3. 访问应用：
- 网页: http://localhost:8000
- API文档: http://localhost:8000/docs

### 方式二：使用uvicorn

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker 部署

### 快速启动

使用 Docker Compose 一键部署：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动Docker部署

1. 构建镜像：
```bash
docker build -t twosevenths:latest .
```

2. 运行容器：
```bash
docker run -d \
  --name twosevenths-app \
  -p 8000:8000 \
  -v $(pwd)/backend/data:/app/backend/data \
  twosevenths:latest
```

3. 查看日志：
```bash
docker logs -f twosevenths-app
```

4. 停止容器：
```bash
docker stop twosevenths-app
docker rm twosevenths-app
```

## 生产环境部署

### 使用反向代理（推荐）

推荐使用 Nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 环境变量配置

在生产环境中，建议创建 `.env` 文件配置环境变量：

```bash
# .env
ENVIRONMENT=production
CORS_ORIGINS=https://your-domain.com
```

然后修改 `docker-compose.yml`：

```yaml
services:
  web:
    build: .
    env_file:
      - .env
    ports:
      - "8000:8000"
```

### 数据备份

数据库文件位于 `backend/data/twosevenths.db`，建议定期备份：

```bash
# 备份数据库
cp backend/data/twosevenths.db backup/twosevenths_$(date +%Y%m%d_%H%M%S).db

# 或使用 Docker volume 备份
docker run --rm \
  -v twosevenths_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz /data
```

## 常见问题

### 1. 端口被占用

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:8000"  # 将主机端口改为8080
```

### 2. 数据持久化

Docker部署时，数据会自动持久化到 `backend/data` 目录。确保该目录有正确的权限：

```bash
chmod -R 755 backend/data
```

### 3. 查看应用日志

```bash
# Docker Compose
docker-compose logs -f web

# 单个容器
docker logs -f twosevenths-app
```

### 4. 重启服务

```bash
# Docker Compose
docker-compose restart

# 单个容器
docker restart twosevenths-app
```

## 性能优化

1. **使用多个worker进程**

修改 Dockerfile 中的启动命令：

```dockerfile
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **启用缓存**

在 Nginx 配置中添加缓存：

```nginx
location /static {
    proxy_pass http://localhost:8000;
    proxy_cache_valid 200 1d;
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## 监控和维护

### 健康检查

应用内置了健康检查端点，可以通过以下命令检查：

```bash
curl http://localhost:8000/api/stats
```

### 日志管理

建议配置日志轮转，避免日志文件过大：

```bash
# 使用 logrotate
cat > /etc/logrotate.d/twosevenths <<EOF
/var/log/twosevenths/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
}
EOF
```
