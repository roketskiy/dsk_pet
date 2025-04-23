import sqlite3
import uuid
from PetDatabase import PetDatabase


class PetDataHandler:
    def __init__(self):
        self.db = PetDatabase()
        self.current_session = None
        self.conn = self.db.conn

    def start_session(self, username="default"):
        """开始新会话"""
        try:
            cursor = self.db.conn.cursor()

            # 检查用户是否存在，不存在则创建
            cursor.execute("SELECT user_id FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if not user:
                cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
                user_id = cursor.lastrowid
            else:
                user_id = user[0]

            # 创建新会话
            session_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
                (session_id, user_id)
            )

            self.db.conn.commit()
            self.current_session = session_id
            return session_id

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法开始会话: {str(e)}")

    def end_session(self):
        """结束当前会话"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE sessions SET end_time=datetime('now', 'localtime') WHERE session_id=?",
                (self.current_session,)
            )
            self.db.conn.commit()
            self.current_session = None

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法结束会话: {str(e)}")

    def log_chat_message(self, role, content):
        """记录聊天消息"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """INSERT INTO chat_logs 
                (session_id, role, content) 
                VALUES (?, ?, ?)""",
                (self.current_session, role, content)
            )
            self.db.conn.commit()

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法记录聊天消息: {str(e)}")

    def log_game_score(self, points):
        """记录游戏得分"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()

            # 记录单次得分
            cursor.execute(
                "INSERT INTO game_scores (session_id, points) VALUES (?, ?)",
                (self.current_session, points)
            )

            # 更新会话总得分
            cursor.execute(
                "UPDATE sessions SET total_score=total_score+? WHERE session_id=?",
                (points, self.current_session)
            )

            self.db.conn.commit()

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法记录游戏得分: {str(e)}")

    def __del__(self):
        self.conn.close()

    def get_chat_history(self, session_id):
        """获取指定会话的聊天记录"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT role, content, timestamp 
            FROM chat_logs 
            WHERE session_id = ? 
            ORDER BY timestamp""",
            (session_id,)
        )
        return cursor.fetchall()

    def get_user_stats(self, username):
        """获取用户统计数据"""
        cursor = self.conn.cursor()

        # 总得分
        cursor.execute(
            """SELECT SUM(total_score) 
            FROM sessions 
            WHERE user_id = (
                SELECT user_id FROM users WHERE username = ?
            )""",
            (username,)
        )
        total_score = cursor.fetchone()[0] or 0

        # 会话次数
        cursor.execute(
            """SELECT COUNT(*) 
            FROM sessions 
            WHERE user_id = (
                SELECT user_id FROM users WHERE username = ?
            )""",
            (username,)
        )
        session_count = cursor.fetchone()[0]

        return {
            'username': username,
            'total_score': total_score,
            'session_count': session_count
        }
