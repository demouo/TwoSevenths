# 🔍 混合内容问题诊断与解决

## 问题确认

你遇到的是**混合内容（Mixed Content）**问题：

```
GitHub Pages (HTTPS)  →  ❌  →  后端 API (HTTP)
https://demouo.github.io     http://47.121.222.197:8000
```

现代浏览器为了安全，会阻止HTTPS页面访问HTTP资源。

## 快速验证

请打开浏览器开发者工具（F12）查看：

1. **Console 标签**：应该会看到类似错误：
   ```
   Mixed Content: The page at 'https://demouo.github.io/TwoSevenths'
   was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint
   'http://47.121.222.197:8000/api/stats'. This request has been blocked;
   the content must be served over HTTPS.
   ```

2. **Network 标签**：API请求显示为红色或被取消（Cancelled）

## 解决方案

### 方案A：临时解决（仅用于测试，不推荐生产环境）

**Chrome浏览器：**

1. 点击地址栏右侧的盾牌图标 🛡️
2. 点击"加载不安全的脚本"或"允许不安全内容"
3. 刷新页面

**或者直接访问后端URL测试：**
- 直接访问：http://47.121.222.197:8000
- 这样前后端都是HTTP，不会有混合内容问题

### 方案B：永久解决 - 为后端配置HTTPS（推荐）

有两个选择：

#### 选项1：使用Nginx + Let's Encrypt（推荐，免费）

**前提条件：**
- 需要一个域名（如：api.twosevenths.com）
- 将域名A记录指向：47.121.222.197

**部署步骤：**

```bash
# 1. 在服务器上安装Nginx和Certbot
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx -y

# 2. 创建Nginx配置
sudo nano /etc/nginx/sites-available/twosevenths
```

添加配置：
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
    }
}
```

```bash
# 3. 启用配置
sudo ln -s /etc/nginx/sites-available/twosevenths /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. 获取SSL证书（自动配置HTTPS）
sudo certbot --nginx -d api.your-domain.com

# 5. 测试HTTPS访问
curl https://api.your-domain.com/api/stats
```

然后更新前端配置：
```javascript
// frontend/config.js
baseURL: 'https://api.your-domain.com'  // 使用HTTPS域名
```

#### 选项2：使用Cloudflare Tunnel（无需域名，免费）

Cloudflare Tunnel可以为你的HTTP服务自动提供HTTPS访问：

```bash
# 1. 下载cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# 2. 登录Cloudflare
cloudflared tunnel login

# 3. 创建tunnel
cloudflared tunnel create twosevenths

# 4. 配置tunnel
cat > ~/.cloudflared/config.yml <<EOF
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: twosevenths.your-domain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# 5. 运行tunnel
cloudflared tunnel run twosevenths
```

#### 选项3：使用反向代理服务（最简单）

使用免费的HTTPS反向代理服务（如 ngrok）：

```bash
# 1. 安装ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# 2. 注册并获取authtoken: https://ngrok.com/

# 3. 设置authtoken
ngrok config add-authtoken <your-token>

# 4. 启动ngrok（会获得一个HTTPS URL）
ngrok http 8000
```

ngrok会提供一个HTTPS URL，如：`https://xxxx.ngrok.io`

然后更新 `frontend/config.js`：
```javascript
baseURL: 'https://xxxx.ngrok.io'
```

### 方案C：修改为本地测试（仅用于演示）

如果只是临时演示，可以本地运行完整版本：

```bash
# 克隆仓库
git clone https://github.com/demouo/TwoSevenths.git
cd TwoSevenths

# 启动后端
docker-compose up -d

# 访问
open http://localhost:8000
```

这样前后端都在同一域名下，没有跨域问题。

## 推荐方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **浏览器允许不安全内容** | 最简单 | 不安全，生产环境不可用 | 仅测试 |
| **Nginx + Let's Encrypt** | 免费、安全、完全控制 | 需要域名 | 生产环境推荐 |
| **Cloudflare Tunnel** | 免费、无需域名 | 依赖第三方服务 | 快速部署 |
| **ngrok** | 最快速、无需配置 | 免费版URL会变化 | 演示/测试 |

## 我的建议

**短期（今天就能用）：**
1. 使用 ngrok 快速获得HTTPS链接（5分钟搞定）
2. 或者直接访问 http://47.121.222.197:8000（绕过GitHub Pages）

**长期（生产环境）：**
1. 注册一个域名（如 twosevenths.com）
2. 配置 Nginx + Let's Encrypt（免费SSL）
3. 将前端访问指向 `https://api.twosevenths.com`

## 下一步操作

### 快速测试（5分钟）

```bash
# 在你的服务器上执行
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# 注册ngrok账号并获取token: https://dashboard.ngrok.com/signup
# 然后执行：
ngrok config add-authtoken <your-token>
ngrok http 8000
```

运行后你会得到一个HTTPS URL，复制这个URL，然后：

```bash
# 在本地执行
cd TwoSevenths
# 编辑 frontend/config.js，将URL替换为ngrok提供的HTTPS URL
git add frontend/config.js
git commit -m "Update to HTTPS backend URL"
git push origin main
```

### 验证

1. 等待GitHub Actions部署完成（1-2分钟）
2. 访问：https://demouo.github.io/TwoSevenths
3. 按F12查看Console，应该没有错误
4. 应该能看到正确的统计数据（28条投票）

---

**需要我帮你配置哪个方案？**

如果你有域名，我推荐方案B（Nginx + Let's Encrypt）。
如果想快速测试，我推荐方案C（ngrok）。
