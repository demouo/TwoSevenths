# 二分之七 / TwoSevenths

## 项目简介

一个展示和反思工作生活平衡的互动网页项目。我们都在过着每周要上班5天，只期待2天的周末，生命的长度被缩减到了2/7。

## 功能特性

- **休息日选择**：用户可以选择自己的休息模式（双休、单休、大小周）
- **实时统计**：展示所有用户的选择数据
  - 各选项的数量和占比
  - 选择时间分布图表
- **弹幕互动**：
  - 用户可以发送弹幕吐槽
  - 支持对弹幕点赞
  - 弹幕定时刷新或重播
  - LLM内容审核（计划中）

## 技术栈

### 前端
- HTML5 + CSS3
- 原生 JavaScript
- Chart.js (数据可视化)

### 后端
- Python 3.9+
- FastAPI
- Pydantic (数据验证)
- SQLite (数据持久化)
- Uvicorn (ASGI服务器)

## 项目结构

```
TwoSevenths/
├── README.md              # 项目文档
├── DEPLOY.md             # 部署说明文档
├── requirements.txt       # Python依赖
├── .gitignore            # Git忽略文件
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker编排配置
├── .dockerignore         # Docker构建忽略文件
├── backend/              # 后端服务
│   ├── __init__.py
│   ├── main.py           # FastAPI主程序
│   ├── models.py         # 数据模型
│   ├── database.py       # SQLite数据库操作
│   ├── routes/           # API路由
│   │   ├── __init__.py
│   │   ├── stats.py      # 统计相关API
│   │   └── messages.py   # 弹幕相关API
│   ├── services/         # 业务逻辑
│   │   ├── __init__.py
│   │   └── moderation.py # LLM审核（预留）
│   └── data/             # 数据存储
│       └── twosevenths.db # SQLite数据库
└── frontend/             # 前端静态资源
    ├── index.html        # 主页面
    ├── css/
    │   └── style.css     # 样式文件
    └── js/
        └── app.js        # 前端逻辑
```

## API 接口设计

### 统计相关

#### POST /api/vote
提交用户选择
```json
{
  "option": "double" | "single" | "alternate"
}
```

**响应**
```json
{
  "success": true,
  "message": "投票成功"
}
```

#### GET /api/stats
获取统计数据
```json
{
  "total": 1234,
  "options": {
    "double": { "count": 500, "percentage": 40.5 },
    "single": { "count": 400, "percentage": 32.4 },
    "alternate": { "count": 334, "percentage": 27.1 }
  },
  "timeline": [
    { "timestamp": "2025-12-19T10:00:00Z", "option": "double" }
  ]
}
```

### 弹幕相关

#### POST /api/messages
发送弹幕
```json
{
  "content": "弹幕内容",
  "option": "double" | "single" | "alternate"
}
```

**响应**
```json
{
  "success": true,
  "message_id": "uuid"
}
```

#### GET /api/messages
获取弹幕列表

**查询参数**
- `limit`: 返回数量限制，默认50
- `offset`: 偏移量，默认0

**响应**
```json
{
  "messages": [
    {
      "id": "uuid",
      "content": "内容",
      "option": "double",
      "likes": 10,
      "timestamp": "2025-12-19T10:00:00Z"
    }
  ],
  "total": 1000
}
```

#### POST /api/messages/{id}/like
点赞弹幕

**响应**
```json
{
  "success": true,
  "likes": 11
}
```

## 快速开始

### 方式一：本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 启动后端服务器

```bash
cd backend
python main.py
```

或使用 uvicorn：
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 访问应用

- 网页: http://localhost:8000
- API文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 方式二：Docker部署（推荐）

#### 1. 使用Docker Compose（最简单）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 2. 手动Docker部署

```bash
# 构建镜像
docker build -t twosevenths:latest .

# 运行容器
docker run -d \
  --name twosevenths-app \
  -p 8000:8000 \
  -v $(pwd)/backend/data:/app/backend/data \
  twosevenths:latest
```

更多部署选项和配置请参考 [DEPLOY.md](DEPLOY.md)。

## 开发计划

- [x] 项目文档设计
- [x] 基础项目结构
- [x] 前端页面开发
- [x] 后端API实现
- [x] 数据持久化优化（SQLite）
- [x] Docker部署配置
- [ ] LLM内容审核集成（可选）
- [ ] 生产环境部署

## 特性说明

### 数据持久化

项目使用 SQLite 数据库进行数据存储，具有以下优势：
- 更好的并发性能
- 支持事务和索引
- 数据完整性保障
- 易于备份和迁移

旧的 JSON 数据会在首次启动时自动迁移到 SQLite。

### Docker 部署

提供了完整的 Docker 配置：
- 使用 Python 3.12 slim 镜像，体积小
- 内置健康检查
- 数据卷持久化
- 支持一键部署

详细配置请参考 [DEPLOY.md](DEPLOY.md)。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
