# 后端服务器部署指南

本项目前端已自动部署到 GitHub Pages，但需要单独部署后端API服务。

## 部署架构

```
前端 (GitHub Pages)
   ↓ API请求
后端 (你的服务器)
   ↓ 数据存储
SQLite 数据库
```

## 前置要求

- Linux服务器（Ubuntu/CentOS/Debian等）
- Python 3.9+
- 域名（可选，推荐用于配置HTTPS）
- 服务器开放端口（如8000或80/443）

## 部署方式

### 方式一：Docker 部署（推荐）

#### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt-get install docker-compose-plugin
```

#### 2. 克隆代码

```bash
git clone https://github.com/demouo/TwoSevenths.git
cd TwoSevenths
```

#### 3. 启动服务

```bash
# 使用 Docker Compose（最简单）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

#### 4. 测试API

```bash
curl http://localhost:8000/api/stats
```

#### 5. 配置反向代理（生产环境）

**使用 Nginx：**

```bash
# 安装 Nginx
sudo apt-get install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/twosevenths
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name api.your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS配置（如果需要）
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/twosevenths /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. 配置HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d api.your-domain.com
```

### 方式二：直接运行（开发/测试）

#### 1. 安装依赖

```bash
# 克隆代码
git clone https://github.com/demouo/TwoSevenths.git
cd TwoSevenths

# 安装Python依赖
pip install -r requirements.txt
```

#### 2. 启动服务

```bash
# 直接运行
python backend/main.py

# 或使用 uvicorn（推荐）
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 生产环境使用多进程
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 3. 使用 systemd 管理（保持后台运行）

创建服务文件：

```bash
sudo nano /etc/systemd/system/twosevenths.service
```

添加以下内容：

```ini
[Unit]
Description=TwoSevenths API Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/TwoSevenths
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable twosevenths
sudo systemctl start twosevenths
sudo systemctl status twosevenths
```

## 配置前端连接后端

部署后端后，需要更新前端配置：

### 1. 修改 `frontend/config.js`

```javascript
const API_CONFIG = {
    baseURL: 'https://api.your-domain.com'  // 替换为你的后端API地址
};
```

### 2. 提交并推送更改

```bash
git add frontend/config.js
git commit -m "Update backend API URL"
git push origin main
```

GitHub Actions 会自动重新部署前端。

## 数据管理

### 数据备份

```bash
# 备份SQLite数据库
cp backend/data/twosevenths.db backup/twosevenths_$(date +%Y%m%d).db

# 使用Docker备份
docker exec twosevenths-app cp /app/backend/data/twosevenths.db /app/backup/
```

### 数据恢复

```bash
# 恢复数据库
cp backup/twosevenths_20250101.db backend/data/twosevenths.db

# 重启服务
docker-compose restart  # Docker方式
# 或
sudo systemctl restart twosevenths  # systemd方式
```

## 监控和维护

### 查看日志

```bash
# Docker方式
docker-compose logs -f

# systemd方式
sudo journalctl -u twosevenths -f
```

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# Docker方式更新
docker-compose down
docker-compose build
docker-compose up -d

# 直接运行方式更新
sudo systemctl restart twosevenths
```

### 健康检查

```bash
# 检查API状态
curl http://localhost:8000/api/stats

# 检查服务状态
sudo systemctl status twosevenths  # systemd
# 或
docker-compose ps  # Docker
```

## 安全建议

1. **配置防火墙**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **限制CORS**

修改 `backend/main.py`：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://demouo.github.io"],  # 只允许GitHub Pages域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **定期更新**
```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade

# 更新Python包
pip install --upgrade -r requirements.txt
```

4. **设置日志轮转**
```bash
sudo nano /etc/logrotate.d/twosevenths
```

添加：
```
/var/log/twosevenths/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
}
```

## 故障排查

### API无法访问

1. 检查服务是否运行：
```bash
docker-compose ps  # Docker
sudo systemctl status twosevenths  # systemd
```

2. 检查端口占用：
```bash
sudo lsof -i :8000
```

3. 查看错误日志：
```bash
docker-compose logs --tail=100  # Docker
sudo journalctl -u twosevenths -n 100  # systemd
```

### CORS错误

确保 `backend/main.py` 的CORS配置包含GitHub Pages域名：
```python
allow_origins=["https://demouo.github.io"]
```

### 数据库锁定

SQLite在高并发时可能出现锁定，建议：
1. 使用多进程 uvicorn
2. 或考虑升级到 PostgreSQL（生产环境）

## 性能优化

1. **使用CDN加速前端资源**
2. **启用Gzip压缩**（Nginx配置）
3. **增加worker进程数**
4. **配置数据库连接池**（如需要）
5. **使用Redis缓存**（可选）

## 需要帮助？

- 查看项目文档：[README.md](README.md)
- 提交Issue：https://github.com/demouo/TwoSevenths/issues
- 部署问题：参考 [DEPLOY.md](DEPLOY.md)
