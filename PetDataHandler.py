import sqlite3
import uuid
from PetDatabase import PetDatabase

class PetDataHandler:
    def __init__(self):
        self.db = PetDatabase()
        self.current_session = None
        self.user_id = self._get_or_create_user()  # 初始化时获取或创建用户
        self.message_counter = 0
        self.conn = self.db.conn

    def _get_or_create_user(self):
        """获取或创建唯一用户"""
        cursor = self.db.conn.cursor()

        # 尝试获取现有用户
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user = cursor.fetchone()

        if user:
            return user[0]
        else:
            # 创建新用户
            user_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            self.db.conn.commit()
            return user_id

    def start_session(self):
        """开始新会话"""
        try:
            session_id = str(uuid.uuid4())
            cursor = self.db.conn.cursor()

            cursor.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
                (session_id, self.user_id)
            )

            self.db.conn.commit()
            self.current_session = session_id
            self.message_counter = 0
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
                "UPDATE sessions SET end_time=CURRENT_TIMESTAMP WHERE session_id=?",
                (self.current_session,)
            )
            self.db.conn.commit()
            self.current_session = None

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法结束会话: {str(e)}")

    def log_chat_message(self, role, content):
        """记录聊天消息（带时间戳和顺序）"""
        if not self.current_session:
            return

        try:
            self.message_counter += 1
            cursor = self.db.conn.cursor()

            cursor.execute(
                """INSERT INTO chat_logs 
                (session_id, message_index, role, content) 
                VALUES (?, ?, ?, ?)""",
                (self.current_session, self.message_counter, role, content)
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

    def get_chat_history(self, session_id=None):
        """获取指定会话的完整聊天记录（按时间顺序）"""
        session_id = session_id or self.current_session
        if not session_id:
            return []

        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT role, content, timestamp 
            FROM chat_logs 
            WHERE session_id = ? 
            ORDER BY message_index
        """, (session_id,))
        return cursor.fetchall()

    def get_user_stats(self):
        """获取用户统计数据"""
        cursor = self.db.conn.cursor()

        # 总得分和会话次数
        cursor.execute("""
            SELECT 
                COUNT(*) as session_count,
                SUM(total_score) as total_score,
                SUM(duration) as total_duration
            FROM sessions 
            WHERE user_id = ?
        """, (self.user_id,))

        stats = cursor.fetchone()

        return {
            'user_id': self.user_id,
            'session_count': stats[0] or 0,
            'total_score': stats[1] or 0,
            'total_duration': stats[2] or 0  # 总时长(秒)
        }