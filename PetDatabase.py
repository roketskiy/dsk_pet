import sqlite3

class PetDatabase:
    def __init__(self, db_path='pet_data.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        self._init_tables()

    def _init_tables(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()

        # 用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 会话表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP NULL,
            total_score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        # 聊天记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT CHECK(role IN ('system', 'user', 'assistant')) NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)

        # 游戏得分表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            score_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)

        self.conn.commit()