from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.routes import stats, messages
from backend.database import init_database, migrate_from_json

# 创建FastAPI应用
app = FastAPI(
    title="七分之二 / TwoSevenths",
    description="工作生活平衡互动展示项目",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://demouo.github.io",      # GitHub Pages部署域名
        "http://localhost:8000",          # 本地开发
        "http://127.0.0.1:8000",          # 本地开发
        "http://47.121.222.197:8000",     # 后端服务器自身
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(stats.router, prefix="/api", tags=["统计"])
app.include_router(messages.router, prefix="/api", tags=["弹幕"])

# 挂载静态文件
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("初始化数据库...")
    init_database()
    print("数据库初始化完成！")

    # 尝试从JSON文件迁移数据（如果存在）
    print("检查是否需要迁移数据...")
    migrated = migrate_from_json()
    if migrated > 0:
        print(f"已迁移 {migrated} 条数据记录")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
