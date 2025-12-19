# GitHub Pages 部署设置指南

代码已成功推送到 GitHub！现在需要在 GitHub 仓库设置中启用 GitHub Pages。

## 步骤 1: 启用 GitHub Pages

1. 打开你的 GitHub 仓库：https://github.com/demouo/TwoSevenths

2. 点击仓库顶部的 **Settings**（设置）

3. 在左侧菜单中找到 **Pages**

4. 在 "Build and deployment" 部分：
   - **Source**: 选择 `GitHub Actions`

5. 保存设置

## 步骤 2: 触发部署

方式一：等待自动部署
- GitHub Actions 会在你推送代码后自动运行
- 访问仓库的 **Actions** 标签页查看部署进度

方式二：手动触发
1. 进入仓库的 **Actions** 标签页
2. 点击左侧的 "Deploy to GitHub Pages"
3. 点击右侧的 "Run workflow" 按钮
4. 点击绿色的 "Run workflow" 确认

## 步骤 3: 查看部署状态

1. 在 **Actions** 标签页可以看到工作流运行状态
2. 等待部署完成（通常需要 1-2 分钟）
3. 部署成功后，访问：https://demouo.github.io/TwoSevenths

## 步骤 4: 部署后端 API

前端部署完成后，你需要部署后端服务。请参考：

📖 **[后端部署完整指南](BACKEND_DEPLOY.md)**

### 快速开始（Docker）

在你的服务器上：

```bash
# 克隆代码
git clone https://github.com/demouo/TwoSevenths.git
cd TwoSevenths

# 启动服务
docker-compose up -d

# 配置 Nginx 反向代理（建议）
# 参考 BACKEND_DEPLOY.md 中的详细说明
```

## 步骤 5: 连接前后端

后端部署完成后，更新前端配置：

1. 编辑 `frontend/config.js`：
```javascript
const API_CONFIG = {
    baseURL: 'https://api.your-domain.com'  // 替换为你的后端API地址
};
```

2. 提交并推送：
```bash
git add frontend/config.js
git commit -m "Update backend API URL"
git push origin main
```

3. GitHub Actions 会自动重新部署前端

## 常见问题

### 1. GitHub Pages 页面显示 404

**原因**: GitHub Pages 可能还未启用或部署未完成

**解决方法**:
- 确认已在 Settings > Pages 中启用 GitHub Actions
- 检查 Actions 标签页的部署状态
- 等待几分钟让 DNS 生效

### 2. 页面加载但功能不工作

**原因**: 后端 API 未部署或配置错误

**解决方法**:
- 检查浏览器控制台是否有 API 请求错误
- 确认 `frontend/config.js` 中的 API 地址正确
- 确保后端服务正在运行并可访问

### 3. CORS 错误

**原因**: 后端未允许来自 GitHub Pages 的跨域请求

**解决方法**:
编辑 `backend/main.py`，添加 GitHub Pages 域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://demouo.github.io",
        "http://localhost:8000"  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. GitHub Actions 工作流失败

**解决方法**:
1. 点击失败的工作流查看详细错误
2. 确认 `.github/workflows/deploy.yml` 配置正确
3. 检查是否有权限问题（Settings > Actions > General > Workflow permissions）

## 验证部署

### 检查前端
访问：https://demouo.github.io/TwoSevenths

### 检查后端
```bash
curl https://your-backend-api.com/api/stats
```

应该返回 JSON 格式的统计数据。

## 下一步

1. ✅ 前端已自动部署到 GitHub Pages
2. ⏳ 部署后端到你的服务器（参考 BACKEND_DEPLOY.md）
3. ⏳ 更新 frontend/config.js 连接后端
4. ⏳ 配置 HTTPS 和域名（可选）
5. ⏳ 设置监控和备份

## 需要帮助？

- 查看部署日志：https://github.com/demouo/TwoSevenths/actions
- 后端部署指南：[BACKEND_DEPLOY.md](BACKEND_DEPLOY.md)
- 提交问题：https://github.com/demouo/TwoSevenths/issues

---

**部署架构**

```
用户浏览器
    ↓
GitHub Pages (前端)
    ↓ API 请求
你的服务器 (后端)
    ↓
SQLite 数据库
```
