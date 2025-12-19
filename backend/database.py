"""
数据库管理模块
使用SQLite进行数据持久化
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

# 数据库文件路径
DB_DIR = Path(__file__).parent / "data"
DB_FILE = DB_DIR / "twosevenths.db"


@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """初始化数据库表结构"""
    DB_DIR.mkdir(exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 创建投票记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建弹幕消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                option TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_votes_option
            ON votes(option)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_votes_timestamp
            ON votes(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp
            ON messages(timestamp DESC)
        """)

        conn.commit()


# ==================== 投票相关操作 ====================

def add_vote(option: str, timestamp: str) -> bool:
    """
    添加投票记录

    Args:
        option: 投票选项
        timestamp: 时间戳

    Returns:
        bool: 是否成功
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO votes (option, timestamp) VALUES (?, ?)",
                (option, timestamp)
            )
        return True
    except Exception as e:
        print(f"添加投票失败: {e}")
        return False


def get_vote_stats() -> Dict:
    """
    获取投票统计数据

    Returns:
        dict: 统计数据
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM votes")
        total = cursor.fetchone()["total"]

        # 获取各选项数量
        cursor.execute("""
            SELECT option, COUNT(*) as count
            FROM votes
            GROUP BY option
        """)
        option_counts = {row["option"]: row["count"] for row in cursor.fetchall()}

        # 获取时间线（最近100条）
        cursor.execute("""
            SELECT option, timestamp
            FROM votes
            ORDER BY id DESC
            LIMIT 100
        """)
        timeline = [
            {"option": row["option"], "timestamp": row["timestamp"]}
            for row in cursor.fetchall()
        ]
        timeline.reverse()  # 按时间正序

        return {
            "total": total,
            "option_counts": option_counts,
            "timeline": timeline
        }


# ==================== 弹幕消息相关操作 ====================

def add_message(message_id: str, content: str, option: str, timestamp: str) -> bool:
    """
    添加弹幕消息

    Args:
        message_id: 消息ID
        content: 消息内容
        option: 关联的选项
        timestamp: 时间戳

    Returns:
        bool: 是否成功
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (id, content, option, timestamp) VALUES (?, ?, ?, ?)",
                (message_id, content, option, timestamp)
            )
        return True
    except Exception as e:
        print(f"添加消息失败: {e}")
        return False


def get_messages(limit: int = 50, offset: int = 0) -> tuple[List[Dict], int]:
    """
    获取弹幕消息列表

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        tuple: (消息列表, 总数)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM messages")
        total = cursor.fetchone()["total"]

        # 获取消息列表
        cursor.execute("""
            SELECT id, content, option, likes, timestamp
            FROM messages
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        messages = [dict(row) for row in cursor.fetchall()]

        return messages, total


def like_message(message_id: str) -> Optional[int]:
    """
    给弹幕点赞

    Args:
        message_id: 消息ID

    Returns:
        Optional[int]: 新的点赞数，如果消息不存在返回None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 增加点赞数
            cursor.execute(
                "UPDATE messages SET likes = likes + 1 WHERE id = ?",
                (message_id,)
            )

            if cursor.rowcount == 0:
                return None

            # 获取新的点赞数
            cursor.execute("SELECT likes FROM messages WHERE id = ?", (message_id,))
            result = cursor.fetchone()

            return result["likes"] if result else None
    except Exception as e:
        print(f"点赞失败: {e}")
        return None


def get_message_by_id(message_id: str) -> Optional[Dict]:
    """
    根据ID获取消息

    Args:
        message_id: 消息ID

    Returns:
        Optional[Dict]: 消息数据，如果不存在返回None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, content, option, likes, timestamp FROM messages WHERE id = ?",
            (message_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None


# ==================== 数据迁移工具 ====================

def migrate_from_json():
    """从JSON文件迁移数据到SQLite（如果JSON文件存在）"""
    import json

    stats_file = DB_DIR / "stats.json"
    messages_file = DB_DIR / "messages.json"

    migrated_count = 0

    # 迁移投票数据
    if stats_file.exists():
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                votes = stats_data.get("votes", [])

                for vote in votes:
                    add_vote(vote["option"], vote["timestamp"])
                    migrated_count += 1

                print(f"已迁移 {len(votes)} 条投票记录")
        except Exception as e:
            print(f"迁移投票数据失败: {e}")

    # 迁移弹幕数据
    if messages_file.exists():
        try:
            with open(messages_file, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                messages = messages_data.get("messages", [])

                for msg in messages:
                    add_message(
                        msg["id"],
                        msg["content"],
                        msg["option"],
                        msg["timestamp"]
                    )
                    # 如果有点赞，更新点赞数
                    if msg.get("likes", 0) > 0:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE messages SET likes = ? WHERE id = ?",
                                (msg["likes"], msg["id"])
                            )
                    migrated_count += 1

                print(f"已迁移 {len(messages)} 条弹幕消息")
        except Exception as e:
            print(f"迁移弹幕数据失败: {e}")

    return migrated_count


if __name__ == "__main__":
    # 测试数据库初始化
    print("初始化数据库...")
    init_database()
    print("数据库初始化完成！")

    # 尝试数据迁移
    print("\n检查是否需要迁移数据...")
    migrate_from_json()
    print("数据迁移完成！")
